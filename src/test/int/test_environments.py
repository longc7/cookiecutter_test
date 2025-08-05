from unittest.mock import MagicMock, patch

import click.testing

import main


class TestEnvironmentSpecificBehavior:
    """Integration tests for environment-specific behavior."""

    @patch('main.Pythena')
    def test_different_environments_use_correct_profiles(self, mock_pythena):
        """Test that different environments create correct Athena profiles."""
        mock_pythena_instance = MagicMock()
        mock_pythena_instance.get_properties.return_value = {'test': 'value'}
        mock_pythena_instance.get_property_value.return_value = 'test_value'
        mock_pythena.return_value = mock_pythena_instance

        runner = click.testing.CliRunner()

        # Test dev environment
        result = runner.invoke(main.main, ['--env', 'dev', '--team', 'acad'])
        assert result.exit_code == 0
        mock_pythena.assert_called_with('test', 'dev', 'acad', 'acad,dev')

        # Reset mock
        mock_pythena.reset_mock()

        # Test UAT environment
        result = runner.invoke(main.main, ['--env', 'uat', '--team', 'ident'])
        assert result.exit_code == 0
        mock_pythena.assert_called_with('test', 'uat', 'ident', 'ident,uat')

        # Reset mock
        mock_pythena.reset_mock()

        # Test production environment
        result = runner.invoke(main.main, ['--env', 'prd', '--team', 'admsol'])
        assert result.exit_code == 0
        mock_pythena.assert_called_with('test', 'prd', 'admsol', 'admsol,prd')

    @patch('main.Pythena')
    def test_environment_profile_construction(self, mock_pythena):
        """Test that profile strings are constructed correctly for each environment."""
        mock_pythena_instance = MagicMock()
        mock_pythena_instance.get_properties.return_value = {'test': 'value'}
        mock_pythena_instance.get_property_value.return_value = 'test_value'
        mock_pythena.return_value = mock_pythena_instance

        runner = click.testing.CliRunner()

        test_cases = [
            ('dev', 'acad', 'acad,dev'),
            ('uat', 'admsol', 'admsol,uat'),
            ('prd', 'ident', 'ident,prd'),
        ]

        for env, team, expected_profile in test_cases:
            mock_pythena.reset_mock()
            result = runner.invoke(main.main, ['--env', env, '--team', team])
            assert result.exit_code == 0

            # Verify the profile parameter is constructed correctly
            mock_pythena.assert_called_once()
            call_args = mock_pythena.call_args[0]
            assert call_args[3] == expected_profile  # profiles parameter

    @patch('main.Pythena')
    @patch('main.configure_logging')
    def test_context_logging_includes_environment_info(self, mock_configure_logging, mock_pythena):
        """Test that logging context includes environment and team information."""
        # Setup mocks
        mock_base_logger = MagicMock()
        mock_configure_logging.return_value = mock_base_logger

        mock_pythena_instance = MagicMock()
        mock_pythena_instance.get_properties.return_value = {'test': 'value'}
        mock_pythena_instance.get_property_value.return_value = 'test_value'
        mock_pythena.return_value = mock_pythena_instance

        with patch('logging.LoggerAdapter') as mock_adapter:
            mock_context_logger = MagicMock()
            mock_adapter.return_value = mock_context_logger

            runner = click.testing.CliRunner()
            result = runner.invoke(main.main, ['--env', 'uat', '--team', 'admsol'])

            assert result.exit_code == 0

            # Verify LoggerAdapter was called with correct context
            mock_adapter.assert_called_once()
            call_args = mock_adapter.call_args
            context = call_args[0][1]  # Second argument is the context dict

            assert context['env'] == 'uat'
            assert context['team'] == 'admsol'
