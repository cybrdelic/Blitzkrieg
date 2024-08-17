from blitzkrieg.ui_management.console_instance import console
import subprocess

def stage_files_for_commit(files: list):
    """Stage files for commit."""
    try:
        console.handle_wait("Staging files for commit")
        for file in files:
            console.handle_info(f"Staging file: {file}")
            subprocess.run(["git", "add", file], check=True)
        console.handle_success("Staged files for commit")
    except subprocess.CalledProcessError as e:
        console.handle_error(f"Failed to stage files for commit: {str(e)}")
        raise SystemExit

def commit_staged_files(commit_message: str):
    """Commit staged files."""
    try:
        console.handle_wait("Committing staged files")
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        console.handle_success("Committed staged files")
    except subprocess.CalledProcessError as e:
        console.handle_error(f"Failed to commit staged files: {str(e)}")
        raise SystemExit

def create_git_tag(tag_name: str):
    """Create a git version tag."""
    try:
        console.handle_wait(f"Creating git version tag: {tag_name}")
        subprocess.run(["git", "tag", tag_name], check=True)
        console.handle_success(f"Created git version tag: {tag_name}")
    except subprocess.CalledProcessError as e:
        console.handle_error(f"Failed to create git version tag: {tag_name}. Exception e has occurred: {str(e)}")
        raise SystemExit

def authenticate_github_cli():
    try:
        console.handle_wait("Ensuring GitHub authentication")
        subprocess.run(["gh", "auth", "status"], check=True)
        console.handle_success("GitHub authentication successful")
    except subprocess.CalledProcessError as e:
        console.handle_error(f"Failed to authenticate with GitHub CLI: {str(e)}")
        raise SystemExit

def sync_local_changes_to_remote_repository():
    try:
        console.handle_wait("Syncing local changes with remote repository")
        subprocess.run(["gh", "repo", "sync"], check=True)
        console.handle_success("Synced changes")
    except subprocess.CalledProcessError as e:
        console.handle_error(f"Failed to sync changes: {str(e)}")
        raise SystemExit
