from typing import Dict, Type

from .config import EmailConfig
from .interfaces import EmailProvider
from .providers.smtp_provider import SMTPProvider


class EmailProviderFactory:
    _providers: Dict[str, Type[EmailProvider]] = {
        "smtp": SMTPProvider,
    }

    @classmethod
    def create(cls, provider_type: str, config: EmailConfig) -> EmailProvider:
        provider_class = cls._providers.get(provider_type.lower())
        if not provider_class:
            raise ValueError(f"Unsupported provider type: {provider_type}")
        return provider_class(config)
