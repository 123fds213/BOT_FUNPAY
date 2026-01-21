# FunPay Automation Bot

Telegram bot scaffold for automating FunPay account workflows (offers, chats, Steam Guard, analytics).

## Features (current scaffold)
- Telegram command handlers with owner-only access control.
- SQLite persistence with encrypted secrets.
- Scheduled tasks (auto-bump offers).
- Stubbed FunPay API client, AI responder, and Steam Guard integration hooks.

## Quick start
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in values.
   - Generate a Fernet key with:
     ```bash
     python - <<'PY'
     from cryptography.fernet import Fernet
     print(Fernet.generate_key().decode())
     PY
     ```
3. Run the bot:
   ```bash
   python main.py
   ```

## Commands
- `/start` — confirm bot is online and trigger an initial offer bump.
- `/stats` — show basic analytics summary.
- `/edit_price <offer_id> <price>` — update a single offer price (stub).

## Notes
- FunPay, Steam Guard, and AI response integrations are stubbed and need API wiring.
- Secrets are encrypted using `FERNET_KEY` in the database.
