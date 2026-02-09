import asyncio
import json
import logging
import os

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

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Add it to environment variables.")

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
        "/add KEY-XXXX\n"
        "/stock"
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
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
