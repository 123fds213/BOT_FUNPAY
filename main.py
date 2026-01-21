import logging

from telegram.ext import Application, CommandHandler

from bot.ai_responder import AIResponder
from bot.config import load_settings
from bot.db import Database
from bot.funpay_api import FunPayClient
from bot.handlers import BotHandlers
from bot.scheduler import schedule_jobs
from bot.steam_guard import SteamGuardConfig, SteamGuardService


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    settings = load_settings()
    db = Database(settings.db_path, settings.fernet_key)
    db.init()

    funpay = FunPayClient(settings.funpay_golden_key)
    ai = AIResponder("Спасибо за сообщение! Мы скоро ответим.")
    steam_guard = SteamGuardService(
        SteamGuardConfig(mafile_path=settings.mafile_path),
        db,
    )

    handlers = BotHandlers(
        owner_id=settings.owner_id,
        db=db,
        funpay=funpay,
        ai=ai,
        steam_guard=steam_guard,
    )

    app = Application.builder().token(settings.telegram_token).build()
    app.add_handler(CommandHandler("start", handlers.secure(handlers.start)))
    app.add_handler(CommandHandler("stats", handlers.secure(handlers.stats)))
    app.add_handler(CommandHandler("edit_price", handlers.secure(handlers.edit_price)))
    app.add_handler(CommandHandler("code", handlers.secure(handlers.request_code)))

    schedule_jobs(app, handlers)

    app.run_polling()


if __name__ == "__main__":
    main()
