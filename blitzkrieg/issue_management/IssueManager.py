import uuid
from datetime import datetime
from blitzkrieg.error_handling.ErrorManager import ErrorManager
from blitzkrieg.project_management.db.connection import get_db_session
from blitzkrieg.project_management.db.services.issues_service import IssueService
from blitzkrieg.project_management.db.crud.issue_crud import IssueCRUD
from blitzkrieg.project_management.db.services.project_service import ProjectService
import os
from rich import print as rprint

class IssueManager:
    def __init__(self, database_manager, file_manager, console_interface, markdown_manager):
        self.database_manager = database_manager
        self.file_manager = file_manager
        self.console_interface = console_interface
        self.markdown_manager = markdown_manager
        self.error_manager = ErrorManager(self.console_interface)

    def create_test_issue_in_db(self):
        issue_dict = self.generate_issue_metadata(None, "Test Issue", "This is a test issue.", "Blitzkrieg")
        with get_db_session() as session:
            self.save_issue_to_database(issue_dict, "Blitzkrieg", session)

    def sync_issue_docs_to_db(self, file_path, project_name, session, table):
        try:
            issue_id, title, content = self.markdown_manager.extract_file_details(file_path)
            action, status = "", ""

            if action == "" and status == "":
                if not issue_id:
                    action, status = self.manage_new_issue_creation(file_path, issue_id, title, content, project_name, session)
                elif issue_id:
                    issue_from_db = self.get_issue_from_db(issue_id, session)
                    action, status = self.update_issue_if_modified(file_path, issue_id, title, content, issue_from_db, session)

            table.add_row(file_path, action, status)
        except Exception as e:
            self.error_manager.display_error(f"Error processing file {file_path}: {e}", exception=e)
            table.add_row(file_path, "Error", "[red]Failed[/red]")

    def sync_db_issues_to_docs(self, issues_dir, project_name, session, table):
        issues_from_db = IssueService().get_all_issues(session)
        issue_markdown_files = self.file_manager.list_files_with_suffix(issues_dir, '.md')
        issue_markdown_files_issue_ids = [self.markdown_manager.extract_file_details(os.path.join(issues_dir, f))[0] for f in issue_markdown_files]

        for issue in issues_from_db:
             if str(issue.id) not in issue_markdown_files_issue_ids:
                file_name = f"{self.convert_title_to_snakecase(issue.title)}_{str(issue.id)}.md"
                file_path = os.path.join(issues_dir, file_name)
                self.file_manager.write_file(file_path, f'# {issue.title}\n\n{issue.description}')
                table.add_row(file_name, "Synced", "[green]Markdown File Created[/green]")


    def verify_uuid_format(self, uuid_to_test, version=4):
        try:
            uuid_obj = uuid.UUID(uuid_to_test, version=version)
            return True
        except ValueError:
            return False


    def get_issue_from_db(self, issue_id, session):
        issue = IssueCRUD().get_issue_by_id(session, issue_id)
        return issue

    def manage_new_issue_creation(self, file_path, issue_id, title, content, project_name, session):
        try:
            issue = self.generate_issue_metadata(issue_id, title, content, project_name)
            created_issue = self.save_issue_to_database(issue, project_name, session)
            if created_issue:
                self.file_manager.append_uuid_to_file(file_path, issue['id'])
                self.error_manager.display_success(f"New issue created: ID {issue['id']}", emoji=':check_mark_button:')
                return "Created", f"[green]New Issue Created: {issue['id']}[/green]"
            else:
                raise Exception("Failed to create new issue in database.")
        except Exception as e:
            self.error_manager.display_error(f"Error creating new issue: {e}", exception=e)
            return "Error", "[red]Error Creating Issue[/red]"

    def generate_issue_metadata(self, issue_id, title, content, project_name):
        shorthand_tag = ''.join(ch for ch in project_name if ch not in 'aeiou').lower()[:4]
        branch_name = f'{shorthand_tag}-{title[1:].replace(" ", "-").lower() if title.startswith("#") else title.replace(" ", "-").lower()}'

        # if not issue_id, generate a uuid:
        if not issue_id:
            issue_id = uuid.uuid4()
        return {'id': issue_id, 'title': title.replace('#', '').strip(), 'branch_name': branch_name, 'content': content}

    def generate_branch_name(self, title, project_name):
        shorthand_tag = ''.join(ch for ch in project_name if ch not in 'aeiou').lower()[:4]
        branch_name = f'{shorthand_tag}{title[1:].replace(" ", "-").lower() if title.startswith("#") else title.replace(" ", "-").lower()}'.replace(":", "")
        return branch_name
    def save_issue_to_database(self, issue, project_name, session):
        index = IssueService().get_next_index(session)
        project = ProjectService().get_project_by_name(session, project_name)
        return IssueService().create_issue(
            session=session,
            id=issue['id'],
            title=issue['title'],
            index=index,
            branch_name=issue['branch_name'],
            description=issue['content'],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            project_id=project.id
        )

    def update_issue_if_modified(self, file_path, issue_id, title, content, existing_issue, session):
        title_changed = existing_issue.title != title
        content_changed = existing_issue.description != content
        if title_changed or content_changed:
            existing_issue.title = title if title_changed else existing_issue.title
            existing_issue.description = content if content_changed else existing_issue.description
            existing_issue.updated_at = datetime.now()
            session.commit()
            return "Updated", "[orange]Updated in DB & Markdown[/orange]"
        return "Unchanged", "[blue]No Changes[/blue]"


    def convert_title_to_snakecase(self, title):
        snake_case_title = title.replace('-', ' ').replace('#', '').replace(' ', '_').replace(":", "").lower()
        return snake_case_title.lstrip('_')

    def rewrite_markdown_file(issue, file_path):
        with open(file_path, 'w') as file:
            file.write(f'{issue.id}\n')
            file.write(f'{issue.title}\n\n')
            file.write(issue.description)

    def check_uuid_or_new_issue(self, uuid_to_test, session):
        if not uuid_to_test or not self.markdown_manager.verify_uuid_format(uuid_to_test):
            return False, True  # Invalid UUID, but might be a new issue
        exists, _ = self.check_issue_presence_in_database(uuid_to_test, session)
        return exists, False  # Valid UUID and issue exists

    def generate_markdown_from_db_entry(self, issue, issues_dir):
        snakecase_title = self.convert_title_to_snakecase(issue.title)
        file_name = f"{snakecase_title}.md"
        file_path = os.path.join(issues_dir, file_name)
        with open(file_path, 'w') as file:
            file.write(f'{issue.id}\n')
            file.write(f'{issue.title}\n\n')
            file.write(issue.description)
        rprint(f"[green]Markdown file created for issue {issue.id} ({file_name})[/green]")
