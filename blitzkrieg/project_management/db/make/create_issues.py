import os
import uuid
from contextlib import contextmanager
from blitzkrieg.project_management.db.connection import get_db_session
from blitzkrieg.project_management.db.services.issues_service import IssueService
from datetime import datetime
from blitzkrieg.project_management.db.services.project_service import ProjectService
from rich.console import Console
from rich.progress import track
from rich import print as rprint
from rich.traceback import install
from rich.table import Table
from halo import Halo

# Install rich traceback for enhanced error reporting
install()

console = Console()

@contextmanager
def change_directory(path):
    """Context manager for changing the current working directory."""
    original_path = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(original_path)

def check_directory_exists(directory, error_message):
    if not os.path.isdir(directory):
        rprint(f'[bold red]Error:[/bold red] {error_message}')
        raise FileNotFoundError(error_message)

def get_files(directory, suffix):
    return [file for file in os.listdir(directory) if file.endswith(suffix)]

def create_shorthand_tag(project_name):
    return ''.join(ch for ch in project_name if ch not in 'aeiou').lower()[:4]

def parse_file_id_and_content(file_path):
    """Parse the file to extract ID, title, and content."""
    with open(file_path, 'r') as f:
        id_line = f.readline().strip()  # Assuming the first line is the ID
        title = f.readline().strip()
        content = ''.join(f.readlines()).strip()
    return id_line, title, content

def process_issue_title(issue_title):
    return issue_title[1:].replace(' ', '-').lower() if issue_title.startswith('#') else issue_title.replace(' ', '-').lower()

def create_issue_dict(issue_id, title, content, project_name):
    shorthand_tag = create_shorthand_tag(project_name)
    branch_name = f'{shorthand_tag}{process_issue_title(title)}'
    return {'id': issue_id, 'title': title.replace('#', '').strip(), 'branch_name': branch_name, 'content': content}

def issue_exists_in_db(issue_id, session):
    """Check if an issue with given ID exists in the database."""
    return IssueService().get_issues(session, issue_id) is not None

def get_project_root():
    return os.path.abspath(os.path.join(os.getcwd(), '../../../..'))

def get_markdown_files(parent_dir):
    issues_dir = os.path.join(parent_dir, '.docs', 'issues')
    check_directory_exists(issues_dir, 'issues directory not found in .docs.')
    files = get_files(issues_dir, '.md')
    if not files:
        raise FileNotFoundError("No .md files found in issues directory.")
    return files, issues_dir

def store_issue_in_db(issue, project_name, session):
    index = IssueService().get_next_index(session)
    project = ProjectService().get_project_by_name(session, project_name)
    IssueService().create_issue(
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

def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test

def add_uuid_to_file(file_path, uuid_str):
    with open(file_path, 'r+') as file:
        content = file.read()
        file.seek(0, 0)
        file.write(f'{uuid_str}\n{content}')

def parse_file_id_and_content(file_path):
    with open(file_path, 'r') as f:
        first_line = f.readline().strip()
        if is_valid_uuid(first_line):
            title = f.readline().strip()
            content = ''.join(f.readlines()).strip()
            return first_line, title, content
        else:
            # Move back to the start as it's not a UUID
            f.seek(0)
            content = f.read().strip()
            return None, None, content

def process_issues(files, issues_dir, project_name):
    table = Table(title="Issue Processing Status", show_header=True, header_style="bold magenta")
    table.add_column("File", style="dim")
    table.add_column("Action", justify="right")
    table.add_column("Status", justify="right")

    with get_db_session() as session:
        for file in track(files, description="[green]Processing issues..."):
            file_path = os.path.join(issues_dir, file)
            issue_id, title, content = parse_file_id_and_content(file_path)
            action = "Checked"
            status = "[blue]Unchanged[/blue]"

            if issue_id is None or not is_valid_uuid(issue_id):
                issue_id = str(uuid.uuid4())
                add_uuid_to_file(file_path, issue_id)
                title = "New Issue"  # Default title, change as needed
                action = "Added UUID"
                status = "[yellow]Updated[/yellow]"

            if not issue_exists_in_db(issue_id, session):
                issue = create_issue_dict(issue_id, title, content, project_name)
                store_issue_in_db(issue, project_name, session)
                action = "Stored"
                status = "[green]New Issue[/green]"

            table.add_row(file, action, status)

    console.print(table)

def main():
    try:
        with Halo(text='Initializing setup', spinner='dots') as spinner:
            project_root = get_project_root()
            project_name = os.path.basename(project_root)
            files, issues_dir = get_markdown_files(project_root)
            spinner.succeed('Setup complete')

        with change_directory(project_root):
            process_issues(files, issues_dir, project_name)

        rprint("[bold green]All issues processed and stored successfully![/bold green]")

    except Exception as e:
        rprint(f'[bold red]Error:[/bold red] {str(e)}')

if __name__ == "__main__":
    main()
