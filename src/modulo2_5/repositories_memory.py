from __future__ import annotations

from models import Message
from models import Sender


class MemoryRepository:
    def __init__(self) -> None:
        self._sender: dict[str, Sender] = {}
        self._messages: dict[str, Message] = {}

    # Sender operations

    def add_sender(self, sender: Sender) -> Sender:
        self._sender[sender.id] = sender
        return sender

    def get_sender(self, sender_id: str) -> Sender | None:
        return self._sender.get(sender_id)

    def get_sender_by_name(self, sender_name: str) -> Sender | None:
        for sender in self._sender.values():
            if sender.name == sender_name:
                return sender
        return None

    def list_senders(self) -> list[Sender]:
        return list(self._sender.values())

    def remove_sender(self, sender_id: str) -> bool:
        if sender_id in self._sender:
            del self._sender[sender_id]
            return True
        return False

    # Message operations
    def add_message(self, message: Message) -> Message:
        self._messages[message.id] = message
        return message

    def get_message(self, message_id: str) -> Message | None:
        return self._messages.get(message_id)

    def list_messages(self) -> list[Message]:
        return list(self._messages.values())

    def get_messages_by_sender(self, sender_id: str) -> list[Message]:
        return [msg for msg in self._messages.values() if msg.sender_id == sender_id]

    def remove_message(self, message_id: str) -> bool:
        if message_id in self._messages:
            del self._messages[message_id]
            return True
        return False


__all__ = ["MemoryRepository"]
