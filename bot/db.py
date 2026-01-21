from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import sqlite3
from typing import Iterable

from cryptography.fernet import Fernet


@dataclass(frozen=True)
class Secret:
    name: str
    value: str


class Database:
    def __init__(self, path: str, fernet_key: str) -> None:
        self.path = path
        self.fernet = Fernet(fernet_key)

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def init(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS secrets (
                    name TEXT PRIMARY KEY,
                    value BLOB NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    body TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS offers (
                    offer_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    offer_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    sold_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS steam_guard_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    requested_at TEXT NOT NULL
                )
                """
            )

    def store_secret(self, secret: Secret) -> None:
        encrypted = self.fernet.encrypt(secret.value.encode("utf-8"))
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO secrets (name, value)
                VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE SET value = excluded.value
                """,
                (secret.name, encrypted),
            )

    def get_secret(self, name: str) -> str | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT value FROM secrets WHERE name = ?",
                (name,),
            ).fetchone()
        if not row:
            return None
        return self.fernet.decrypt(row[0]).decode("utf-8")

    def log_message(self, chat_id: str, direction: str, body: str) -> None:
        created_at = datetime.utcnow().isoformat()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO messages (chat_id, direction, body, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (chat_id, direction, body, created_at),
            )

    def upsert_offers(self, offers: Iterable[dict]) -> None:
        updated_at = datetime.utcnow().isoformat()
        with self.connect() as conn:
            for offer in offers:
                conn.execute(
                    """
                    INSERT INTO offers (offer_id, title, price, quantity, status, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(offer_id) DO UPDATE SET
                        title = excluded.title,
                        price = excluded.price,
                        quantity = excluded.quantity,
                        status = excluded.status,
                        updated_at = excluded.updated_at
                    """,
                    (
                        offer["offer_id"],
                        offer["title"],
                        offer["price"],
                        offer["quantity"],
                        offer["status"],
                        updated_at,
                    ),
                )

    def last_steam_guard_request(self) -> datetime | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT requested_at FROM steam_guard_requests ORDER BY id DESC LIMIT 1"
            ).fetchone()
        if not row:
            return None
        return datetime.fromisoformat(row[0])

    def log_steam_guard_request(self) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO steam_guard_requests (requested_at) VALUES (?)",
                (datetime.utcnow().isoformat(),),
            )
