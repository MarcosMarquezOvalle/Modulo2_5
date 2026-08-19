from __future__ import annotations

import sqlite3
from datetime import datetime
from threading import Lock

from models import Message
from models import Sender


class SqliteRepository:
    """SQLite-backed repository for senders and messages.

    This creates two tables:
      - senders(id TEXT PRIMARY KEY, name TEXT, channel TEXT, contact TEXT)
      - messages(id TEXT PRIMARY KEY, sender_id TEXT, recipient TEXT, content TEXT, timestamp TEXT,
                 FOREIGN KEY(sender_id) REFERENCES senders(id) ON DELETE CASCADE)

    By default uses an on-disk file path; pass db_path=':memory:' for in-memory SQLite.
    The class is thread-safe via an internal Lock and a single sqlite3.Connection opened with
    check_same_thread=False.
    """

    def __init__(self, db_path: str = "messages.db") -> None:
        self._lock = Lock()
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        # Enable foreign keys
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        with self._lock, self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS senders (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    contact TEXT NOT NULL
                )
                """,
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    sender_id TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(sender_id) REFERENCES senders(id) ON DELETE CASCADE
                )
                """,
            )

    # Sender operations
    def add_sender(self, sender: Sender) -> Sender:
        with self._lock, self._conn:
            self._conn.execute(
                "REPLACE INTO senders (id, name, channel, contact) VALUES (?, ?, ?, ?)",
                (sender.id, sender.name, sender.channel, sender.contact),
            )
        return sender

    def get_sender(self, sender_id: str) -> Sender | None:
        cur = self._conn.execute(
            "SELECT id, name, channel, contact FROM senders WHERE id = ?",
            (sender_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        return Sender(
            id=row["id"],
            name=row["name"],
            channel=row["channel"],
            contact=row["contact"],
        )

    def get_sender_by_name(self, sender_name: str) -> Sender | None:
        cur = self._conn.execute(
            "SELECT id, name, channel, contact FROM senders WHERE name = ?",
            (sender_name,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        return Sender(
            id=row["id"],
            name=row["name"],
            channel=row["channel"],
            contact=row["contact"],
        )

    def list_senders(self) -> list[Sender]:
        cur = self._conn.execute(
            "SELECT id, name, channel, contact FROM senders ORDER BY name",
        )
        return [
            Sender(
                id=r["id"],
                name=r["name"],
                channel=r["channel"],
                contact=r["contact"],
            )
            for r in cur.fetchall()
        ]

    def remove_sender(self, sender_id: str) -> bool:
        with self._lock, self._conn:
            cur = self._conn.execute("DELETE FROM senders WHERE id = ?", (sender_id,))
            return cur.rowcount > 0

    # Message operations
    def add_message(self, message: Message) -> Message:
        ts = (
            message.timestamp.isoformat()
            if isinstance(message.timestamp, datetime)
            else str(message.timestamp)
        )
        with self._lock, self._conn:
            self._conn.execute(
                "REPLACE INTO messages (id, sender_id, recipient, content, timestamp) VALUES (?, ?, ?, ?, ?)",
                (message.id, message.sender_id, message.recipient, message.content, ts),
            )
        return message

    def get_message(self, message_id: str) -> Message | None:
        cur = self._conn.execute(
            "SELECT id, sender_id, recipient, content, timestamp FROM messages WHERE id = ?",
            (message_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        ts = (
            datetime.fromisoformat(row["timestamp"])
            if row["timestamp"]
            else datetime.utcnow()
        )
        return Message(
            id=row["id"],
            sender_id=row["sender_id"],
            recipient=row["recipient"],
            content=row["content"],
            timestamp=ts,
        )

    def list_messages(self) -> list[Message]:
        cur = self._conn.execute(
            "SELECT id, sender_id, recipient, content, timestamp FROM messages ORDER BY timestamp DESC",
        )
        rows = cur.fetchall()
        messages: list[Message] = []
        for r in rows:
            ts = (
                datetime.fromisoformat(r["timestamp"])
                if r["timestamp"]
                else datetime.utcnow()
            )
            messages.append(
                Message(
                    id=r["id"],
                    sender_id=r["sender_id"],
                    recipient=r["recipient"],
                    content=r["content"],
                    timestamp=ts,
                ),
            )
        return messages

    def get_messages_by_sender(self, sender_id: str) -> list[Message]:
        cur = self._conn.execute(
            "SELECT id, sender_id, recipient, content, timestamp FROM messages WHERE sender_id = ? ORDER BY timestamp DESC",
            (sender_id,),
        )
        rows = cur.fetchall()
        messages: list[Message] = []
        for r in rows:
            ts = (
                datetime.fromisoformat(r["timestamp"])
                if r["timestamp"]
                else datetime.utcnow()
            )
            messages.append(
                Message(
                    id=r["id"],
                    sender_id=r["sender_id"],
                    recipient=r["recipient"],
                    content=r["content"],
                    timestamp=ts,
                ),
            )
        return messages

    def remove_message(self, message_id: str) -> bool:
        with self._lock, self._conn:
            cur = self._conn.execute("DELETE FROM messages WHERE id = ?", (message_id,))
            return cur.rowcount > 0

    def close(self) -> None:
        try:
            self._conn.close()
        finally:
            pass


__all__ = ["SqliteRepository"]
