from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
import uuid

from bot.states import FindGame, JoinGame
from bot.keyboards import main_menu, level_menu
from bot.sports_list import SPORTS_LIST
from bot.rating_system import format_rating
from bot.database import async_session_maker, Game, CompletedGame

router = Router()


@router.message(FindGame.sport)
async def process_find_sport(message: Message, state: FSMContext):
    sport = message.text

    if sport == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Поиск отменен", reply_markup=main_menu())
        return

    if sport not in SPORTS_LIST:
        await message.answer("⚠️ Выбери вид спорта из меню")
        return

    # Ищем игры в БД
    async with async_session_maker() as session:
        result = await session.execute(
            select(Game).where(Game.sport == sport, Game.is_active == True, Game.city == 'Москва')
        )
        filtered_games = result.scalars().all()

    if not filtered_games:
        await message.answer(
            f"😔 Пока нет игр по виду спорта: {sport}\n\n"
            "Создай свою игру!",
            reply_markup=main_menu()
        )
        await state.clear()
        return

    await message.answer(
        f"🔍 Найдено игр: {len(filtered_games)}\n\n"
        "Смотри анкеты ниже:",
        reply_markup=main_menu()
    )

    for idx, game in enumerate(filtered_games, 1):
        # Вычисляем сколько мест осталось
        players_needed_num = int(game.players_needed.replace('+', '')) if game.players_needed != '6+' else 6
        spots_left = players_needed_num - game.participants_count

        game_text = (
            f"📋 Игра #{idx}\n\n"
            f"🎯 Спорт: {game.sport}\n"
            f"📍 Место: {game.location}\n"
            f"🕐 Время: {game.time}\n"
            f"🏅 Уровень: {game.level}\n"
            f"👥 Набрано: {game.participants_count}/{game.players_needed}\n"
            f"🔓 Осталось мест: {spots_left}\n"
            f"💬 Комментарий: {game.comment}\n"
            f"👤 Создатель: @{game.creator_username}\n\n"
            f"{format_rating(game.creator_id)}"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Хочу присоединиться", callback_data=f"join_{game.id}")]
        ])

        await message.answer(game_text, reply_markup=keyboard)

    await state.clear()


@router.callback_query(F.data.startswith("join_"))
async def process_join_request(callback: CallbackQuery, state: FSMContext):
    game_id = int(callback.data.split("_")[1])

    # Ищем игру в БД
    async with async_session_maker() as session:
        result = await session.execute(select(Game).where(Game.id == game_id, Game.is_active == True))
        game = result.scalar_one_or_none()

    if not game:
        await callback.answer("❌ Игра не найдена", show_alert=True)
        return

    if callback.from_user.id == game.creator_id:
        await callback.answer("⚠️ Это твоя игра!", show_alert=True)
        return

    await state.update_data(game_id=game_id)
    await state.set_state(JoinGame.level)

    await callback.message.answer(
        "🏅 Укажи свой уровень игры:",
        reply_markup=level_menu()
    )
    await callback.answer()


@router.message(JoinGame.level)
async def process_join_level(message: Message, state: FSMContext):
    level = message.text

    if level == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отклик отменен", reply_markup=main_menu())
        return

    if level not in ["🟢 Начинающий", "🟡 Средний", "🔴 Продвинутый"]:
        await message.answer("⚠️ Выбери уровень из меню")
        return

    data = await state.get_data()
    game_id = data['game_id']

    # Получаем игру из БД
    async with async_session_maker() as session:
        result = await session.execute(select(Game).where(Game.id == game_id))
        game = result.scalar_one_or_none()

    if not game:
        await message.answer("❌ Игра не найдена", reply_markup=main_menu())
        await state.clear()
        return

    await message.answer(
        "✅ Заявка отправлена создателю!",
        reply_markup=main_menu()
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{game_id}_{message.from_user.id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_{game_id}_{message.from_user.id}")
        ]
    ])

    await message.bot.send_message(
        chat_id=game.creator_id,
        text=(
            f"🔔 Новая заявка на игру!\n\n"
            f"👤 Пользователь: @{message.from_user.username or 'без username'}\n"
            f"Имя: {message.from_user.first_name}\n"
            f"🏅 Уровень: {level}\n\n"
            f"🎯 Игра: {game.sport}\n"
            f"📍 {game.location}\n"
            f"🕐 {game.time}\n"
            f"🏅 Требуемый уровень: {game.level}"
        ),
        reply_markup=keyboard
    )

    await state.clear()


@router.callback_query(F.data.startswith("accept_"))
async def process_accept(callback: CallbackQuery):
    parts = callback.data.split("_")
    game_id = int(parts[1])
    user_id = int(parts[2])

    # Получаем игру из БД
    async with async_session_maker() as session:
        result = await session.execute(select(Game).where(Game.id == game_id))
        game = result.scalar_one_or_none()

        if not game:
            await callback.answer("❌ Игра уже удалена", show_alert=True)
            return

        # Увеличиваем счётчик участников
        game.participants_count += 1

        # Проверяем сколько нужно людей
        players_needed_num = int(game.players_needed.replace('+', '')) if game.players_needed != '6+' else 6

        # Если набрали всех — закрываем игру
        if game.participants_count >= players_needed_num:
            game.is_active = False
            status_text = "✅ Заявка принята! Все места заняты, игра закрыта."
        else:
            spots_left = players_needed_num - game.participants_count
            status_text = f"✅ Заявка принята! Набрано: {game.participants_count}/{game.players_needed}. Осталось мест: {spots_left}"

        await callback.message.edit_text(
            callback.message.text + f"\n\n{status_text}"
        )

        await callback.bot.send_message(
            chat_id=user_id,
            text=(
                f"🎉 Твоя заявка принята!\n\n"
                f"🎯 Игра: {game.sport}\n"
                f"📍 {game.location}\n"
                f"🕐 {game.time}\n\n"
                f"👤 Контакт создателя: @{game.creator_username}"
            )
        )

        # Сохраняем завершенную игру для последующей оценки
        game_uuid = str(uuid.uuid4())
        completed_game = CompletedGame(
            game_id=game_uuid,
            creator_id=game.creator_id,
            creator_username=game.creator_username,
            participant_id=user_id,
            participant_username=callback.from_user.username or "без username",
            game_time=game.time,
            sport=game.sport,
            reviews_sent=False
        )
        session.add(completed_game)
        await session.commit()

    await callback.answer(status_text)


@router.callback_query(F.data.startswith("decline_"))
async def process_decline(callback: CallbackQuery):
    parts = callback.data.split("_")
    user_id = int(parts[2])

    await callback.message.edit_text(
        callback.message.text + "\n\n❌ Заявка отклонена"
    )

    await callback.bot.send_message(
        chat_id=user_id,
        text="😔 К сожалению, твоя заявка была отклонена."
    )

    await callback.answer("❌ Заявка отклонена")
