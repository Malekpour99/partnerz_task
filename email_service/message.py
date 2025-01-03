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
