import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GIGACHAT_AUTH = os.getenv("GIGACHAT_AUTH")
GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
GIGACHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1"

HISTORY_LIMIT = os.getenv("HISTORY_LIMIT")

POSTGRES_USER = os.getenv("POSTGRES_USER", "tg_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "tg_pass")
POSTGRES_DB = os.getenv("POSTGRES_DB", "tg_bot_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
