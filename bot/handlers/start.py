from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
import os

from bot.keyboards import main_menu, sport_menu
from bot.states import FindGame

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    # Путь к фото
    photo_path = os.path.join(os.path.dirname(__file__), '..', 'start_photo.jpg')

    # Отправляем фото с текстом
    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(
            photo=photo,
            caption=f"👋 Привет, {message.from_user.first_name}!\n\n"
                    "Я помогу тебе найти партнера для спорта.\n\n"
                    "Выбери действие:",
            reply_markup=main_menu()
        )
    else:
        # Если фото нет, отправляем просто текст
        await message.answer(
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            "Я помогу тебе найти партнера для спорта.\n\n"
            "Выбери действие:",
            reply_markup=main_menu()
        )


@router.message(F.text == "👤 Мои игры")
async def my_games(message: Message):
    from bot.handlers.create_game import games_storage
    from bot.rating_system import completed_games
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    user_id = message.from_user.id

    # Ищем активные игры (созданные пользователем)
    active_games = [(idx, game) for idx, game in enumerate(games_storage) if game['creator_id'] == user_id]

    # Ищем завершённые игры
    finished_games = [game for game in completed_games
                     if game['creator_id'] == user_id or game['participant_id'] == user_id]

    if not active_games and not finished_games:
        await message.answer(
            "📋 У тебя пока нет игр\n\n"
            "Создай игру или откликнись на существующую!",
            reply_markup=main_menu()
        )
        return

    # Показываем активные игры с кнопками отмены
    if active_games:
        await message.answer("🎮 Твои активные игры:", reply_markup=main_menu())

        for idx, game in active_games:
            text = (
                f"{game['sport']}\n"
                f"📍 {game['location']}\n"
                f"🕐 {game['time']}\n"
                f"👥 Нужно: {game['players_needed']}\n"
                f"🏅 Уровень: {game['level']}"
            )

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отменить игру", callback_data=f"cancel_game_{idx}")]
            ])

            await message.answer(text, reply_markup=keyboard)

    # Показываем завершённые игры
    if finished_games:
        text = "✅ Завершённые игры:\n\n"
        for idx, game in enumerate(finished_games, 1):
            partner = game['participant_username'] if game['creator_id'] == user_id else game['creator_username']
            text += (
                f"{idx}. {game['sport']}\n"
                f"👤 Партнёр: @{partner}\n"
                f"🕐 {game['game_time']}\n\n"
            )
        await message.answer(text)


@router.message(F.text == "🔍 Найти игру")
async def find_game(message: Message, state: FSMContext):
    await state.set_state(FindGame.sport)
    await message.answer(
        "🎯 Выбери вид спорта для поиска:",
        reply_markup=sport_menu()
    )


@router.callback_query(F.data.startswith("cancel_game_"))
async def cancel_game(callback: CallbackQuery):
    from bot.handlers.create_game import games_storage

    game_idx = int(callback.data.split("_")[2])

    if game_idx >= len(games_storage):
        await callback.answer("❌ Игра уже удалена", show_alert=True)
        return

    game = games_storage[game_idx]

    # Проверяем, что это игра пользователя
    if game['creator_id'] != callback.from_user.id:
        await callback.answer("⚠️ Это не твоя игра!", show_alert=True)
        return

    # Удаляем игру
    games_storage.pop(game_idx)

    await callback.message.edit_text(
        f"❌ Игра отменена\n\n"
        f"{game['sport']}\n"
        f"📍 {game['location']}\n"
        f"🕐 {game['time']}"
    )
    await callback.answer("✅ Игра удалена из поиска!")
