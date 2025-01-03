import smtplib
from time import sleep
from typing import Optional
from email.mime.multipart import MIMEMultipart

from ..config import EmailConfig
from ..message import EmailMessage
from ..exceptions import EmailError
from ..interfaces import EmailProvider
from .smtp_provider import SMTPProvider


class AWSEmailProvider(EmailProvider):
    """AWS SES-specific email provider"""

    def __init__(
        self, config: EmailConfig, ses_configuration_set: Optional[str] = None
    ):
        super().__init__(config)
        self.ses_configuration_set = ses_configuration_set
        self._smtp_provider = SMTPProvider(config)

    def connect(self) -> None:
        """Connect using underlying SMTP provider"""
        self._smtp_provider.connect()

    def disconnect(self) -> None:
        """Disconnect underlying SMTP provider"""
        self._smtp_provider.disconnect()

    def _create_mime_message(self, email_message: EmailMessage) -> MIMEMultipart:
        """Create MIME message with AWS SES specific headers"""
        mime_message = self._smtp_provider._create_mime_message(email_message)

        # Add AWS SES specific headers
        if self.ses_configuration_set:
            mime_message["X-SES-CONFIGURATION-SET"] = self.ses_configuration_set

        return mime_message

    def send(self, message: EmailMessage) -> None:
        """Send email using AWS SES"""
        if not self._smtp_provider._connection:
            self.connect()

        mime_message = self._create_mime_message(message)

        retries = 0
        while retries <= self._smtp_provider._max_retries:
            try:
                self._smtp_provider._connection.sendmail(
                    message.sender,
                    message.recipients,
                    mime_message.as_string(),
                )
                return
            except smtplib.SMTPResponseException as e:
                # SMTP 454 - Temporary Authentication Issue
                if e.smtp_code == 454 and retries < self._smtp_provider._max_retries:
                    retries += 1
                    sleep(self._smtp_provider._retry_delay)
                    continue
                raise EmailError(f"Failed to send email via AWS SES: {str(e)}")
            except smtplib.SMTPException as e:
                raise EmailError(f"Failed to send email via AWS SES: {str(e)}")
