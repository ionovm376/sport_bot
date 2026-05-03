from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from bot.states import ReviewGame
from bot.keyboards import attendance_menu, quality_menu, main_menu
from bot.rating_system import add_review, format_rating, completed_games, user_ratings
from bot.review_scheduler import review_contexts

router = Router()


@router.message(F.text == "⭐ Мой рейтинг")
async def show_my_rating(message: Message):
    rating_text = format_rating(message.from_user.id)
    await message.answer(
        f"📊 Твоя статистика:\n\n{rating_text}",
        reply_markup=main_menu()
    )


@router.message(F.text == "/debug_games")
async def debug_completed_games(message: Message):
    """Временная команда для отладки - показать завершенные игры"""
    if not completed_games:
        await message.answer("Завершенных игр пока нет")
        return

    text = f"📋 Завершенных игр: {len(completed_games)}\n\n"
    for idx, game in enumerate(completed_games, 1):
        text += (
            f"{idx}. {game['sport']}\n"
            f"   Создатель: @{game['creator_username']} (ID: {game['creator_id']})\n"
            f"   Участник: @{game['participant_username']} (ID: {game['participant_id']})\n"
            f"   Время: {game['game_time']}\n"
            f"   Опросы отправлены: {game['reviews_sent']}\n\n"
        )

    await message.answer(text)


@router.message(F.text == "/debug_ratings")
async def debug_ratings(message: Message):
    """Показать все рейтинги"""
    if not user_ratings:
        await message.answer("Рейтингов пока нет")
        return

    text = "📊 Все рейтинги:\n\n"
    for user_id, data in user_ratings.items():
        text += (
            f"User ID: {user_id}\n"
            f"⭐ Рейтинг: {data['rating']:.1f}\n"
            f"🎮 Игр: {data['games_count']}\n"
            f"✅ Успешных: {data['success_games']}\n"
            f"❌ Неявок: {data['no_show']}\n\n"
        )

    await message.answer(text)


@router.callback_query(F.data.startswith("review_attend_"))
async def process_attend(callback: CallbackQuery):
    user_id = callback.from_user.id
    context = review_contexts.get(user_id)

    if not context:
        await callback.answer("⚠️ Контекст оценки не найден", show_alert=True)
        return

    game_id = callback.data.split("_")[2]
    context['step'] = 'quality'

    quality_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👍 Отлично", callback_data=f"review_great_{game_id}")],
        [InlineKeyboardButton(text="😐 Нормально", callback_data=f"review_ok_{game_id}")],
        [InlineKeyboardButton(text="👎 Плохо", callback_data=f"review_bad_{game_id}")]
    ])

    await callback.message.edit_text(
        "👍 Как прошла игра?",
        reply_markup=quality_keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("review_noshow_"))
async def process_noshow(callback: CallbackQuery):
    user_id = callback.from_user.id
    context = review_contexts.get(user_id)

    if not context:
        await callback.answer("⚠️ Контекст оценки не найден", show_alert=True)
        return

    game_id = context['game_id']
    to_user_id = context['to_user_id']

    add_review(user_id, to_user_id, game_id, 0)
    review_contexts.pop(user_id, None)

    await callback.message.edit_text("😔 Жаль, что партнер не пришел. Оценка сохранена.")
    await callback.answer("✅ Оценка сохранена!")


@router.callback_query(F.data.startswith("review_great_"))
async def process_great(callback: CallbackQuery):
    await process_quality_callback(callback, 5)


@router.callback_query(F.data.startswith("review_ok_"))
async def process_ok(callback: CallbackQuery):
    await process_quality_callback(callback, 3)


@router.callback_query(F.data.startswith("review_bad_"))
async def process_bad(callback: CallbackQuery):
    await process_quality_callback(callback, 1)


async def process_quality_callback(callback: CallbackQuery, score: int):
    user_id = callback.from_user.id
    context = review_contexts.get(user_id)

    if not context:
        await callback.answer("⚠️ Контекст оценки не найден", show_alert=True)
        return

    game_id = context['game_id']
    to_user_id = context['to_user_id']

    add_review(user_id, to_user_id, game_id, score)
    review_contexts.pop(user_id, None)

    await callback.message.edit_text("✅ Спасибо за оценку! Рейтинг партнера обновлен.")
    await callback.answer("✅ Оценка сохранена!")
