import os
from unittest.mock import patch

import pytest

from merkato.util import load_config


class TestUtil:
    @patch.dict(
        os.environ,
        {
            "EMAIL_SENDER": "test@example.com",
            "EMAIL_PASSWORD": "password123",
            "EMAIL_RECIPIENT": "recipient@example.com",
            "EMAIL_SMTP_SERVER": "smtp.example.com",
            "EMAIL_SMTP_PORT": "587",
        },
    )
    @patch("merkato.util.load_dotenv")  # Mock load_dotenv to prevent it from actually loading .env
    def test_load_config(self, mock_load_dotenv):  # Add parameter to receive the mock
        """Test loading configuration with all required env vars"""
        config = load_config()

        assert config["email"]["sender"] == "test@example.com"
        assert config["email"]["password"] == "password123"
        assert config["email"]["recipient"] == "recipient@example.com"
        assert config["email"]["smtp_server"] == "smtp.example.com"
        assert config["email"]["smtp_port"] == 587

    @patch.dict(
        os.environ,
        {
            "EMAIL_SENDER": "test@example.com",
            # Missing other required env vars
        },
    )
    @patch("merkato.util.load_dotenv")
    def test_load_config_missing_env_vars(self, mock_load_dotenv):  # Add parameter here too
        """Test that load_config raises ValueError when env vars are missing"""

        with pytest.raises(ValueError, match="Email configuration environment variables are not fully set"):
            load_config()
