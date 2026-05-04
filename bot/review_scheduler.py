import asyncio
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.rating_system import completed_games

# Глобальное хранилище контекста оценок
review_contexts = {}


async def check_and_send_reviews(bot):
    """Фоновая задача для отправки опросов после игр"""
    while True:
        try:
            current_time = datetime.now()

            for game in completed_games:
                if game['reviews_sent']:
                    continue

                # Устанавливаем время создания игры при первой проверке
                if 'created_at' not in game:
                    game['created_at'] = current_time
                    continue

                # Отправляем опрос через 2 часа после создания матча
                time_passed = current_time - game['created_at']

                # 2 часа = 7200 секунд
                if time_passed.total_seconds() >= 7200:
                    await send_review_requests(bot, game)
                    game['reviews_sent'] = True

            # Проверяем каждые 5 минут (300 секунд)
            await asyncio.sleep(300)

        except Exception as e:
            print(f"Ошибка в check_and_send_reviews: {e}")
            await asyncio.sleep(300)


async def send_review_requests(bot, game):
    """Отправить запросы на оценку обоим участникам"""
    game_id = game['game_id']

    # Сохраняем контекст для обработчиков
    review_contexts[game['creator_id']] = {
        'game_id': game_id,
        'to_user_id': game['participant_id'],
        'step': 'attendance'
    }
    review_contexts[game['participant_id']] = {
        'game_id': game_id,
        'to_user_id': game['creator_id'],
        'step': 'attendance'
    }

    # Inline клавиатура для посещаемости
    attendance_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Пришел", callback_data=f"review_attend_{game_id}"),
            InlineKeyboardButton(text="❌ Не пришел", callback_data=f"review_noshow_{game_id}")
        ]
    ])

    # Отправляем создателю (оценить участника)
    try:
        await bot.send_message(
            chat_id=game['creator_id'],
            text=(
                f"⏰ Время оценить партнера!\n\n"
                f"🎯 Игра: {game['sport']}\n"
                f"👤 Партнер: @{game['participant_username']}\n\n"
                f"Пришел ли партнер на игру?"
            ),
            reply_markup=attendance_keyboard
        )
    except Exception as e:
        print(f"Не удалось отправить опрос создателю: {e}")

    # Отправляем участнику (оценить создателя)
    try:
        await bot.send_message(
            chat_id=game['participant_id'],
            text=(
                f"⏰ Время оценить партнера!\n\n"
                f"🎯 Игра: {game['sport']}\n"
                f"👤 Партнер: @{game['creator_username']}\n\n"
                f"Пришел ли партнер на игру?"
            ),
            reply_markup=attendance_keyboard
        )
    except Exception as e:
        print(f"Не удалось отправить опрос участнику: {e}")
