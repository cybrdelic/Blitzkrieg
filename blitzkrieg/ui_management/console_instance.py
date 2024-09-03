from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
from blitzkrieg.ui_management.tui import TextualApp

console = ConsoleInterface()
def create_tui_app(commands=None):
    app = TextualApp(commands)
    return app

def run_tui(commands=None):
    app = create_tui_app(commands)
    app.run()

# Global instances for backward compatibility
app = create_tui_app()
