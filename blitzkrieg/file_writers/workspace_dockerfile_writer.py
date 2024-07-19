from blitzkrieg.file_writers.base_dockerfile_writer import BaseDockerfileWriter
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface

class WorkspaceDockerfileWriter(BaseDockerfileWriter):
    def __init__(self, workspace_path: str, console: ConsoleInterface):
        super().__init__(path=workspace_path, console=console)

    def write_dockerfile(self):
        dockerfile_content = """
        # Dockerfile.alembic_worker
        FROM python:3.9-slim

        # Set the working directory
        WORKDIR /app

        # Copy the requirements file and install dependencies
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt

        # Copy the application code
        COPY . .

        # Install Alembic
        RUN pip install alembic

        # Ensure the script has execution permissions
        RUN chmod +x /app/alembic_init.sh

        RUN chown -R 1000:1000 /app

        # Set the entry point to the initialization script
        ENTRYPOINT ["/app/alembic_init.sh"]
        """
        super().write_dockerfile(dockerfile_content)
