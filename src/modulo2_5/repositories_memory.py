from __future__ import annotations


from typing import Dict, List, Optional
from models import Message, Sender


class MemoryRepository:

    def __init__(self) -> None:
        self._sender: Dict[str, Sender] = {}
        self._messages: Dict[str, Message] = {}


    # Sender operations
    def add_sender(self, sender: Sender) -> Sender:
        self._sender[sender.id] = sender
        return sender

    def get_sender(self, sender_id: str) -> Optional[Sender]:
        return self._sender.get(sender_id)
        
    def get_sender_by_name(self, sender_name: str) -> Optional[Sender]:
        for sender in self._sender.values():
            if sender.name == sender_name:
                return sender
        return None
        
    def list_senders(self) -> List[Sender]:
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

    def get_message(self, message_id: str) -> Optional[Message]:
        return self._messages.get(message_id)

    def list_messages(self) -> List[Message]:
        return list(self._messages.values())

    def get_messages_by_sender(self, sender_id: str) -> List[Message]:
        return [msg for msg in self._messages.values() if msg.sender_id == sender_id]
        
    def remove_message(self, message_id: str) -> bool:
        if message_id in self._messages:
            del self._messages[message_id]
            return True
        return False


__all__ = ["MemoryRepository"]
