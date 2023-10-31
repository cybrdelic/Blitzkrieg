from fuzzywuzzy import process
from pathlib import Path
from blitzkrieg.cli.ui_utils import handle_error

def get_template_path(template_dir: Path, input_template_name: str) -> Path:
    try:
        available_files = [f.name for f in template_dir.iterdir() if f.is_file()]
        best_match, score = process.extractOne(input_template_name, available_files)
        if score > 80:
            return template_dir / best_match
        else:
            handle_error(f"No close match found for: {input_template_name}")
            return None
    except Exception as e:
        handle_error(f"An exception occurred: {e}")
        return None
