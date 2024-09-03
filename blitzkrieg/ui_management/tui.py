from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual.widgets import SelectionList
from textual.widgets import Header, Footer, Static, Button, Log
from textual.containers import Container, Vertical

class CommandScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Container(
            Static("Enter command arguments:"),
            Static("", id="argument_prompt"),
            Static("", id="argument_input", classes="input"),
            Button("Execute", id="execute"),
            Button("Back", id="back")
        )

class TextualApp(App):
    CSS = """
    #log {
        height: 60%;
        border: solid $accent;
    }
    #spinner {
        height: 5%;
        border: solid $accent;
    }
    #command_list {
        height: 25%;
        border: solid $accent;
    }
    .input {
        background: $boost;
        color: $text;
        padding: 1 2;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("e", "toggle_command_list", "Toggle Command List"),
    ]

    def __init__(self, commands):
        super().__init__()
        self.commands = commands
        self.log_widget = Log(id="log", highlight=True)
        self.spinner = Static(id="spinner")
        self.command_list = SelectionList[str](id="command_list")

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            self.log_widget,
            self.spinner,
            self.command_list,
            Vertical(
                Button("Copy Output", id="copy_output"),
                Button("Exit", id="exit")
            )
        )
        yield Footer()

    def on_mount(self):
        self.command_list.display = False
        for command in self.commands:
            self.command_list.add_option((command.name, command.name))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit":
            self.exit()

    def action_toggle_command_list(self):
        self.command_list.display = not self.command_list.display

    def on_selection_list_selected(self, event: SelectionList.selected):
        selected_command = next((cmd for cmd in self.commands if cmd.name == event.value), None)
        if selected_command:
            self.push_screen(CommandScreen(selected_command))
