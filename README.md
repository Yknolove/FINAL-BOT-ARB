@@ -7,25 +7,30 @@ A minimal Telegram bot that notifies about P2P arbitrage opportunities.
# P2P Arbitrage Telegram Bot

A minimal Telegram bot that notifies about P2P arbitrage opportunities.
Set the following variables in your environment or in a `.env` file before running the bot:

- `BOT_TOKEN` – Telegram bot token obtained from BotFather.
- `WEBHOOK_URL` – Public URL that Telegram should use to deliver updates (e.g. `https://your.domain/webhook`).
- `PORT` – (optional) HTTP port for the webhook. Defaults to `8443`.

An example file `.env.example` is provided for reference.

## Installing dependencies

Use `pip` to install the requirements:

```bash
pip install -r requirements.txt
```

## Running the bot

After setting the required variables and installing dependencies, start the bot with:

```bash
python main.py
```

This will launch the Telegram bot and begin processing updates.
