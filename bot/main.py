import asyncio
import logging
from aiogram import Bot, Dispatcher

from bot.config import BOT_TOKEN
from bot.handlers import start, create_game, find_game, rating
from bot.review_scheduler import check_and_send_reviews
from bot.game_cleanup import cleanup_expired_games
from bot.database import init_db

logging.basicConfig(level=logging.INFO)


async def main():
    # Инициализируем базу данных
    await init_db()
    logging.info("Database initialized")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(create_game.router)
    dp.include_router(find_game.router)
    dp.include_router(rating.router)

    # Запускаем фоновые задачи
    asyncio.create_task(check_and_send_reviews(bot))
    asyncio.create_task(cleanup_expired_games())
    logging.info("Background tasks started")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
