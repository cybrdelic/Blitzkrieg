import ast
import inspect
import os
import pyperclip
import sys
from blitzkrieg.ui_management.console_instance import console

def is_click_command(node: ast.FunctionDef) -> bool:
    """Check if a function definition is a Click command."""
    return any(
        isinstance(decorator, ast.Call) and
        isinstance(decorator.func, ast.Attribute) and
        decorator.func.attr == 'command'
        for decorator in node.decorator_list
    )

def extract_function_and_references(function_name):
    try:
        console.handle_wait(f"Extracting function '{function_name}' and its references...")
        # Get all Python files in the current working directory
        console.handle_wait("Getting all Python files in the current working directory...")
        python_files = [f for f in os.listdir() if f.endswith('.py')]
        console.handle_success(f"Found {len(python_files)} Python files in the current working directory.")

        function_def = None
        references = []

        for file in python_files:
            try:
                console.handle_wait(f"Reading file {file}...")
                with open(file, 'r') as f:
                    content = f.read()
                    tree = ast.parse(content)
            except Exception as e:
                console.handle_error(f"Error reading file {file}: {str(e)}")
                continue

            console.handle_wait(f"Walking the AST of file {file}...")
            for node in ast.walk(tree):
                console.handle_wait(f"Checking node {node} is a function definition or reference")
                if isinstance(node, ast.FunctionDef):
                    if node.name == function_name or (is_click_command(node) and any(
                        isinstance(decorator, ast.Call) and
                        len(decorator.args) > 0 and
                        isinstance(decorator.args[0], ast.Str) and
                        decorator.args[0].s == function_name
                        for decorator in node.decorator_list
                    )):
                        function_def = ast.get_source_segment(content, node)
                        console.handle_success(f"Function '{function_name}' found in file {file}.")
                elif isinstance(node, (ast.Name, ast.Attribute)):
                    console.handle_info(f"Checking if node {node} is a reference to function '{function_name}'...")
                    if hasattr(node, 'id') and node.id == function_name:
                        references.append(ast.get_source_segment(content, node.parent))
                        console.handle_success(f"Reference to function '{function_name}' found in file {file}.")
                    elif hasattr(node, 'attr') and node.attr == function_name:
                        references.append(ast.get_source_segment(content, node.parent))
                        console.handle_success(f"Reference to function '{function_name}' found in file {file}.")

        if function_def is None:
            console.handle_error(f"Function '{function_name}' not found in the current working directory.")

        result = f"Function definition:\n\n{function_def}\n\nReferences:\n"
        for ref in references:
            result += f"\n{ref}"

        # Copy to clipboard
        try:
            pyperclip.copy(result)
            print("Result copied to clipboard.")
        except Exception as e:
            print(f"Error copying to clipboard: {str(e)}")

        console.handle_info(result)

    except Exception as e:
        console.handle_error(f"An error occurred: {str(e)}")
