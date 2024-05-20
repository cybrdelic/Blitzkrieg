import os

class DocumentDatabaseIntegration:
    def __init__(self, db_manager, file_manager, console_interface, markdown_manager):
        self.db_manager = db_manager
        self.file_manager = file_manager
        self.console_interface = console_interface
        self.markdown_manager = markdown_manager

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
        console.log("Starting issue processing...", style="info")

        # Configure the table for displaying processing status
        table = self.console_interface.configure_table()

        # Establish a database session for issue processing
        with self.db_manager.get_db_session() as session:
            for file in self.console_interface.track(files, description="[green]Processing issues..."):
                try:
                    # Process the issue file
                    issue = self.markdown_manager.process_issue_file(file, issues_dir, project_name)
                    # Synchronize the issue with the database
                    self.db_manager.synchronize_issue_with_db(session, issue)
                    # Add the issue to the table
                    self.console_interface.add_issue_to_table(table, issue)
                except Exception as e:
                    # Handle any exceptions that occur during issue processing
                    self.console_interface.handle_issue_processing_exception(console, file, e)

            # Display the processing status
            self.console_interface.display_processing_status(console, table)
