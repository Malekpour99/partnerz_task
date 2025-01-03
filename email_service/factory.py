from typing import Dict, Type, Optional

from .config import EmailConfig
from .interfaces import EmailProvider
from .providers.smtp_provider import SMTPProvider
from .providers.aws_provider import AWSEmailProvider


class EmailProviderFactory:
    _providers: Dict[str, Type[EmailProvider]] = {
        "smtp": SMTPProvider,
        "aws": AWSEmailProvider,
    }

    @classmethod
    def create(
        cls,
        provider_type: str,
        config: EmailConfig,
        ses_configuration_set: Optional[str] = None,
    ) -> EmailProvider:
        """
        Create an email provider instance.

        Args:
            provider_type: Type of provider ('smtp' or 'aws')
            config: Email configuration
            ses_configuration_set: Optional AWS SES configuration set
        """
        provider_class = cls._providers.get(provider_type.lower())
        if not provider_class:
            raise ValueError(f"Unsupported provider type: {provider_type}")

        if provider_type.lower() == "aws":
            return provider_class(config, ses_configuration_set)
        # smtp provider
        return provider_class(config)
