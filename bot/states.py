from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    city = State()


class CreateGame(StatesGroup):
    sport = State()
    location = State()
    time = State()
    level = State()
    players_needed = State()
    comment = State()
    confirm = State()


class FindGame(StatesGroup):
    sport = State()


class JoinGame(StatesGroup):
    level = State()
    game_idx = State()


class ReviewGame(StatesGroup):
    attendance = State()
    quality = State()
