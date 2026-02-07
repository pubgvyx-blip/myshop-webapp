import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo
)
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ==============================
# НАСТРОЙКИ
# ==============================

BOT_TOKEN = "8572275616:AAGB0QDBGZ99JtAG2_JLABjjpxdKnBnmj-0"
WEBAPP_URL = "https://myshop-webapp-production.up.railway.app"
ADMIN_ID = 5718190757  # твой Telegram ID

# ==============================
# ИНИЦИАЛИЗАЦИЯ
# ==============================

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# ==============================
# КНОПКИ
# ==============================

def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Открыть магазин",
                    web_app=WebAppInfo(url=WEBAPP_URL)
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
        reply_markup=main_menu()
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

# ==============================
# ЗАПУСК
# ==============================

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
