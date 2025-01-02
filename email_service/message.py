from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class EmailMessage:
    subject: str
    recipients: List[str]
    html_content: str
    sender: str
    attachment_path: Optional[Path] = None
    attachment_name: Optional[str] = None
    metadata: List[str] = None

    def __post_init__(self):
        self.metadata = self.metadata or []
