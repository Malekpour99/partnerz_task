from typing import Optional
from dataclasses import dataclass


@dataclass
class EmailConfig:
    username: str
    password: str
    host: str
    port: int
    use_tls: bool = True
    provider: Optional[str] = None
