from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from typing import runtime_checkable

from models import Message
from models import Sender
from repositories import SqliteRepository
from repositories_memory import MemoryRepository

repo = SqliteRepository()


@runtime_checkable
class Repository(Protocol):
    def save_message(self, sender_name: str, recipient: str, content: str) -> None: ...


class Repository_sqlite:
    def __init__(self, sqlite_repo: SqliteRepository) -> None:
        self._sqlite_repo = sqlite_repo

    def save_message(self, sender_name: str, recipient: str, content: str) -> None:
        sender = self._sqlite_repo.get_sender_by_name(sender_name)
        print("Sender:", sender)
        if sender is None:
            sender = Sender(name=sender_name, channel=sender_name, contact=recipient)
            sender = self._sqlite_repo.add_sender(sender)
        self._sqlite_repo.add_message(
            Message(sender_id=sender.id, recipient=recipient, content=content),
        )
        print(f"Message saved on Sqlite: {content}")


class Repository_memory:
    def __init__(self, memory_repository: MemoryRepository) -> None:
        self._memory_repo = memory_repository

    def save_message(self, sender_name: str, recipient: str, content: str) -> None:
        sender = self._memory_repo.get_sender_by_name(sender_name)
        print("Sender:", sender)
        if sender is None:
            sender = Sender(name=sender_name, channel=sender_name, contact=recipient)
            sender = self._memory_repo.add_sender(sender)
        self._memory_repo.add_message(
            Message(sender_id=sender.id, recipient=recipient, content=content),
        )
        print(f"Message saved on Memory: {content}")


@runtime_checkable
class MessageSender(Protocol):
    print("MessageSender.")

    def send(self, recipient: str, message: str) -> None: ...


class EmailSender:
    print("EmailSender.")

    def __init__(self, smtp_client: object | None = None) -> None:
        self._smtp_client = smtp_client

    def send(self, recipient: str, message: str) -> None:
        if self._smtp_client is None:
            print(f"[Email] To: {self._smtp_client} | {message}")
            return
        print(f"[Email2] To: {self._smtp_client} | {message}")
        self._smtp_client.send(recipient, message)


class SmsSender:
    print("SmsSender.")

    def __init__(self, sms_client: object | None = None) -> None:
        self._sms_client = sms_client

    def send(self, recipient: str, message: str) -> None:
        if self._sms_client is None:
            print(f"[SMS] To: {recipient} | {message}")
            return

        self._sms_client.send(recipient, message)


class SlackSender:
    print("SlackSender.")

    def __init__(self, slack_client: object | None = None) -> None:
        self._slack_client = slack_client

    def send(self, recipient: str, message: str) -> None:
        if self._slack_client is None:
            print(f"[Slack] Channel: {recipient} | {message}")
            return

        self._slack_client.send(recipient, message)


@dataclass(frozen=True)
class Notification:
    recipient: str
    message: str


class NotificationService:
    print("NotificationService")

    def __init__(self, sender: MessageSender) -> None:
        self._sender = sender

    def send(self, notification: Notification) -> None:
        self._sender.send(notification.recipient, notification.message)


class SenderFactory:
    print("SenderFactory.")

    def create(self, channel: str, **kwargs: object) -> MessageSender:
        if channel == "email":
            return EmailSender(kwargs.get("smtp_client"))
        if channel == "sms":
            return SmsSender(kwargs.get("sms_client"))
        if channel == "slack":
            return SlackSender(kwargs.get("slack_client"))

        raise ValueError(f"Unsupported channel: {channel}")


class SenderProvider:
    print("SenderProvider.")

    def __init__(self, factory: SenderFactory, default_channel: str = "email") -> None:
        self._factory = factory
        self._default_channel = default_channel

    def get_sender(self, channel: str | None = None, **kwargs: object) -> MessageSender:
        selected_channel = channel or self._default_channel
        return self._factory.create(selected_channel, **kwargs)


class NotificationApp:
    print("NotificationApp.")

    def __init__(self, provider: SenderProvider) -> None:
        self._provider = provider

    def dispatch(
        self,
        repo: Repository,
        channel: str,
        recipient: str,
        message: str,
    ) -> None:
        sender = self._provider.get_sender(channel)
        service = NotificationService(sender)
        service.send(Notification(recipient=recipient, message=message))
        repo.save_message(sender_name=channel, recipient=recipient, content=message)
        print(f"Notification sent via {channel} to {recipient}: {message}")


def main() -> None:
    print("main function.")
    factory = SenderFactory()
    provider = SenderProvider(factory)

    app = NotificationApp(provider)
    repo = Repository_sqlite(SqliteRepository())
    print("Dispatching notifications through different channels with SqliteRepository:")
    app.dispatch(repo, "email", "mmarquez@email.com", "Hello via Email!")
    app.dispatch(repo, "sms", "+1234567890", "Hello via SMS!")
    app.dispatch(repo, "slack", "#general", "Hello via Slack!")

    repo = Repository_memory(MemoryRepository())
    print("Dispatching notifications through different channels with MemoryRepository:")
    app.dispatch(repo, "email", "mmarquez@email.com", "Hello via Email!")
    app.dispatch(repo, "sms", "+1234567890", "Hello via SMS!")
    app.dispatch(repo, "slack", "#general", "Hello via Slack!")


if __name__ == "__main__":
    main()

__all__ = [
    "EmailSender",
    "MessageSender",
    "Notification",
    "NotificationApp",
    "NotificationService",
    "SenderFactory",
    "SenderProvider",
    "SlackSender",
    "SmsSender",
    "main",
]
