from unittest.mock import MagicMock, patch

import click.testing

import main


class TestCliArguments:
    """Test CLI argument validation."""

    def test_env_argument_validation(self):
        """Test that env argument only accepts valid values."""
        runner = click.testing.CliRunner()
        result = runner.invoke(main.main, ['--env', 'invalid', '--team', 'acad'])

        assert result.exit_code != 0
        assert 'Invalid value' in result.output

    def test_team_argument_validation(self):
        """Test that team argument only accepts valid values."""
        runner = click.testing.CliRunner()
        result = runner.invoke(main.main, ['--env', 'dev', '--team', 'invalid'])

        assert result.exit_code != 0
        assert 'Invalid value' in result.output

    def test_team_argument_required(self):
        """Test that team argument is required."""
        runner = click.testing.CliRunner()
        result = runner.invoke(main.main, ['--env', 'dev'])

        assert result.exit_code != 0
        assert 'Missing option' in result.output or 'required' in result.output.lower()

    def test_env_argument_defaults_to_dev(self):
        """Test that env argument defaults to dev when not specified."""
        # We can't easily test the default from help output, so test actual behavior
        with patch('main.Pythena') as mock_pythena:
            mock_pythena_instance = MagicMock()
            mock_pythena_instance.get_properties.return_value = {'test': 'value'}
            mock_pythena_instance.get_property_value.return_value = 'test_value'
            mock_pythena.return_value = mock_pythena_instance

            runner = click.testing.CliRunner()
            runner.invoke(main.main, ['--team', 'acad'])

            # Should call Pythena with 'dev' as the environment when not specified
            mock_pythena.assert_called_once_with('test', 'dev', 'acad', 'acad,dev')

    def test_all_valid_env_values_accepted(self):
        """Test that all valid environment values are accepted."""
        runner = click.testing.CliRunner()

        # Test each valid environment (we'll get Athena errors but CLI parsing should work)
        for env in ['dev', 'uat', 'prd']:
            result = runner.invoke(main.main, ['--env', env, '--team', 'acad'])
            # Should not be a CLI argument error (exit code 2)
            assert result.exit_code != 2

    def test_all_valid_team_values_accepted(self):
        """Test that all valid team values are accepted."""
        runner = click.testing.CliRunner()

        # Test each valid team (we'll get Athena errors but CLI parsing should work)
        for team in ['acad', 'admsol', 'ident']:
            result = runner.invoke(main.main, ['--env', 'dev', '--team', team])
            # Should not be a CLI argument error (exit code 2)
            assert result.exit_code != 2
