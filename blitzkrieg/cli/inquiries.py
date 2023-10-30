import inquirer

def get_initial_answer():
    questions = [
        inquirer.List(
            'command',
            message="What do you want to do?",
            choices=['Initialize the project', 'Stop the project'],
        )
    ]
    return inquirer.prompt(questions)['command']

def get_project_name():
    questions = [
        inquirer.Text(
            'project_name',
            message="What is the project name?",
        )
    ]
    return inquirer.prompt(questions)['project_name']

def get_project_init_confirmation(project_name: str):
    questions = [
        inquirer.List(
            'command',
            message=f"Are you sure that you want to initialize the project, {project_name}?",
            choices=['Yes', 'No']
        )
    ]

    return inquirer.prompt(questions)['command']
