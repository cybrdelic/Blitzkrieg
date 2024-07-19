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
from blitzkrieg.database_manager import DatabaseManager
from blitzkrieg.file_management.DirectoryManager import DirectoryManager
from blitzkrieg.file_manager import FileManager
from blitzkrieg.file_management.MarkdownManager import MarkdownManager
from blitzkrieg.issue_management.IssueManager import IssueManager
from blitzkrieg.project_management.base_project_management.ProjectManager import ProjectManager
from blitzkrieg.project_management.db.connection import get_db_engine, get_db_session


from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface

# Enhanced error reporting
install()

engine = get_db_engine()
db_manager = DatabaseManager(engine)
console_interface = ConsoleInterface()
project_manager = ProjectManager()
file_manager = FileManager()
directory_manager = DirectoryManager(file_manager)
markdown_manager = MarkdownManager(file_manager)
issue_manager = IssueManager(db_manager, file_manager, console_interface, markdown_manager)



def execute_issue_processing_workflow(files, issues_dir, project_name):
    """
    Process each issue file and synchronize issues between markdown and database.

    Args:
        files (list): List of issue file names.
        issues_dir (str): Directory path of the issues.
        project_name (str): Name of the project.
    """
    console = console_interface.console
    # Inform the user that issue processing is starting
    console.log("Starting issue synchronization process...", style="info")

    # Configure the table for displaying processing status
    table = console_interface.configure_table()

    # Establish a database session for issue processing
    with get_db_session() as session:
        for file in track(files, description="[green]Synchronizing issues..."):
            try:
                # Ensure 'file' is a string, not a list
                if isinstance(file, list):
                    file = file[0]  # Assuming the file name is the first element
                file_path = os.path.join(issues_dir, file)
                issue_manager.sync_issue_docs_to_db(file_path, project_name, session, table)
            except Exception as e:
                console.log(f"Error in file {file}: {e}", style="error")
                table.add_row(file, "Error", "[red]Failed[/red]")

        # Synchronize the issues from database to markdown files
        console.log("Synchronizing database issues to Markdown...", style="warning")
        try:
            issue_manager.sync_db_issues_to_docs(issues_dir, project_name, session, table)
        except Exception as e:
            # Handle and display synchronization errors
            console.log(f"Synchronization error: {e}", style="error")

    # Display the final status table with processing results
    console.log(table)
    # Confirm completion of issue processing
    console.log("Issue processing completed.", style="success")

def main():
    console = console_interface.console
    try:
        with Halo(text='Fetching details from your local...', spinner='dots'):
            project_root = project_manager.find_project_root()
            project_name = os.path.basename(project_root)
            files, issues_dir = markdown_manager.fetch_markdown_files_list(project_root)
        with project_manager.temporary_directory_change(project_root):
            execute_issue_processing_workflow(files, issues_dir, project_name)
        console.log("[bold green]All issues processed and stored successfully![/bold green]")
    except Exception as e:
        console.log(f'[bold red]Error:[/bold red] {str(e)}')

if __name__ == "__main__":
    main()
