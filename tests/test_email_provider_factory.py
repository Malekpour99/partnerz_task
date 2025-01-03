import pytest

from email_service.factory import EmailProviderFactory
from email_service.providers.smtp_provider import SMTPProvider
from email_service.providers.aws_provider import AWSEmailProvider


class TestEmailProviderFactory:
    """Tests for the EmailProviderFactory."""

    def test_create_smtp_provider(self, email_config):
        """Test creation of an SMTPProvider instance."""
        provider = EmailProviderFactory.create("smtp", email_config)
        assert isinstance(provider, SMTPProvider)

    def test_create_aws_provider(self, email_config):
        """Test creation of an AWSEmailProvider instance."""
        provider = EmailProviderFactory.create("aws", email_config, "test-config-set")
        assert isinstance(provider, AWSEmailProvider)
        assert provider.ses_configuration_set == "test-config-set"

    def test_create_invalid_provider(self, email_config):
        """Test error raised for invalid provider type."""
        with pytest.raises(ValueError):
            EmailProviderFactory.create("invalid", email_config)
