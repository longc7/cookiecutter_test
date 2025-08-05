import os
import tempfile
from unittest.mock import patch

import yaml

import main


class TestConfigureLogging:
    """Test the logging configuration functionality."""

    def test_configure_logging_with_default_config(self):
        """Test that configure_logging works with default configuration."""
        with patch('main.get_log_config_path') as mock_get_path:
            mock_get_path.return_value = {
                'version': 1,
                'handlers': {'console': {'class': 'logging.StreamHandler'}},
                'loggers': {'test': {'level': 'INFO'}}
            }

            logger = main.configure_logging()

            assert logger is not None
            assert logger.name == 'test'

    def test_configure_logging_with_file_config(self):
        """Test that configure_logging works with a YAML file."""
        test_config = {
            'version': 1,
            'handlers': {'console': {'class': 'logging.StreamHandler'}},
            'loggers': {'test': {'level': 'DEBUG'}}
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_file = f.name

        try:
            with patch('main.get_log_config_path') as mock_get_path:
                mock_get_path.return_value = temp_file

                logger = main.configure_logging()

                assert logger is not None
                assert logger.name == 'test'
        finally:
            os.unlink(temp_file)

    def test_configure_logging_fallback_on_error(self):
        """Test that configure_logging falls back to basic config on error."""
        with patch('main.get_log_config_path') as mock_get_path:
            mock_get_path.return_value = '/nonexistent/file.yaml'

            with patch('logging.basicConfig') as mock_basic_config:
                logger = main.configure_logging()

                mock_basic_config.assert_called_once()
                assert logger.name == 'test'


class TestGetLogConfigPath:
    """Test the log configuration path resolution."""

    def test_environment_variable_takes_precedence(self):
        """Test that LOG_CONFIG_PATH environment variable is used first."""
        with patch.dict(os.environ, {'LOG_CONFIG_PATH': '/custom/path.yaml'}):
            result = main.get_log_config_path()
            assert result == '/custom/path.yaml'

    def test_local_file_used_when_exists(self):
        """Test that local log-config.yaml is used when it exists."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('os.path.exists') as mock_exists:
                mock_exists.side_effect = lambda path: path == './log-config.yaml'

                result = main.get_log_config_path()
                assert result == './log-config.yaml'

    def test_docker_path_used_when_exists(self):
        """Test that docker path is used when local file doesn't exist."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('os.path.exists') as mock_exists:
                mock_exists.side_effect = lambda path: path == '/ext-vol/app-conf/logging/log-config.yaml'

                result = main.get_log_config_path()
                assert result == '/ext-vol/app-conf/logging/log-config.yaml'

    def test_default_config_returned_when_no_files_exist(self):
        """Test that default config dict is returned when no files exist."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('os.path.exists', return_value=False):
                result = main.get_log_config_path()

                assert isinstance(result, dict)
                assert 'version' in result
                assert 'handlers' in result
                assert 'loggers' in result
