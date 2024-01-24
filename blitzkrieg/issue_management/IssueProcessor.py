import logging
from rich.progress import track
from blitzkrieg.project_management.db.services.issues_service import IssueService
import os

class IssueProcessor:
    def __init__(self, file_handler, console_interface, issue_manager):
        self.file_handler = file_handler
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.console_interface = console_interface
        self.issue_manager = issue_manager
        self.database_manager = issue_manager.database_manager
        self.error_manager = console_interface.error_manager

    def check_issue_presence_in_database(self, issue_id, session):
        issue = IssueService().get_issues(session, issue_id)
        return issue is not None, issue

    def manage_new_issue_creation(self, file_path, issue_id, title, content, project_name, session):
        self.logger.info(f"Creating new issue {issue_id} in database")
        index = IssueService().get_next_index(session)
        branch_name = f"{project_name}-{index}"
        IssueService().create_issue(
            session=session,
            id=issue_id,
            title=title,
            index=index,
            branch_name=branch_name,
            description=content,
            project_id=project_name
        )
        self.file_handler.prepend_uuid_to_file(file_path, issue_id)
        return "Created", "[green]New Issue Added[/green]"

    def execute_issue_processing_workflow(self, files, issues_dir, project_name):
        """
        Process each issue file and synchronize issues between markdown and database.

        Args:
            files (list): List of issue file names.
            issues_dir (str): Directory path of the issues.
            project_name (str): Name of the project.
        """
        console = self.console_interface.console
        # Inform the user that issue processing is starting
        console.print("Starting issue processing...", style="info")

        # Configure the table for displaying processing status
        table = self.console_interface.configure_table()

        # Establish a database session for issue processing
        with self.db_manager.sessions_scope() as session:
            for file in track(files, description="[green]Processing issues..."):
                try:
                    # Ensure 'file' is a string, not a list
                    if isinstance(file, list):
                        file = file[0]  # Assuming the file name is the first element
                    file_path = os.path.join(issues_dir, file)
                    self.issue_manager.handle_issue_file(file_path, project_name, session, table)
                except Exception as e:
                    console.print(f"Error in file {file}: {e}", style="error")
                    table.add_row(file, "Error", "[red]Failed[/red]")

            # Synchronize the issues from database to markdown files
            console.print("Synchronizing database issues to Markdown...", style="warning")
            try:
                self.issue_manager.synchronize_database_issues_to_markdown(issues_dir, project_name, session, table)
            except Exception as e:
                # Handle and display synchronization errors
                console.print(f"Synchronization error: {e}", style="error")

        # Display the final status table with processing results
        console.print(table)
        # Confirm completion of issue processing
        console.print("Issue processing completed.", style="success")
