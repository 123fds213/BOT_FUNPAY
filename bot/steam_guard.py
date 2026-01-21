from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from pathlib import Path

from bot.db import Database


@dataclass(frozen=True)
class SteamGuardConfig:
    mafile_path: str
    min_interval_minutes: int = 5


class SteamGuardService:
    def __init__(self, config: SteamGuardConfig, db: Database) -> None:
        self.config = config
        self.db = db

    def _load_mafile(self) -> dict:
        path = Path(self.config.mafile_path)
        if not path.exists():
            raise FileNotFoundError(f"maFile not found: {path}")
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def can_request_code(self) -> bool:
        last_request = self.db.last_steam_guard_request()
        if not last_request:
            return True
        return datetime.utcnow() - last_request >= timedelta(
            minutes=self.config.min_interval_minutes
        )

    def request_code(self) -> str:
        if not self.can_request_code():
            raise RuntimeError("Steam Guard code request is rate-limited.")
        _ = self._load_mafile()
        self.db.log_steam_guard_request()
        return "000000"  # TODO: generate code from maFile
