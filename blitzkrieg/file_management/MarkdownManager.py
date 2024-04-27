import os
import uuid
from blitzkrieg.file_management.DirectoryManager import DirectoryManager
from blitzkrieg.file_management.MarkdownParser import MarkdownParser
from blitzkrieg.project_management.db.services.issues_service import IssueService

class MarkdownManager:
    def __init__(self, file_manager):
        self.file_manager = file_manager
        self.directory_manager = DirectoryManager(file_manager)
        self.markdown_suffix = '.md'

    def extract_file_details(self, file_path):
        content = self.file_manager.read_file(file_path)
        parser = MarkdownParser(content)
        issue_id = parser.extract_id(file_path)
        title = parser.extract_title()
        content = parser.extract_content()
        return issue_id, title, content

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
