from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    keyboard = [
        [KeyboardButton(text="🔍 Найти игру")],
        [KeyboardButton(text="➕ Создать игру")],
        [KeyboardButton(text="👤 Мои игры")],
        [KeyboardButton(text="⭐ Мой рейтинг")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def sport_menu():
    keyboard = [
        [KeyboardButton(text="🎾 Теннис"), KeyboardButton(text="⚽ Футбол")],
        [KeyboardButton(text="🏀 Баскетбол"), KeyboardButton(text="🏐 Волейбол")],
        [KeyboardButton(text="🏓 Настольный теннис"), KeyboardButton(text="🏸 Бадминтон")],
        [KeyboardButton(text="🏒 Хоккей"), KeyboardButton(text="🏉 Регби")],
        [KeyboardButton(text="🏉 Тэг-регби"), KeyboardButton(text="🥋 Самбо")],
        [KeyboardButton(text="🥋 Карате"), KeyboardButton(text="🥋 Тхэквондо")],
        [KeyboardButton(text="🥋 Дзюдо"), KeyboardButton(text="🥊 Бокс")],
        [KeyboardButton(text="🥊 Рукопашный бой"), KeyboardButton(text="🏃 Лёгкая атлетика")],
        [KeyboardButton(text="🏃 Кросс"), KeyboardButton(text="🏊 Плавание")],
        [KeyboardButton(text="⛷️ Лыжные гонки"), KeyboardButton(text="⛸️ Фигурное катание")],
        [KeyboardButton(text="🎿 Биатлон"), KeyboardButton(text="🏂 Сноуборд")],
        [KeyboardButton(text="🏂 Джибинг"), KeyboardButton(text="⛸️ Коньки")],
        [KeyboardButton(text="🧘 Инсайд флоу"), KeyboardButton(text="🔥 Горячий барре")],
        [KeyboardButton(text="🔥 Горячая йога"), KeyboardButton(text="🔥 Горячая растяжка")],
        [KeyboardButton(text="🧘 Пилатес"), KeyboardButton(text="🥌 Кёрлинг")],
        [KeyboardButton(text="🎾 Падел"), KeyboardButton(text="🎾 Сквош")],
        [KeyboardButton(text="🏐 Снежный волейбол"), KeyboardButton(text="⚽ Футбол в валенках")],
        [KeyboardButton(text="❄️ Снежки"), KeyboardButton(text="💪 Зал для мужчин")],
        [KeyboardButton(text="💪 Зал для женщин"), KeyboardButton(text="♟️ Шахматы")],
        [KeyboardButton(text="🎲 Настольные игры")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def level_menu():
    keyboard = [
        [KeyboardButton(text="🟢 Начинающий")],
        [KeyboardButton(text="🟡 Средний")],
        [KeyboardButton(text="🔴 Продвинутый")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def players_menu():
    keyboard = [
        [KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3")],
        [KeyboardButton(text="4"), KeyboardButton(text="5"), KeyboardButton(text="6+")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def confirm_menu():
    keyboard = [
        [KeyboardButton(text="✅ Подтвердить")],
        [KeyboardButton(text="❌ Отменить")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def skip_comment():
    keyboard = [
        [KeyboardButton(text="⏭️ Пропустить")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def attendance_menu():
    keyboard = [
        [KeyboardButton(text="✅ Пришел")],
        [KeyboardButton(text="❌ Не пришел")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def quality_menu():
    keyboard = [
        [KeyboardButton(text="👍 Отлично")],
        [KeyboardButton(text="😐 Нормально")],
        [KeyboardButton(text="👎 Плохо")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
