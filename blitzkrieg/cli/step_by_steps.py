from blitzkrieg.cli.ui_utils import Step, TextComponent, step_by_step


def show_generate_compose_file_steps(project_name: str):
    steps = [
        Step("Generating Docker Compose File", [
            TextComponent(f"Working on container named {project_name}"),
            TextComponent("Rendering Template")
        ])
    ]
    step_by_step(steps)

def show_kubernetes_setup_steps():
    steps = [
        Step("Setting up Kubernetes...", [
            TextComponent("Generating Kubernetes YAML files..."),
            TextComponent("Applying configurations to cluster...")
        ])
    ]
    step_by_step(steps)
