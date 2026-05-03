from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.states import CreateGame
from bot.keyboards import sport_menu, level_menu, players_menu, confirm_menu, skip_comment, main_menu
from bot.sports_list import SPORTS_LIST

router = Router()

games_storage = []


@router.message(F.text == "➕ Создать игру")
async def create_game_start(message: Message, state: FSMContext):
    await state.set_state(CreateGame.sport)
    await message.answer(
        "🎯 Выбери вид спорта:",
        reply_markup=sport_menu()
    )


@router.message(F.text == "❌ Отмена")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "❌ Создание игры отменено",
        reply_markup=main_menu()
    )


@router.message(CreateGame.sport)
async def process_sport(message: Message, state: FSMContext):
    sport = message.text

    if sport not in SPORTS_LIST:
        await message.answer("⚠️ Выбери вид спорта из меню")
        return

    await state.update_data(sport=sport)
    await state.set_state(CreateGame.location)
    await message.answer(
        "📍 Укажи место игры:\n(например: Лужники, Парк Горького)",
        reply_markup=main_menu()
    )


@router.message(CreateGame.location)
async def process_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    await state.set_state(CreateGame.time)
    await message.answer(
        "🕐 Укажи время игры:\n(например: сегодня 19:00, завтра 10:00)"
    )


@router.message(CreateGame.time)
async def process_time(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    await state.set_state(CreateGame.level)
    await message.answer(
        "🏅 Выбери уровень игры:",
        reply_markup=level_menu()
    )


@router.message(CreateGame.level)
async def process_level(message: Message, state: FSMContext):
    level = message.text

    if level not in ["🟢 Начинающий", "🟡 Средний", "🔴 Продвинутый"]:
        await message.answer("⚠️ Выбери уровень из меню")
        return

    await state.update_data(level=level)
    await state.set_state(CreateGame.players_needed)
    await message.answer(
        "👥 Сколько человек нужно?",
        reply_markup=players_menu()
    )


@router.message(CreateGame.players_needed)
async def process_players(message: Message, state: FSMContext):
    players = message.text

    if players not in ["1", "2", "3", "4", "5", "6+"]:
        await message.answer("⚠️ Выбери количество из меню")
        return

    await state.update_data(players_needed=players)
    await state.set_state(CreateGame.comment)
    await message.answer(
        "💬 Добавь комментарий (необязательно):",
        reply_markup=skip_comment()
    )


@router.message(CreateGame.comment)
async def process_comment(message: Message, state: FSMContext):
    comment = message.text if message.text != "⏭️ Пропустить" else "—"
    await state.update_data(comment=comment)

    data = await state.get_data()

    confirmation_text = (
        "📋 Проверь данные:\n\n"
        f"🎯 Спорт: {data['sport']}\n"
        f"📍 Место: {data['location']}\n"
        f"🕐 Время: {data['time']}\n"
        f"🏅 Уровень: {data['level']}\n"
        f"👥 Нужно людей: {data['players_needed']}\n"
        f"💬 Комментарий: {comment}\n\n"
        "Всё верно?"
    )

    await state.set_state(CreateGame.confirm)
    await message.answer(confirmation_text, reply_markup=confirm_menu())


@router.message(CreateGame.confirm)
async def process_confirm(message: Message, state: FSMContext):
    if message.text == "✅ Подтвердить":
        data = await state.get_data()
        data['creator_id'] = message.from_user.id
        data['creator_username'] = message.from_user.username or "без username"

        games_storage.append(data)

        await message.answer(
            "✅ Игра создана!\n\n"
            "Теперь другие пользователи смогут найти её и присоединиться.",
            reply_markup=main_menu()
        )
        await state.clear()
    elif message.text == "❌ Отменить":
        await state.clear()
        await message.answer(
            "❌ Создание игры отменено",
            reply_markup=main_menu()
        )
    else:
        await message.answer("⚠️ Выбери действие из меню")
