import os
import uuid
from contextlib import contextmanager
from datetime import datetime
from rich.console import Console
from rich.progress import track
from rich.box import ROUNDED
from rich import print as rprint
from rich.table import Table
from rich.traceback import install
from rich.theme import Theme
from rich.progress import Progress, BarColumn, TextColumn
from halo import Halo
from blitzkrieg.project_management.db.connection import get_db_session
from blitzkrieg.project_management.db.services.issues_service import IssueService
from blitzkrieg.project_management.db.services.project_service import ProjectService
import time

# Enhanced error reporting
install()
# Custom theme for rich
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "error": "bold red",
    "success": "bold green",
    "header": "bold blue"
})

console = Console(theme=custom_theme)

def show_task_progress_bar(task_description, total):
    """
    Display a progress bar for a given task.
    """
    with Progress(
        "[progress.description]{task.description}",
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.0f}%",
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(task_description, total=total)
        while not progress.finished:
            progress.update(task, advance=0.1)
            time.sleep(0.1)
# User Flow 1: Setup and Environment Configuration
def find_project_root_directory(marker='.git'):
    """
    Find the project root by looking for a directory containing a specific marker.

    Args:
        marker (str): A filename or directory name that uniquely identifies the project root.

    Returns:
        str: Absolute path to the project root directory.
    """
    current_dir = os.getcwd()
    while True:
        if os.path.isdir(os.path.join(current_dir, marker)):
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            # Reached the filesystem root without finding the marker
            raise FileNotFoundError(f"Could not find the {marker} to identify the project root.")
        current_dir = parent_dir


@contextmanager
def temporary_directory_change(path):
    original_path = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original_path)

# User Flow 2: File and Directory Handling
def validate_directory_presence(directory, error_message):
    if not os.path.isdir(directory):
        rprint(f'[bold red]Error:[/bold red] {error_message}')
        raise FileNotFoundError(error_message)

def list_files_with_suffix(directory, suffix):
    return [file for file in os.listdir(directory) if file.endswith(suffix)]

# User Flow 3: Markdown File Processing
def extract_file_details(file_path):
    with open(file_path, 'r') as file:
        id_line = file.readline().strip()
        title = file.readline().strip()
        content = file.read().strip()
    return id_line, title, content


def prepend_uuid_to_file(file_path, uuid_str):
    with open(file_path, 'r+') as file:
        content = file.read()
        file.seek(0, 0)
        file.write(f'{uuid_str}\n{content}')

def fetch_markdown_files_list(parent_dir):
    issues_dir = os.path.join(parent_dir, '.docs', 'issues')
    validate_directory_presence(issues_dir, 'Issues directory not found in .docs.')
    return list_files_with_suffix(issues_dir, '.md'), issues_dir

# User Flow 4: Issue Management
def generate_issue_metadata(issue_id, title, content, project_name):
    shorthand_tag = ''.join(ch for ch in project_name if ch not in 'aeiou').lower()[:4]
    branch_name = f'{shorthand_tag}{title[1:].replace(" ", "-").lower() if title.startswith("#") else title.replace(" ", "-").lower()}'
    return {'id': issue_id, 'title': title.replace('#', '').strip(), 'branch_name': branch_name, 'content': content}

def check_issue_presence_in_database(issue_id, session):
    issue = IssueService().get_issues(session, issue_id)
    return issue is not None, issue

def save_issue_to_database(issue, project_name, session):
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

def rewrite_markdown_file(issue, file_path):
    with open(file_path, 'w') as file:
        file.write(f'{issue.id}\n')
        file.write(f'{issue.title}\n\n')
        file.write(issue.description)

# User Flow 5: Syncing Issues to Database and Markdown
def verify_uuid_format(uuid_to_test, version=4):
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test

def check_uuid_or_new_issue(uuid_to_test, session):
    if not uuid_to_test or not verify_uuid_format(uuid_to_test):
        return False, True  # Invalid UUID, but might be a new issue
    exists, _ = check_issue_presence_in_database(uuid_to_test, session)
    return exists, False  # Valid UUID and issue exists

