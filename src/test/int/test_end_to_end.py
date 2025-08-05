import os
from unittest.mock import MagicMock, patch

import click.testing

import main


class TestEndToEndExecution:
    """Integration tests for the complete application flow."""

    @patch("main.Pythena")
    @patch.dict(os.environ, {"ATHENA_SECRET": "test-secret"})
    def test_complete_application_flow_dev(self, mock_pythena):
        """Test complete application execution in dev environment."""
        # Setup mock Pythena
        mock_pythena_instance = MagicMock()
        mock_pythena_instance.get_properties.return_value = {
            "database.url": "dev-db-url",
            "api.endpoint": "dev-api-endpoint",
        }
        mock_pythena_instance.get_property_value.return_value = "dev-property-value"
        mock_pythena.return_value = mock_pythena_instance

        # Run the application
        runner = click.testing.CliRunner()
        result = runner.invoke(main.main, ["--env", "dev", "--team", "acad"])

        # Verify execution
        assert result.exit_code == 0
        mock_pythena.assert_called_once_with(
            "test", "dev", "acad", "acad,dev"
        )
        mock_pythena_instance.get_properties.assert_called_once()
        mock_pythena_instance.get_property_value.assert_called_once()

    @patch("main.Pythena")
    @patch.dict(os.environ, {"ATHENA_SECRET": "test-secret"})
    def test_complete_application_flow_production(self, mock_pythena):
        """Test complete application execution in production environment."""
        # Setup mock Pythena for production
        mock_pythena_instance = MagicMock()
        mock_pythena_instance.get_properties.return_value = {
            "database.url": "prd-db-url",
            "api.endpoint": "prd-api-endpoint",
        }
        mock_pythena_instance.get_property_value.return_value = "prd-property-value"
        mock_pythena.return_value = mock_pythena_instance

        # Run the application
        runner = click.testing.CliRunner()
        result = runner.invoke(main.main, ["--env", "prd", "--team", "admsol"])

        # Verify execution
        assert result.exit_code == 0
        mock_pythena.assert_called_once_with(
            "test", "prd", "admsol", "admsol,prd"
        )

    @patch("main.Pythena")
    def test_application_flow_without_athena_secret(self, mock_pythena):
        """Test application behavior when ATHENA_SECRET is not set."""
        # Ensure ATHENA_SECRET is not in environment
        with patch.dict(os.environ, {}, clear=True):
            mock_pythena_instance = MagicMock()
            mock_pythena_instance.get_properties.return_value = None
            mock_pythena.return_value = mock_pythena_instance

            runner = click.testing.CliRunner()
            result = runner.invoke(main.main, ["--env", "dev", "--team", "acad"])

            # Should exit with error code 1
            assert result.exit_code == 1
