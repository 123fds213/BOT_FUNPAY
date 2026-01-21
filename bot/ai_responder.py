from __future__ import annotations


class AIResponder:
    def __init__(self, fallback_message: str) -> None:
        self.fallback_message = fallback_message

    def respond(self, prompt: str) -> str:
        """Return a stubbed response for now."""
        _ = prompt
        return self.fallback_message
