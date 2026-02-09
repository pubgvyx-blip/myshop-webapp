# MyShop WebApp + Telegram Bot

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export BOT_TOKEN="<your_bot_token>"
export WEBAPP_URL="http://127.0.0.1:5000"
export ADMIN_ID="5718190757"
python app.py
# in another terminal
python bot.py
```

## 24/7 deployment

The repository is configured for two long-running processes in `Procfile`:

- `web`: Flask app via gunicorn
- `worker`: Telegram bot polling process

Set environment variables in your hosting provider:

- `BOT_TOKEN` (required)
- `WEBAPP_URL` (optional)
- `ADMIN_ID` (optional)
- `DB_PATH` (optional, defaults to `shop.db` in repo root)

## DB quick notes

`/buy` reads from table `keys` and marks purchased records as used.
If there are no rows in `keys`, user sees `Нет в наличии`.

Healthcheck endpoint:

- `GET /health` -> `{"status":"ok"}`
