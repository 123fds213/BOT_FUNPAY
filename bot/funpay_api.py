from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import requests


@dataclass(frozen=True)
class Offer:
    offer_id: str
    title: str
    price: float
    quantity: int
    status: str


class FunPayClient:
    def __init__(self, golden_key: str) -> None:
        self.golden_key = golden_key

    def ping(self) -> bool:
        """Stubbed health check for the FunPay API."""
        return True

    def fetch_offers(self) -> list[Offer]:
        """Stubbed offers list. Replace with FunPay API calls."""
        return []

    def bump_offers(self, offers: Iterable[Offer]) -> None:
        """Stubbed offer bumping."""
        for _offer in offers:
            continue

    def update_offer_price(self, offer_id: str, price: float) -> None:
        """Stubbed offer price update."""
        _ = (offer_id, price)

    def send_chat_message(self, chat_id: str, message: str) -> None:
        """Stubbed chat message sender."""
        _ = (chat_id, message)
