# Хранилище рейтингов пользователей
user_ratings = {}

# Структура:
# user_ratings[user_id] = {
#     "scores": [5, 3, 5, 0],  # все оценки
#     "games_count": 4,
#     "success_games": 3,
#     "no_show": 1,
#     "rating": 3.25
# }

# Хранилище завершенных игр (для отправки опросов)
completed_games = []

# Структура:
# {
#     "game_id": "unique_id",
#     "creator_id": 123,
#     "participant_id": 456,
#     "game_time": "сегодня 19:00",
#     "sport": "🎾 Теннис",
#     "reviews_sent": False
# }

# Хранилище оценок
reviews = []

# Структура:
# {
#     "from_user_id": 123,
#     "to_user_id": 456,
#     "game_id": "unique_id",
#     "score": 5
# }


def get_user_rating(user_id):
    """Получить рейтинг пользователя"""
    if user_id not in user_ratings:
        return {
            "scores": [],
            "games_count": 0,
            "success_games": 0,
            "no_show": 0,
            "rating": 0.0
        }
    return user_ratings[user_id]


def add_review(from_user_id, to_user_id, game_id, score):
    """Добавить оценку"""
    # Проверка: нельзя оценить самого себя
    if from_user_id == to_user_id:
        return False

    # Проверка: одна оценка за игру
    for review in reviews:
        if review["from_user_id"] == from_user_id and review["game_id"] == game_id:
            return False

    # Добавляем оценку
    reviews.append({
        "from_user_id": from_user_id,
        "to_user_id": to_user_id,
        "game_id": game_id,
        "score": score
    })

    # Обновляем рейтинг пользователя
    if to_user_id not in user_ratings:
        user_ratings[to_user_id] = {
            "scores": [],
            "games_count": 0,
            "success_games": 0,
            "no_show": 0,
            "rating": 0.0
        }

    user_ratings[to_user_id]["scores"].append(score)
    user_ratings[to_user_id]["games_count"] += 1

    if score > 0:
        user_ratings[to_user_id]["success_games"] += 1
    else:
        user_ratings[to_user_id]["no_show"] += 1

    # Пересчитываем средний рейтинг
    scores = user_ratings[to_user_id]["scores"]
    user_ratings[to_user_id]["rating"] = sum(scores) / len(scores) if scores else 0.0

    return True


def format_rating(user_id):
    """Форматировать рейтинг для отображения"""
    rating_data = get_user_rating(user_id)

    if rating_data["games_count"] == 0:
        return "⭐ Новичок\n🎮 Игр: 0"

    rating_stars = rating_data["rating"]
    games = rating_data["games_count"]
    success = rating_data["success_games"]
    no_show = rating_data["no_show"]

    return (
        f"⭐ Рейтинг: {rating_stars:.1f}/5.0\n"
        f"🎮 Всего игр: {games}\n"
        f"✅ Успешных: {success}\n"
        f"❌ Неявок: {no_show}"
    )
