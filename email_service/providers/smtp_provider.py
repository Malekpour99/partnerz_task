import smtplib
from time import sleep
from pathlib import Path
from typing import Optional
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from ..interfaces import EmailProvider
from ..config import EmailConfig
from ..message import EmailMessage
from ..exceptions import EmailError

class SMTPProvider(EmailProvider):
    def __init__(self, config: EmailConfig):
        self.config = config
        self._connection = None
        self._max_retries = 2
        self._retry_delay = 1  # seconds

    def connect(self) -> None:
        """Establish SMTP connection"""
        try:
            self._connection = smtplib.SMTP(self.config.host, self.config.port)
            if self.config.use_tls:
                self._connection.starttls()
            self._connection.login(self.config.username, self.config.password)
        except smtplib.SMTPException as e:
            raise EmailError(f"Failed to connect to SMTP server: {str(e)}")

    def disconnect(self) -> None:
        """Close SMTP connection"""
        if self._connection:
            try:
                self._connection.quit()
            except smtplib.SMTPException:
                pass
            finally:
                self._connection = None

    def _create_mime_message(self, email_message: EmailMessage) -> MIMEMultipart:
        """Create MIME message with all components"""
        mime_message = MIMEMultipart()
        mime_message['Subject'] = Header(email_message.subject, 'utf-8')
        mime_message['From'] = email_message.sender
        mime_message['To'] = email_message.recipients[0]  # We'll handle multiple recipients in send()

        # Attach HTML content
        html_part = MIMEText(email_message.html_content.encode('utf-8'), 'html', 'utf-8')
        mime_message.attach(html_part)

        # Add attachment if provided
        if email_message.attachment_path:
            self._add_attachment(mime_message, email_message.attachment_path, email_message.attachment_name)

        return mime_message

    def _add_attachment(self, mime_message: MIMEMultipart, filepath: Path, filename: Optional[str]) -> None:
        """Add attachment to MIME message"""
        try:
            with open(filepath, 'rb') as f:
                attachment = MIMEApplication(f.read())
                attachment.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=filename or filepath.name
                )
                mime_message.attach(attachment)
        except IOError as e:
            raise EmailError(f"Failed to attach file: {str(e)}")

    def send(self, message: EmailMessage) -> None:
        """Send email message with retry logic"""
        if not self._connection:
            self.connect()

        mime_message = self._create_mime_message(message)
        
        retries = 0
        while retries <= self._max_retries:
            try:
                self._connection.sendmail(
                    message.sender,
                    message.recipients,
                    mime_message.as_string()
                )
                return
            except smtplib.SMTPResponseException as e:
                if e.smtp_code == 454 and retries < self._max_retries:
                    retries += 1
                    sleep(self._retry_delay)
                    continue
                raise EmailError(f"Failed to send email: {str(e)}")
            except smtplib.SMTPException as e:
                raise EmailError(f"Failed to send email: {str(e)}")