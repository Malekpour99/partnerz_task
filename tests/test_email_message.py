import pytest

from email_service.message import EmailMessage


class TestEmailMessage:
    """Tests for the EmailMessage class."""

    def test_create_email_message(self, email_message):
        """Test successful creation of an email message."""
        assert email_message.subject == "Test Subject"
        assert email_message.recipients == ["recipient@example.com"]
        assert email_message.html_content == "<p>Test content</p>"
        assert email_message.sender == "sender@example.com"
        assert email_message.metadata == {"campaign": "test"}

    def test_invalid_metadata(self):
        """Test handling of invalid metadata."""
        with pytest.raises(ValueError):
            EmailMessage(
                subject="Test",
                recipients=["test@example.com"],
                html_content="test",
                sender="test@example.com",
                metadata="invalid",  # Should be a dict
            )

    def test_get_sanitized_metadata_headers(self, email_message):
        """Test metadata header sanitization."""
        headers = email_message.get_sanitized_metadata_headers()
        assert headers["X-Metadata-campaign"] == "test"

    def test_metadata_header_sanitization(self):
        """Test sanitization of metadata keys and values."""
        message = EmailMessage(
            subject="Test",
            recipients=["test@example.com"],
            html_content="test",
            sender="test@example.com",
            metadata={"key with spaces": "value\nwith\nnewlines"},
        )
        headers = message.get_sanitized_metadata_headers()
        assert "X-Metadata-key-with-spaces" in headers
        assert "\n" not in headers["X-Metadata-key-with-spaces"]
