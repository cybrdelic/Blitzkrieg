import re

class MarkdownParser:
    def __init__(self, content: str):
        self.content = content
        self.lines = content.split('\n')

    def extract_id(self, file_path):
        # extract the id from the end of the filename
        filename = file_path.split('/')[-1]
        id_match = re.search(r'(\w{8}-\w{4}-\w{4}-\w{4}-\w{12})', filename)
        if id_match:
            return id_match.group()
        return None

    def extract_title(self):
        # Find the first Markdown heading as the title
        title = None
        for line in self.lines:
            if line.startswith('# '):
                title = line[2:].strip()  # Remove the '#' and any leading spaces
                break
        return title

    def extract_content(self):
        # Extract content starting after the title line
        if self.extract_title():
            title_index = self.lines.index('# ' + self.extract_title())
            return '\n'.join(self.lines[title_index + 1:]).strip()
        return None