def handle_issue_file(file, issues_dir, project_name, session, table):
    """
    Process a single issue file - create a new issue, update an existing one, or report an error.
    """
    file_path = os.path.join(issues_dir, file)
    issue_id, title, content = extract_file_details(file_path)
    action, status = "", ""

    if not verify_uuid_format(issue_id):
        # Generate new UUID and prepend to file
        new_uuid = str(uuid.uuid4())
        prepend_uuid_to_file(file_path, new_uuid)
        issue_id = new_uuid
        action, status = "UUID Prepended", "[green]New UUID Added[/green]"

    # Check if issue exists in DB and whether the UUID is valid
    issue_exists, issue_in_db = check_issue_presence_in_database(issue_id, session)

    if action == "" and status == "":  # Only proceed if no action has been taken yet
        if not issue_exists:  # New issue
            issue_id = str(uuid.uuid4())
            action, status = manage_new_issue_creation(file, issue_id, title, content, project_name, session, issues_dir)
        elif issue_exists:
            existing_issue = issue_in_db
            action, status = update_issue_if_modified(file, issue_id, title, content, existing_issue, session, file_path)

    table.add_row(file, action, status)


def manage_new_issue_creation(file, issue_id, title, content, project_name, session, issues_dir):
    """
    Handle the creation of a new issue.
    """
    issue = generate_issue_metadata(issue_id, title, content, project_name)
    save_issue_to_database(issue, project_name, session)
    file_path = os.path.join(issues_dir, file)
    prepend_uuid_to_file(file_path, issue_id)
    rprint(f"[green]New issue {issue_id} stored in DB and UUID added to file {file}[/green]")
    return "Created", "[green]New Issue Created[/green]"

def update_issue_if_modified(file, issue_id, title, content, existing_issue, session, file_path):
    """
    Update an existing issue if there are changes.
    """
    title_changed = existing_issue.title != title
    content_changed = existing_issue.description != content
    if title_changed or content_changed:
        existing_issue.title = title if title_changed else existing_issue.title
        existing_issue.description = content if content_changed else existing_issue.description
        existing_issue.updated_at = datetime.now()
        session.commit()
        rewrite_markdown_file(existing_issue, file_path)
        rprint(f"[orange]Issue {issue_id} updated in DB and markdown file {file}[/orange]")
        return "Updated", "[orange]Updated in DB & Markdown[/orange]"

    return "Unchanged", "[blue]No Changes[/blue]"

def convert_title_to_snakecase(title):
    snake_case_title = title.replace('-', ' ').replace('#', '').replace(' ', '_').replace(":","").lower()
    # if underscore is at the beginning of the title, remove it
    if snake_case_title[0] == '_':
        snake_case_title = snake_case_title[1:]
    return snake_case_title
def generate_markdown_from_db_entry(issue, issues_dir):
    snakecase_title = convert_title_to_snakecase(issue.title)
    file_name = f"{snakecase_title}.md"
    file_path = os.path.join(issues_dir, file_name)
    with open(file_path, 'w') as file:
        file.write(f'{issue.id}\n')
        file.write(f'{issue.title}\n\n')
        file.write(issue.description)
    rprint(f"[green]Markdown file created for issue {issue.id} ({file_name})[/green]")

def synchronize_database_issues_to_markdown(issues_dir, project_name, session, table):
    """
    Sync issues from the database to markdown files and update the table with the action taken.

    Args:
        issues_dir (str): Directory path of the issues.
        project_name (str): Name of the project.
        session: Database session.
        table (Table): Table object to update with actions and statuses.
    """
    issues = IssueService().get_all_issues(session)
    markdown_files = list_files_with_suffix(issues_dir, '.md')
    markdown_ids = [extract_file_details(os.path.join(issues_dir, f))[0] for f in markdown_files]

    for issue in issues:
        if str(issue.id) not in markdown_ids:
            generate_markdown_from_db_entry(issue, issues_dir)
            action = "Synced"
            status = "[green]Markdown File Created[/green]"
            file_name = f"{convert_title_to_snakecase(issue.title)}.md"  # Assuming file naming convention
            table.add_row(file_name, action, status)


