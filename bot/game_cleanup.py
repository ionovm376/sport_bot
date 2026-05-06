import asyncio
from datetime import datetime
from sqlalchemy import select
from bot.database import async_session_maker, Game


async def cleanup_expired_games():
    """Фоновая задача для удаления просроченных игр"""
    while True:
        try:
            current_time = datetime.utcnow()

            async with async_session_maker() as session:
                # Находим все активные игры, у которых истёк срок
                result = await session.execute(
                    select(Game).where(
                        Game.is_active == True,
                        Game.expires_at != None,
                        Game.expires_at <= current_time
                    )
                )
                expired_games = result.scalars().all()

                # Помечаем их как неактивные
                for game in expired_games:
                    game.is_active = False
                    print(f"Игра #{game.id} удалена (просрочена): {game.sport}, {game.time}")

                if expired_games:
                    await session.commit()
                    print(f"Удалено просроченных игр: {len(expired_games)}")

            # Проверяем каждую минуту (для теста)
            await asyncio.sleep(60)

        except Exception as e:
            print(f"Ошибка в cleanup_expired_games: {e}")
            await asyncio.sleep(60)
