from abc import ABC, abstractmethod

from email_service.message import EmailMessage


class EmailProvider(ABC):
    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def send(self, message: EmailMessage) -> None:
        pass
