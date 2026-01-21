from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    owner_id: int
    funpay_golden_key: str
    fernet_key: str
    db_path: str
    mafile_path: str


def load_settings() -> Settings:
    load_dotenv()
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    owner_id = int(os.getenv("OWNER_TELEGRAM_ID", "0"))
    funpay_golden_key = os.getenv("FUNPAY_GOLDEN_KEY", "").strip()
    fernet_key = os.getenv("FERNET_KEY", "").strip()
    db_path = os.getenv("DB_PATH", "funpay_bot.db").strip()
    mafile_path = os.getenv("MAFILE_PATH", "mafile.json").strip()

    if not telegram_token:
        raise ValueError("TELEGRAM_BOT_TOKEN is required")
    if owner_id <= 0:
        raise ValueError("OWNER_TELEGRAM_ID is required")
    if not funpay_golden_key:
        raise ValueError("FUNPAY_GOLDEN_KEY is required")
    if not fernet_key:
        raise ValueError("FERNET_KEY is required")

    return Settings(
        telegram_token=telegram_token,
        owner_id=owner_id,
        funpay_golden_key=funpay_golden_key,
        fernet_key=fernet_key,
        db_path=db_path,
        mafile_path=mafile_path,
    )
