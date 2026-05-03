# 🎾 Sport Bot - Telegram бот для поиска партнеров по спорту

## 🚀 Установка

1. Установи зависимости:
```bash
pip install -r requirements.txt
```

2. Создай бота через @BotFather в Telegram и получи токен

3. Добавь токен в `.env`:
```
BOT_TOKEN=твой_токен_здесь
```

4. Запусти бота:
```bash
python -m bot.main
```

## ✅ Что работает

- /start - запуск бота
- Главное меню с кнопками
- Полный FSM для создания игры (все 7 шагов)
- Сохранение игр в память (games_storage)
- Отмена создания игры на любом этапе

## 📋 Структура

```
sport_bot/
├── bot/
│   ├── main.py          # точка входа
│   ├── config.py        # конфигурация
│   ├── keyboards.py     # клавиатуры
│   ├── states.py        # FSM состояния
│   └── handlers/
│       ├── start.py     # /start и главное меню
│       └── create_game.py  # создание игры
├── .env
└── requirements.txt
```
