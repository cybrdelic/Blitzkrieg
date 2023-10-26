from setuptools import setup, find_packages

setup(
    name="blitzkrieg",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'rich',
        'pyfiglet',
        'questionary',
    ],
    entry_points={
        'console_scripts': [
            'blitz=blitzkrieg.main:main',
        ],
    },
    author="Alex Figueroa",
    description="A tool to autonomously spin up dockerized PostgreSQL databases.",
    license="MIT",
    keywords="database postgresql docker automation",
    url="https://github.com/your_github/rundbfast",  # GitHub repo link
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
