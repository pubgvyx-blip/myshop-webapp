import asyncio
import json
import logging
import os
import sqlite3
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

# ==============================
# НАСТРОЙКИ
# ==============================

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://myshop-webapp-production.up.railway.app")
ADMIN_ID = int(os.getenv("ADMIN_ID", "5718190757"))
DB_PATH = os.getenv("DB_PATH", str(Path(__file__).resolve().parent / "shop.db"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Add it to environment variables.")


# ==============================
# DB
# ==============================

def ensure_keys_table() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            key TEXT NOT NULL,
            is_used INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()


# ==============================
# ИНИЦИАЛИЗАЦИЯ
# ==============================

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()


# ==============================
# КНОПКИ
# ==============================

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Открыть магазин",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ]
        ]
    )


# ==============================
# /start
# ==============================

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "🔥 <b>Добро пожаловать в магазин!</b>\n\n"
        "Нажми кнопку ниже, чтобы открыть каталог 👇",
        reply_markup=main_menu(),
    )


# ==============================
# /admin
# ==============================

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Доступ запрещён")
        return

    await message.answer(
        "⚙️ <b>Админ-панель</b>\n\n"
        "Команды:\n"
        "/add android KEY-XXXX\n"
        "/add pc KEY-XXXX\n"
        "/stock"
    )


@dp.message(Command("add"))
async def add_key(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Доступ запрещён")
        return

    parts = (message.text or "").split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Формат: /add <android|pc> <KEY>")
        return

    product = parts[1].strip().lower()
    key_value = parts[2].strip()

    if product not in {"android", "pc"}:
        await message.answer("Товар должен быть android или pc")
        return

    ensure_keys_table()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO keys(product, key, is_used) VALUES (?, ?, 0)",
        (product, key_value),
    )
    conn.commit()
    conn.close()

    await message.answer(f"✅ Ключ добавлен для <b>{product}</b>")


@dp.message(Command("stock"))
async def stock(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Доступ запрещён")
        return

    ensure_keys_table()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT product, COUNT(*) FROM keys WHERE is_used = 0 GROUP BY product"
    )
    rows = dict(cur.fetchall())
    conn.close()

    android_count = rows.get("android", 0)
    pc_count = rows.get("pc", 0)
    await message.answer(
        "📦 <b>Остатки</b>\n"
        f"android: <b>{android_count}</b>\n"
        f"pc: <b>{pc_count}</b>"
    )


@dp.message(F.web_app_data)
async def handle_webapp(message: Message):
    data = message.web_app_data.data

    try:
        payload = json.loads(data)
    except json.JSONDecodeError:
        payload = None

    if isinstance(payload, dict) and payload.get("event") == "purchase":
        product = payload.get("product", "неизвестно")
        key = payload.get("key", "-")
        await message.answer(
            "✅ <b>Покупка подтверждена</b>\n"
            f"Товар: <code>{product}</code>\n"
            f"Ключ: <code>{key}</code>"
        )
        return

    if data == "android":
        await message.answer("Вы выбрали Android версию 🔥")
    elif data == "pc":
        await message.answer("Вы выбрали PC версию 💻")


# ==============================
# ЗАПУСК
# ==============================

async def main():
    logging.info("Bot worker started")
    ensure_keys_table()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
