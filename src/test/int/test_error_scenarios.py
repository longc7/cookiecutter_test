from unittest.mock import MagicMock, patch

import click.testing

import main


class TestErrorScenarios:
    """Integration tests for error handling scenarios."""

    @patch('main.Pythena')
    def test_athena_connection_timeout(self, mock_pythena):
        """Test behavior when Athena connection times out."""
        mock_pythena.side_effect = TimeoutError("Connection timeout")

        runner = click.testing.CliRunner()
        result = runner.invoke(main.main, ['--env', 'dev', '--team', 'acad'])

        assert result.exit_code == 1

    @patch('main.Pythena')
    def test_athena_authentication_failure(self, mock_pythena):
        """Test behavior when Athena authentication fails."""
        mock_pythena_instance = MagicMock()
        mock_pythena_instance.get_properties.return_value = None  # Simulates auth failure
        mock_pythena.return_value = mock_pythena_instance

        runner = click.testing.CliRunner()
        result = runner.invoke(main.main, ['--env', 'dev', '--team', 'acad'])

        assert result.exit_code == 1

    @patch('main.Pythena')
    def test_property_not_found(self, mock_pythena):
        """Test behavior when requested property is not found."""
        mock_pythena_instance = MagicMock()
        mock_pythena_instance.get_properties.return_value = {'other': 'value'}
        mock_pythena_instance.get_property_value.return_value = None
        mock_pythena.return_value = mock_pythena_instance

        runner = click.testing.CliRunner()
        result = runner.invoke(main.main, ['--env', 'dev', '--team', 'acad'])

        # Should still complete successfully (application logic continues)
        assert result.exit_code == 0

    @patch('main.Pythena')
    def test_general_exception_handling(self, mock_pythena):
        """Test that general exceptions are caught and logged properly."""
        mock_pythena.side_effect = RuntimeError("Unexpected error")

        runner = click.testing.CliRunner()
        result = runner.invoke(main.main, ['--env', 'dev', '--team', 'acad'])

        assert result.exit_code == 1

    @patch('main.Pythena')
    def test_import_error_handling(self, mock_pythena):
        """Test behavior when required modules cannot be imported."""
        mock_pythena.side_effect = ImportError("Module not found")

        runner = click.testing.CliRunner()
        result = runner.invoke(main.main, ['--env', 'dev', '--team', 'acad'])

        assert result.exit_code == 1

    @patch('main.Pythena')
    @patch('main.configure_logging')
    @patch('logging.LoggerAdapter')
    def test_error_logging_during_exception(self, mock_adapter, mock_configure_logging, mock_pythena):
        """Test that errors are properly logged when exceptions occur."""
        # Setup mocks
        mock_base_logger = MagicMock()
        mock_configure_logging.return_value = mock_base_logger

        mock_context_logger = MagicMock()
        mock_adapter.return_value = mock_context_logger

        mock_pythena.side_effect = Exception("Test exception")

        runner = click.testing.CliRunner()
        result = runner.invoke(main.main, ['--env', 'dev', '--team', 'acad'])

        assert result.exit_code == 1

        # Verify that exception was logged on the LoggerAdapter
        mock_context_logger.exception.assert_called_once()
        exception_call = mock_context_logger.exception.call_args[0][0]
        assert "Unhandled exception occurred" in exception_call

    @patch('main.Pythena')
    def test_athena_network_error(self, mock_pythena):
        """Test behavior when network errors occur with Athena."""
        mock_pythena.side_effect = ConnectionError("Network unreachable")

        runner = click.testing.CliRunner()
        result = runner.invoke(main.main, ['--env', 'dev', '--team', 'acad'])

        assert result.exit_code == 1

    @patch('main.Pythena')
    def test_athena_properties_empty_dict(self, mock_pythena):
        """Test behavior when Athena returns empty properties dictionary."""
        mock_pythena_instance = MagicMock()
        mock_pythena_instance.get_properties.return_value = {}
        mock_pythena_instance.get_property_value.return_value = None
        mock_pythena.return_value = mock_pythena_instance

        runner = click.testing.CliRunner()
        result = runner.invoke(main.main, ['--env', 'dev', '--team', 'acad'])

        # Should complete successfully even with empty properties
        assert result.exit_code == 0
