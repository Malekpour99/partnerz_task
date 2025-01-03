import pytest
import smtplib
from unittest.mock import Mock, patch

from email_service.exceptions import EmailError
from email_service.providers.aws_provider import AWSEmailProvider


class TestAWSEmailProvider:
    """Tests for the AWSEmailProvider class."""

    @pytest.fixture
    def aws_provider(self, email_config):
        """Fixture for creating an AWSEmailProvider instance."""
        return AWSEmailProvider(email_config, "test-config-set")

    def test_create_mime_message(self, aws_provider, email_message):
        """Test MIME message creation with AWS-specific headers."""
        mime_message = aws_provider._create_mime_message(email_message)
        assert mime_message["X-SES-CONFIGURATION-SET"] == "test-config-set"

    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp, aws_provider, email_message):
        """Test successfully sending an email via AWS."""
        aws_provider._smtp_provider._connection = Mock()
        aws_provider.send(email_message)
        aws_provider._smtp_provider._connection.sendmail.assert_called_once()

    @patch("smtplib.SMTP")
    def test_aws_specific_error_handling(self, mock_smtp, aws_provider, email_message):
        """Test handling AWS-specific errors."""
        aws_provider._smtp_provider._connection = Mock()
        aws_provider._smtp_provider._connection.sendmail.side_effect = (
            smtplib.SMTPException("AWS specific error")
        )

        with pytest.raises(EmailError) as exc_info:
            aws_provider.send(email_message)
        assert "Failed to send email via AWS SES" in str(exc_info.value)
