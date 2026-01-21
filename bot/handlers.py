from __future__ import annotations

from datetime import datetime
from functools import wraps
from typing import Callable, Awaitable

from telegram import Update
from telegram.ext import ContextTypes

from bot.ai_responder import AIResponder
from bot.db import Database
from bot.funpay_api import FunPayClient
from bot.steam_guard import SteamGuardService


HandlerFunc = Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]]


def owner_only(owner_id: int) -> Callable[[HandlerFunc], HandlerFunc]:
    def decorator(func: HandlerFunc) -> HandlerFunc:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            if update.effective_user and update.effective_user.id == owner_id:
                await func(update, context)
                return
            if update.message:
                await update.message.reply_text("Access denied.")

        return wrapper

    return decorator


class BotHandlers:
    def __init__(
        self,
        owner_id: int,
        db: Database,
        funpay: FunPayClient,
        ai: AIResponder,
        steam_guard: SteamGuardService,
    ) -> None:
        self.owner_id = owner_id
        self.db = db
        self.funpay = funpay
        self.ai = ai
        self.steam_guard = steam_guard

    @property
    def secure(self) -> Callable[[HandlerFunc], HandlerFunc]:
        return owner_only(self.owner_id)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        _ = context
        if update.message:
            await update.message.reply_text("FunPay bot is online.")
        await self.bump_offers()

    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        _ = context
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        if update.message:
            await update.message.reply_text(
                "📊 Stats (stub)\n"
                f"Updated: {now}\n"
                "Sales today: 0\n"
                "Weekly sales: 0\n"
                "Average price: 0"
            )

    async def edit_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            return
        if len(context.args) != 2:
            await update.message.reply_text("Usage: /edit_price <offer_id> <price>")
            return
        offer_id, price_text = context.args
        try:
            price = float(price_text)
        except ValueError:
            await update.message.reply_text("Price must be a number.")
            return
        self.funpay.update_offer_price(offer_id, price)
        await update.message.reply_text(
            f"Price update requested for offer {offer_id}: {price}"
        )

    async def request_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        _ = context
        if not update.message:
            return
        try:
            code = self.steam_guard.request_code()
        except (FileNotFoundError, RuntimeError) as exc:
            await update.message.reply_text(str(exc))
            return
        await update.message.reply_text(f"Steam Guard code: {code}")

    async def handle_funpay_message(self, chat_id: str, message: str) -> str:
        self.db.log_message(chat_id, "inbound", message)
        response = self.ai.respond(message)
        self.db.log_message(chat_id, "outbound", response)
        self.funpay.send_chat_message(chat_id, response)
        return response

    async def bump_offers(self) -> None:
        offers = self.funpay.fetch_offers()
        self.db.upsert_offers([
            {
                "offer_id": offer.offer_id,
                "title": offer.title,
                "price": offer.price,
                "quantity": offer.quantity,
                "status": offer.status,
            }
            for offer in offers
        ])
        self.funpay.bump_offers(offers)
