from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Sender:
    """Represents a message sender (an origin)."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    channel: str = ""  # e.g. 'email', 'sms', 'slack'
    contact: str = ""  # e.g. email address, phone number, slack channel


@dataclass
class Message:
    """Represents a single message sent by a Sender."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    recipient: str = ""
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


__all__ = ["Sender", "Message"]
