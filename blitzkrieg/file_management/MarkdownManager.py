import os
import uuid
from blitzkrieg.file_management.DirectoryManager import DirectoryManager

from blitzkrieg.project_management.db.services.issues_service import IssueService

class MarkdownManager:
    def __init__(self, file_manager):
        self.file_manager = file_manager
        self.directory_manager = DirectoryManager(file_manager)
        self.markdown_suffix = '.md'

    def extract_file_details(self, file_path):
        # Extracts the object (in this case, issue) ID, title, and content from the file. The ID is in the first line. if it isn't then it probably means it is a new issue that hasnt been synched with the database yet. The title is whatever occurs after a singular #. The content is everything after the title.
        content = self.file_manager.read_file(file_path)
        lines = content.split('\n')

        # Check if the file has at least one line
        if len(lines) >= 1:
            id_line = lines[0]
        else:
            id_line = None

        # Find the line with the title
        title = None
        for line in lines[1:]:
            if line.startswith('# '):
                title = line[2:]  # Remove the hashtag and space
                break

        # The content is everything after the title
        content_start_index = lines.index('# ' + title) + 1 if title else 2
        content = '\n'.join(lines[content_start_index:])

        return id_line.strip() if id_line else None, title.strip() if title else None, content.strip()

    def verify_uuid_format(self, uuid_to_test, version=4):
        try:
            uuid_obj = uuid.UUID(uuid_to_test, version=version)
        except ValueError:
            return False
        return str(uuid_obj) == uuid_to_test

    def check_issue_presence_in_database(self, issue_id, session):
        issue = IssueService().get_issues(session, issue_id)
        return issue is not None, issue

    def fetch_markdown_files_list(self, parent_dir):
        issues_dir = os.path.join(parent_dir, '.docs', 'issues')
        self.directory_manager.validate_directory_presence(issues_dir, 'Issues directory not found in .docs.')
        return self.file_manager.list_files_with_suffix(issues_dir, '.md'), issues_dir
    
