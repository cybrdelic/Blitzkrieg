# from unittest.mock import call, patch
# import pytest
# from rundbfast.core.cli.ui import print_cli_header, print_cli_footer, print_message, print_header, print_label, print_warning, print_error, print_divider, print_success, print_table, show_choices, show_progress, show_spinner, generate_cli_header
# from rich.panel import Panel
# import time

# def test_generate_cli_header():
#     header_panel = generate_cli_header()
#     assert isinstance(header_panel, Panel)

# # Test for print_cli_header
# def test_print_cli_header(capsys):
#     print_cli_header()
#     captured = capsys.readouterr()
#     print(f"Captured output: {captured.out}")

# # Test for print_cli_footer
# def test_print_cli_footer(capsys):
#     print_cli_footer()
#     captured = capsys.readouterr()
#     print(f"Captured output: {captured.out}")
#     assert "Thanks for riding with us!" in captured.out

# # Test for print_message without title
# def test_print_message_no_title(capsys):
#     message = "Test Message with no title"
#     print_message(message)
#     captured = capsys.readouterr()
#     print(f"Captured output: {captured.out}")
#     assert message in captured.out

# # Test for print_message with title
# def test_print_message_with_title(capsys):
#     message = "Test Message with Title"
#     title = "Title"
#     print_message(message, title=title)
#     captured = capsys.readouterr()
#     print(f"Captured output: {captured.out}")
#     assert message in captured.out
#     assert title in captured.out

# # Test for print_header
# def test_print_header(capsys):
#     header_text = "Header Text"
#     print_header(header_text)
#     captured = capsys.readouterr()
#     assert header_text in captured.out

# # Test for print_label
# def test_print_label(capsys):
#     label_text = "Label"
#     print_label(label_text)
#     captured = capsys.readouterr()
#     assert label_text in captured.out

# # Test for print_warning
# def test_print_warning(capsys):
#     warning_text = "Warning Message"
#     print_warning(warning_text)
#     captured = capsys.readouterr()
#     print(f"Captured output: {captured.out}")
#     assert warning_text in captured.out
#     assert "⚠️" in captured.out

# # Test for print_error
# def test_print_error(capsys):
#     error_text = "Error Message"
#     print_error(error_text)
#     captured = capsys.readouterr()
#     print(f"Captured output: {captured.out}")
#     assert error_text in captured.out
#     assert "❌" in captured.out

# # Test for print_success
# def test_print_success(capsys):
#     success_text = "Success Message"
#     print_success(success_text)
#     captured = capsys.readouterr()
#     print(f"Captured output: {captured.out}")
#     assert success_text in captured.out
#     assert "✅" in captured.out

# # Test for print_divider
# def test_print_divider(capsys):
#     print_divider()
#     captured = capsys.readouterr()
#     print(f"Captured output: {captured.out}")
#     # Just check if the output has some content, as the exact appearance of the divider might vary
#     assert len(captured.out.strip()) > 0

# # Test for print_table
# def test_print_table(capsys):
#     data = [{"Name": "John", "Age": "30"}, {"Name": "Jane", "Age": "25"}]
#     print_table(data)
#     captured = capsys.readouterr()
#     print(f"Captured output: {captured.out}")
#     assert "John" in captured.out
#     assert "Jane" in captured.out
#     assert "30" in captured.out
#     assert "25" in captured.out

# from unittest.mock import MagicMock

# @pytest.mark.parametrize("choices_list, expected", [(["Choice1", "Choice2"], "Choice1"), (["Option1", "Option2"], "Option2")])
# def test_show_choices(choices_list, expected):
#     mock_select = MagicMock()
#     mock_select.ask.return_value = expected
#     with patch('rundbfast.core.cli.ui.questionary.select', return_value=mock_select):
#         result = show_choices("Pick an option:", choices_list)
#     assert result == expected

# @patch('rundbfast.core.cli.ui.Progress')
# def test_show_progress(mocked_progress):
#     mock_task = MagicMock()
#     mocked_progress().add_task.return_value = mock_task

#     with show_progress("Progress test") as task:
#         time.sleep(1)
#         task.completed = 20
#         time.sleep(2)
#         task.completed = 50
#         time.sleep(3)
#         task.completed = 100

#     mocked_progress.assert_called_once()
#     mock_task.completed.assert_has_calls([call(20), call(50), call(100)])

# @patch('rich.spinner.Spinner')
# def test_show_spinner(mocked_spinner):
#     try:
#         with show_spinner("Spinner test"):
#             time.sleep(3)
#     except Exception as e:
#         pytest.fail(f"show_spinner raised an exception: {e}")

#     mocked_spinner.assert_called_once()