def configure_rich_table():
    """
    Configure and return a Rich table for displaying the issue processing status.

    The table will have columns for 'File', 'Action', and 'Status', with added
    styling and alignment for better readability and appearance.

    Returns:
        Table: A configured Rich table object ready for use.
    """
    # Create a new table with a title and header
    table = Table(
        title="Issue Processing Status",
        show_header=True,
        header_style="bold magenta",  # Bold magenta text on black background for headers
        title_style="bold cyan",      # Bold cyan text on black background for title
        border_style="bright_green",           # Bright green color for table border
        box=ROUNDED,                  # Using rounded corners for the table
        padding=(0, 1),                        # Padding inside cells (top/bottom, left/right)
        title_justify="left"                 # Center-justify the title
    )

    # Define the columns with enhanced styling
    table.add_column("File", style="bold yellow", justify="left", width=40, no_wrap=True)
    table.add_column("Action", style="bold blue", justify="left", width=25)
    table.add_column("Status", style="bold green", justify="left", width=35)

    return table

def execute_issue_processing_workflow(files, issues_dir, project_name):
    """
    Process each issue file and synchronize issues between markdown and database.

    Args:
        files (list): List of issue file names.
        issues_dir (str): Directory path of the issues.
        project_name (str): Name of the project.
    """
    # Inform the user that issue processing is starting
    console.print("Starting issue processing...", style="info")

    # Configure the table for displaying processing status
    table = configure_rich_table()

    # Establish a database session for issue processing
    with get_db_session() as session:
        # Process each file, displaying progress with Rich's track
        for file in track(files, description="[green]Processing issues..."):
            try:
                # Attempt to process individual file
                handle_issue_file(file, issues_dir, project_name, session, table)
            except Exception as e:
                # Log and display error without halting the entire process
                console.print(f"Error in file {file}: {e}", style="error")
                # Record the error in the table
                table.add_row(file, "Error", "[red]Failed[/red]")

        # Synchronize the issues from database to markdown files
        console.print("Synchronizing database issues to Markdown...", style="warning")
        try:
            synchronize_database_issues_to_markdown(issues_dir, project_name, session, table)
        except Exception as e:
            # Handle and display synchronization errors
            console.print(f"Synchronization error: {e}", style="error")

    # Display the final status table with processing results
    console.print(table)
    # Confirm completion of issue processing
    console.print("Issue processing completed.", style="success")

def main():
    try:
        with Halo(text='Initializing setup', spinner='dots'):
            project_root = find_project_root_directory()
            project_name = os.path.basename(project_root)
            files, issues_dir = fetch_markdown_files_list(project_root)
            console.print('Setup complete')
        with temporary_directory_change(project_root):
            execute_issue_processing_workflow(files, issues_dir, project_name)
        console.print("[bold green]All issues processed and stored successfully![/bold green]")
    except Exception as e:
        console.print(f'[bold red]Error:[/bold red] {str(e)}')

if __name__ == "__main__":
    main()
 OK SO I HAVE THIS SCRIPT BUT I WANT IT TO WORK FO R ALL THESE SCENARIOS:
1. A USER CREATES A MARKDOWN FILE IN THE .docs/issues DIR WITH THE TITLE IN THE LINE WITH A SINGLE HASHTAG , AND THE CONTENT BEING EVERYTHING UNDER THE TITLE: IN THIS CASE, I WANT THE SCRIPT TO PARSE THE FILE, GET THE TITLE, AND CONTENT, AND ADD A UUID TO THE FIRST LINE OF THE FILE TO DENOTE THE NOTATION OF ITS EXISTENCE. THEN CREATE THE ISSUE WITH THE APPROPRIATE DATA AND ADD IT AS A ROW TO THE ISSUES TABLE IN THE DB.
2. A USER CREATES AN ISSUE IN THE DB THAT DOESNT EXIST IN THE .docs/issues dir: Add the issue markdown in the following format:
{uuid}
# {title}

{content (formatted in markdown)}
3. A user updates something either in the db or the markdown files: they need to sync
4. a user deletes something either in the db or the markdown files: they need to sync, preferably a soft delete.

Can we discuss how to implement this system in the best way possible while keeping this in the same file, while focusing on best practices, ensuring abstractness for reusability and extensibility?
