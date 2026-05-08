from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from bot.keyboards import main_menu, sport_menu, city_menu
from bot.states import FindGame, Registration
from bot.database import async_session_maker, Game, CompletedGame

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Registration.city)
    await message.answer(
        "Добро пожаловать в PlayZone!\n\n"
        "🏙️ Выбери свой город:",
        reply_markup=city_menu()
    )


@router.message(Registration.city)
async def process_city(message: Message, state: FSMContext):
    if message.text == "🏙️ Москва":
        await state.clear()
        await message.answer(
            "Отлично! Ты в PlayZone Москва!\n\n"
            "Здесь ты можешь быстро найти людей для спорта или создать свою игру.\n\n"
            "👇 Выбирай, что хочешь сделать:",
            reply_markup=main_menu()
        )
    elif message.text == "🌍 Другое":
        await state.clear()
        await message.answer(
            "К сожалению, пока сервис работает только в Москве 😔\n\n"
            "Следи за обновлениями — скоро откроемся в других городах!\n\n"
            "Чтобы начать заново, нажми /start",
            reply_markup=None
        )
    else:
        await message.answer("⚠️ Выбери город из меню")


@router.message(F.text == "👤 Мои игры")
async def my_games(message: Message):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    user_id = message.from_user.id

    # Ищем активные игры (созданные пользователем) в БД
    async with async_session_maker() as session:
        result = await session.execute(
            select(Game).where(Game.creator_id == user_id, Game.is_active == True)
        )
        active_games = result.scalars().all()

        # Ищем завершённые игры
        result = await session.execute(
            select(CompletedGame).where(
                (CompletedGame.creator_id == user_id) | (CompletedGame.participant_id == user_id)
            )
        )
        finished_games = result.scalars().all()

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

        for game in active_games:
            # Вычисляем сколько мест осталось
            try:
                players_needed_num = int(game.players_needed)
            except ValueError:
                # Если не число (например старая запись "6+"), считаем как 6
                players_needed_num = 6

            spots_left = players_needed_num - game.participants_count

            text = (
                f"{game.sport}\n"
                f"📍 {game.location}\n"
                f"🕐 {game.time}\n"
                f"👥 Набрано: {game.participants_count}/{game.players_needed}\n"
                f"🔓 Осталось мест: {spots_left}\n"
                f"🏅 Уровень: {game.level}"
            )

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отменить игру", callback_data=f"cancel_game_{game.id}")]
            ])

            await message.answer(text, reply_markup=keyboard)

    # Показываем завершённые игры
    if finished_games:
        text = "✅ Завершённые игры:\n\n"
        for idx, game in enumerate(finished_games, 1):
            partner = game.participant_username if game.creator_id == user_id else game.creator_username
            text += (
                f"{idx}. {game.sport}\n"
                f"👤 Партнёр: @{partner}\n"
                f"🕐 {game.game_time}\n\n"
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
    game_id = int(callback.data.split("_")[2])

    async with async_session_maker() as session:
        result = await session.execute(select(Game).where(Game.id == game_id))
        game = result.scalar_one_or_none()

        if not game:
            await callback.answer("❌ Игра уже удалена", show_alert=True)
            return

        # Проверяем, что это игра пользователя
        if game.creator_id != callback.from_user.id:
            await callback.answer("⚠️ Это не твоя игра!", show_alert=True)
            return

        # Помечаем игру как неактивную
        game.is_active = False
        await session.commit()

        await callback.message.edit_text(
            f"❌ Игра отменена\n\n"
            f"{game.sport}\n"
            f"📍 {game.location}\n"
            f"🕐 {game.time}"
        )
        await callback.answer("✅ Игра удалена из поиска!")
