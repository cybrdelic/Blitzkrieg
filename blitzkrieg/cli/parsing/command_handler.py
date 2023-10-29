
from blitzkrieg.core.managers.postgres.postgres_manager import initialize_with_persistence_check
from asciimatics.screen import Screen
import asyncio

class CommandHandler:

    def init(self, args):
        project_name = input("Project Name: ")
        asyncio.run(initialize_with_persistence_check(project_name, init_mode=True))
