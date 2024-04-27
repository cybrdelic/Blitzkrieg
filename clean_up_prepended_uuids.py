import os
import re

# Assuming all files are in the same directory
cwd = os.getcwd()
directory = os.path.join(cwd, '.docs', 'issues')

# Regular expression to match the UUID format
uuid_regex = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

for filename in os.listdir(directory):
    if filename.endswith('.md'):
        # Split the filename by underscores and filter out UUID parts
        parts = filename.split('_')
        new_parts = [part for part in parts if not re.match(uuid_regex, part)]
        new_filename = '_'.join(new_parts)

        # Get the original UUID (last UUID in the original filename)
        uuids = re.findall(uuid_regex, filename)
        if uuids:
            new_filename = f"{uuids[-1]}_{new_filename}"  # Prepend the original UUID

        # Rename the file
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_filename)
        os.rename(old_path, new_path)
