from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class EmailMessage:
    subject: str
    recipients: List[str]
    html_content: str
    sender: str
    attachment_path: Optional[Path] = None
    attachment_name: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        self.metadata = self.metadata or {}

        if not isinstance(self.metadata, dict):
            raise ValueError("Metadata must be a dictionary")

    def get_sanitized_metadata_headers(self) -> Dict[str, str]:
        """
        Returns metadata as sanitized email headers.
        Converts metadata to X-Metadata-* headers with sanitized values.
        """
        headers = {}
        for key, value in self.metadata.items():
            # Sanitize header key and value
            header_key = f"X-Metadata-{key}".replace(" ", "-")
            header_value = str(value).replace("\n", " ")
            headers[header_key] = header_value
        return headers
