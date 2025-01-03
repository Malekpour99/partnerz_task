import pytest
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from unittest.mock import Mock, patch, mock_open

from email_service.message import EmailMessage
from email_service.exceptions import EmailError
from email_service.providers.smtp_provider import SMTPProvider


class TestSMTPProvider:
    """Tests for the SMTPProvider class."""

    @pytest.fixture
    def smtp_provider(self, email_config):
        """Fixture for creating an SMTPProvider instance."""
        return SMTPProvider(email_config)

    @patch("smtplib.SMTP")
    def test_connect_success(self, mock_smtp, smtp_provider):
        """Test successful connection to the SMTP server."""
        smtp_provider.connect()
        mock_smtp.assert_called_once_with(
            smtp_provider.config.host, smtp_provider.config.port
        )
        mock_smtp.return_value.starttls.assert_called_once()
        mock_smtp.return_value.login.assert_called_once_with(
            smtp_provider.config.username, smtp_provider.config.password
        )

    @patch("smtplib.SMTP")
    def test_connect_failure(self, mock_smtp, smtp_provider):
        """Test failure to connect to the SMTP server."""
        mock_smtp.side_effect = smtplib.SMTPException("Connection failed")
        with pytest.raises(EmailError):
            smtp_provider.connect()

    def test_disconnect(self, smtp_provider):
        """Test disconnecting from the SMTP server."""
        smtp_provider._connection = Mock()
        smtp_provider.disconnect()
        assert smtp_provider._connection is None

    @patch("pathlib.Path.open", mock_open(read_data=b"test data"))
    def test_add_attachment(self, smtp_provider):
        """Test adding an attachment to an email."""
        mime_message = MIMEMultipart()
        smtp_provider._add_attachment(
            mime_message, Path("./tests/test.txt"), "test.txt"
        )
        assert len(mime_message.get_payload()) == 1

    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp, smtp_provider, email_message):
        """Test successfully sending an email."""
        smtp_provider._connection = Mock()
        smtp_provider.send(email_message)
        smtp_provider._connection.sendmail.assert_called_once()

    @patch("smtplib.SMTP")
    def test_send_email_retry(self, mock_smtp, smtp_provider, email_message):
        """Test retrying email send after a temporary failure."""
        smtp_provider._connection = Mock()
        smtp_provider._connection.sendmail.side_effect = [
            smtplib.SMTPResponseException(454, "Temporary failure"),
            None,
        ]
        smtp_provider.send(email_message)
        assert smtp_provider._connection.sendmail.call_count == 2

    @patch("smtplib.SMTP")
    def test_send_email_no_recipients(self, mock_smtp, smtp_provider):
        """Test error raised when no recipients are provided."""
        message = EmailMessage(
            subject="Test",
            recipients=[],
            html_content="test",
            sender="test@example.com",
        )
        with pytest.raises(EmailError):
            smtp_provider.send(message)
