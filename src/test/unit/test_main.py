from unittest.mock import MagicMock, patch

import click.testing

import main


class TestMainFunction:
    """Test the main CLI function."""

    def test_main_help_option(self):
        """Test that main function responds to --help."""
        runner = click.testing.CliRunner()
        result = runner.invoke(main.main, ['--help'])

        assert result.exit_code == 0
        assert 'Environment' in result.output
        assert 'Team name' in result.output

    @patch('main.Pythena')
    @patch('main.configure_logging')
    def test_main_successful_execution(self, mock_configure_logging, mock_pythena):
        """Test successful execution of main function."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_configure_logging.return_value = mock_logger

        mock_pythena_instance = MagicMock()
        mock_pythena_instance.get_properties.return_value = {'test': 'value'}
        mock_pythena_instance.get_property_value.return_value = 'test_value'
        mock_pythena.return_value = mock_pythena_instance

        runner = click.testing.CliRunner()
        result = runner.invoke(main.main, ['--env', 'dev', '--team', 'acad'])

        assert result.exit_code == 0
        mock_pythena.assert_called_once_with('test', 'dev', 'acad', 'acad,dev')

    @patch('main.Pythena')
    @patch('main.configure_logging')
    def test_main_athena_failure(self, mock_configure_logging, mock_pythena):
        """Test main function handles Athena connection failure."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_configure_logging.return_value = mock_logger

        mock_pythena_instance = MagicMock()
        mock_pythena_instance.get_properties.return_value = None
        mock_pythena.return_value = mock_pythena_instance

        runner = click.testing.CliRunner()
        result = runner.invoke(main.main, ['--env', 'dev', '--team', 'acad'])

        assert result.exit_code == 1

    @patch('main.Pythena')
    @patch('main.configure_logging')
    def test_main_exception_handling(self, mock_configure_logging, mock_pythena):
        """Test that main function handles exceptions properly."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_configure_logging.return_value = mock_logger

        mock_pythena.side_effect = Exception("Test exception")

        runner = click.testing.CliRunner()
        result = runner.invoke(main.main, ['--env', 'dev', '--team', 'acad'])

        assert result.exit_code == 1
