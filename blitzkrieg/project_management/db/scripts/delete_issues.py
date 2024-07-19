import os
from blitzkrieg.file_management.DirectoryManager import DirectoryManager
from blitzkrieg.file_manager import FileManager
from blitzkrieg.file_management.MarkdownManager import MarkdownManager
from blitzkrieg.issue_management.IssueManager import IssueManager
from blitzkrieg.project_management.base_project_management.ProjectManager import ProjectManager
from blitzkrieg.project_management.db.DBManager import DatabaseManager
from blitzkrieg.project_management.db.connection import get_db_engine, get_db_session
from blitzkrieg.project_management.db.services.issues_service import IssueService
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface


engine = get_db_engine()
db_manager = DatabaseManager(engine)
console_interface = ConsoleInterface()
project_manager = ProjectManager()
file_manager = FileManager()
directory_manager = DirectoryManager(file_manager)
markdown_manager = MarkdownManager(file_manager)
issue_manager = IssueManager(db_manager, file_manager, console_interface, markdown_manager)

def delete_issues_from_docs():
    project_root = project_manager.find_project_root()
    issues_dir = os.path.join(project_root, '.docs', 'issues')
    issue_markdown_files = file_manager.list_files_with_suffix(issues_dir, '.md')
    table = console_interface.configure_table()
    for file in issue_markdown_files:
        try:
            file_path = os.path.join(issues_dir, file)
            file_manager.delete_file(file_path)
            table.add_row(file, "Deleted", "[red]Markdown File Deleted[/red]")
        except Exception as e:
            console_interface.error_manager.display_error(f"Error deleting file {file}: {e}", exception=e)
            table.add_row(file, "Error", "[red]Failed[/red]")

def delete_issues_from_db():
    with get_db_session() as session:
        issues_from_db = IssueService().get_all_issues(session)
        table = console_interface.configure_table()
        for issue in issues_from_db:
            try:
                IssueService().delete_issue(session, issue.id)
                table.add_row(str(issue.id), "Deleted", "[red]Issue Deleted[/red]")
            except Exception as e:
                console_interface.error_manager.display_error(f"Error deleting issue {issue.id}: {e}", exception=e)
                table.add_row(str(issue.id), "Error", "[red]Failed[/red]")

def main():
    delete_issues_from_docs()
    delete_issues_from_db()

if __name__ == '__main__':
    main()
