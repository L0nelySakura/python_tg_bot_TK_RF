from sqlalchemy import Column, Integer, String, Text, DateTime, func
from internal.config.config import engine, async_session
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user / ai
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def save_message(user_id: int, role: str, content: str):
    async with async_session() as session:
        async with session.begin():
            session.add(Message(user_id=user_id, role=role, content=content))


async def get_history(user_id: int, limit: int = 10):
    async with async_session() as session:
        result = await session.execute(
            Message.__table__.select()
            .where(Message.user_id == user_id)
            .order_by(Message.id.desc())
            .limit(limit)
        )
        rows = result.fetchall()
        return [{"role": r[2], "content": r[3]} for r in reversed(rows)]


async def clear_history(user_id: int):
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                Message.__table__.delete().where(Message.user_id == user_id)
            )
