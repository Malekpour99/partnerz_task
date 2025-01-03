import pytest

from email_service.config import EmailConfig
from email_service.message import EmailMessage


@pytest.fixture
def email_config():
    """Fixture for creating a sample email configuration."""
    return EmailConfig(
        username="test@example.com",
        password="password123",
        host="smtp.example.com",
        port=587,
        use_tls=True,
    )


@pytest.fixture
def email_message():
    """Fixture for creating a sample email message."""
    return EmailMessage(
        subject="Test Subject",
        recipients=["recipient@example.com"],
        html_content="<p>Test content</p>",
        sender="sender@example.com",
        metadata={"campaign": "test"},
    )
