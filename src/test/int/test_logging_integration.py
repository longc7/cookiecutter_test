import logging
import os
import tempfile
from unittest.mock import MagicMock, patch

import click.testing
import yaml

import main


class TestLoggingIntegration:
    """Integration tests for logging functionality."""

    def test_logging_with_local_config_file(self):
        """Test that logging works with a local config file."""
        # Create a temporary log config file
        test_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'simple': {
                    'format': '%(asctime)s %(levelname)-8s [%(filename)s %(lineno)d] : %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'INFO',
                    'formatter': 'simple',
                    'stream': 'ext://sys.stdout'
                }
            },
            'loggers': {
                'test': {
                    'level': 'INFO',
                    'handlers': ['console'],
                    'propagate': False
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_file = f.name

        try:
            with patch.dict(os.environ, {'LOG_CONFIG_PATH': temp_file}):
                logger = main.configure_logging()

                # Test that we can log messages
                logger.info("Test message")
                logger.error("Test error message")

                assert logger.name == 'test'
                assert logger.level <= logging.INFO
        finally:
            os.unlink(temp_file)

    @patch('main.Pythena')
    def test_logging_output_during_execution(self, mock_pythena):
        """Test that log messages are generated during application execution."""
        # Setup mock
        mock_pythena_instance = MagicMock()
        mock_pythena_instance.get_properties.return_value = {'test': 'value'}
        mock_pythena_instance.get_property_value.return_value = 'test_value'
        mock_pythena.return_value = mock_pythena_instance

        # Capture logging output through LoggerAdapter
        with patch('main.configure_logging') as mock_configure_logging:
            with patch('logging.LoggerAdapter') as mock_adapter:
                mock_base_logger = MagicMock()
                mock_configure_logging.return_value = mock_base_logger

                mock_context_logger = MagicMock()
                mock_adapter.return_value = mock_context_logger

                runner = click.testing.CliRunner()
                result = runner.invoke(main.main, ['--env', 'dev', '--team', 'acad'])

                assert result.exit_code == 0

                # Verify logging calls were made on the LoggerAdapter
                assert mock_context_logger.info.call_count >= 2  # Starting and finished messages

                # Check for specific log messages
                log_calls = [call[0][0] for call in mock_context_logger.info.call_args_list]
                assert any('Starting test' in msg for msg in log_calls)
                assert any('Finished test' in msg for msg in log_calls)

    @patch('main.configure_logging')
    @patch('main.Pythena')
    def test_logging_handler_cleanup(self, mock_pythena, mock_configure_logging):
        """Test that logging handlers are properly cleaned up."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_handler = MagicMock()
        mock_logger.handlers = [mock_handler]
        mock_configure_logging.return_value = mock_logger

        mock_pythena_instance = MagicMock()
        mock_pythena_instance.get_properties.return_value = {'test': 'value'}
        mock_pythena_instance.get_property_value.return_value = 'test_value'
        mock_pythena.return_value = mock_pythena_instance

        # Mock the root logger handlers
        with patch('logging.root.handlers', [mock_handler]):
            with patch('logging.getLogger') as mock_get_logger:
                mock_app_logger = MagicMock()
                mock_app_logger.handlers = [mock_handler]
                mock_get_logger.return_value = mock_app_logger

                runner = click.testing.CliRunner()
                result = runner.invoke(main.main, ['--env', 'dev', '--team', 'acad'])

                assert result.exit_code == 0

                # Verify handlers were flushed and closed
                assert mock_handler.flush.call_count >= 2  # Called for both root and app logger
                assert mock_handler.close.call_count >= 2
