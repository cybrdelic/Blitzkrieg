import os

def create_setup_content(project_name: str, email: str, github_username: str, description: str):
    """Create the content for setup.py."""
    return f"""
    # setup.py
    from setuptools import setup, find_packages

    setup(
        name="{project_name}",
        version="0.1.0",
        author="{email}",
        author_email="{email}",
        description="{description}",
        url="https://github.com/{github_username}/{project_name}",
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        package_dir={{"": "src"}},
        packages=find_packages(where="src"),
        python_requires=">=3.6",
        install_requires=[
            "click"
        ],
        entry_points={{
            'console_scripts': [
                '{project_name}={project_name}.core.{project_name}:main',
            ],
        }},
    )
    """

def write_to_file(filename: str, content: str):
    """Write the content to a file."""
    try:
        with open(filename, 'w') as f:
            f.write(content.strip())
        print(f"Successfully created {filename}.")
    except Exception as e:
        print(f"Error creating {filename}: {e}")

def create_setup(project_name: str, email: str, github_username: str, description: str, project_dir: str):
    """Create setup.py."""
    print("Creating setup.py...")
    os.chdir(project_dir)
    setup_content = create_setup_content(project_name, email, github_username, description)
    write_to_file('setup.py', setup_content)
