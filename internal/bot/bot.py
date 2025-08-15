from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from internal.config.config import BOT_TOKEN
from internal.handlers import start, chat
from internal.services.db_service import init_db

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)

dp = Dispatcher()
dp.include_router(start.router)
dp.include_router(chat.router)


async def run_bot():
    await init_db()

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
