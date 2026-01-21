from __future__ import annotations

from telegram.ext import Application

from bot.handlers import BotHandlers


def schedule_jobs(app: Application, handlers: BotHandlers) -> None:
    job_queue = app.job_queue
    job_queue.run_repeating(
        lambda _: app.create_task(handlers.bump_offers()),
        interval=60 * 60 * 2,
        first=10,
        name="auto_bump_offers",
    )
