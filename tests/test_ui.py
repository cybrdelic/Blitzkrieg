import pytest
from rundbfast.core.cli.ui import print_cli_header, print_cli_footer, print_message, print_header, print_label, print_warning, print_error, print_divider, print_success, print_table, show_choices, show_progress, show_spinner

# Test for print_cli_header
def test_print_cli_header(capsys):
    print_cli_header()
    captured = capsys.readouterr()
    assert "RunDBFast" in captured.out

# Test for print_cli_footer
def test_print_cli_footer(capsys):
    print_cli_footer()
    captured = capsys.readouterr()
    assert "Thanks for riding with us!" in captured.out

# Test for print_message without title
def test_print_message_no_title(capsys):
    message = "Test Message"
    print_message(message)
    captured = capsys.readouterr()
    assert message in captured.out

# Test for print_message with title
def test_print_message_with_title(capsys):
    message = "Test Message"
    title = "Title"
    print_message(message, title=title)
    captured = capsys.readouterr()
    assert message in captured.out
    assert title in captured.out

# Test for print_header
def test_print_header(capsys):
    header_text = "Header Text"
    print_header(header_text)
    captured = capsys.readouterr()
    assert header_text in captured.out

# Test for print_label
def test_print_label(capsys):
    label_text = "Label"
    print_label(label_text)
    captured = capsys.readouterr()
    assert label_text in captured.out

# Test for print_warning
def test_print_warning(capsys):
    warning_text = "Warning Message"
    print_warning(warning_text)
    captured = capsys.readouterr()
    assert warning_text in captured.out
    assert "⚠️" in captured.out

# Test for print_error
def test_print_error(capsys):
    error_text = "Error Message"
    print_error(error_text)
    captured = capsys.readouterr()
    assert error_text in captured.out
    assert "❌" in captured.out

# Test for print_success
def test_print_success(capsys):
    success_text = "Success Message"
    print_success(success_text)
    captured = capsys.readouterr()
    assert success_text in captured.out
    assert "✅" in captured.out

# Test for print_divider
def test_print_divider(capsys):
    print_divider()
    captured = capsys.readouterr()
    # Just check if the output has some content, as the exact appearance of the divider might vary
    assert len(captured.out.strip()) > 0

# For other methods like show_choices, pause_for_user, and clear_screen,
# testing is a bit more complex due to their interactive nature or effects on the terminal.
# You might need to use mocking or other strategies to test them.
