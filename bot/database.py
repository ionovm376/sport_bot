from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, BigInteger, DateTime, Boolean, Integer
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./sport_bot.db")

# Для Railway PostgreSQL нужно заменить postgres:// или postgresql:// на postgresql+asyncpg://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), default="Москва")
    rating: Mapped[int] = mapped_column(Integer, default=0)
    games_played: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sport: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(255))
    time: Mapped[str] = mapped_column(String(100))
    level: Mapped[str] = mapped_column(String(50))
    players_needed: Mapped[str] = mapped_column(String(10))
    comment: Mapped[str] = mapped_column(String(500), default="—")
    city: Mapped[str] = mapped_column(String(100), default="Москва")
    creator_id: Mapped[int] = mapped_column(BigInteger)
    creator_username: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CompletedGame(Base):
    __tablename__ = "completed_games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(String(100), unique=True)
    sport: Mapped[str] = mapped_column(String(100))
    game_time: Mapped[str] = mapped_column(String(100))
    creator_id: Mapped[int] = mapped_column(BigInteger)
    creator_username: Mapped[str] = mapped_column(String(255))
    participant_id: Mapped[int] = mapped_column(BigInteger)
    participant_username: Mapped[str] = mapped_column(String(255))
    reviews_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
