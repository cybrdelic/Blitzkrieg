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
from blitzkrieg.file_management.DirectoryManager import DirectoryManager
from blitzkrieg.file_manager import FileManager
from blitzkrieg.file_management.MarkdownManager import MarkdownManager
from blitzkrieg.issue_management.IssueManager import IssueManager
from blitzkrieg.project_management.base_project_management.ProjectManager import ProjectManager
from blitzkrieg.project_management.db.DBManager import DatabaseManager
from blitzkrieg.project_management.db.connection import get_db_engine, get_db_session
from blitzkrieg.project_management.db.services.issues_service import IssueService
from blitzkrieg.project_management.db.services.project_service import ProjectService
import time
from blitzkrieg.project_management.db.models.issue import Issue

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

def main():
    issue_manager.create_test_issue_in_db()

if __name__ == '__main__':
    main()
