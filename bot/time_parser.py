from datetime import datetime, timedelta
import pytz
import re

# Московский часовой пояс
MOSCOW_TZ = pytz.timezone('Europe/Moscow')


def parse_game_time(time_str: str) -> datetime | None:
    """
    Парсит время игры из текста пользователя (московское время).
    Возвращает datetime объект в UTC или None если не удалось распарсить.
    """
    time_str = time_str.lower().strip()

    # Текущее время в Москве
    now_moscow = datetime.now(MOSCOW_TZ)

    # "Сегодня 19:00" или "сегодня в 19:00"
    match = re.search(r'сегодня\s+(?:в\s+)?(\d{1,2}):(\d{2})', time_str)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            # Создаём время на сегодня
            game_time_moscow = now_moscow.replace(hour=hour, minute=minute, second=0, microsecond=0)
            # Конвертируем в UTC
            return game_time_moscow.astimezone(pytz.UTC).replace(tzinfo=None)

    # "Завтра 14:30" или "завтра в 14:30"
    match = re.search(r'завтра\s+(?:в\s+)?(\d{1,2}):(\d{2})', time_str)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            # Создаём время на завтра
            tomorrow_moscow = now_moscow + timedelta(days=1)
            game_time_moscow = tomorrow_moscow.replace(hour=hour, minute=minute, second=0, microsecond=0)
            # Конвертируем в UTC
            return game_time_moscow.astimezone(pytz.UTC).replace(tzinfo=None)

    # "07.05 в 10:00" или "7.5 10:00"
    match = re.search(r'(\d{1,2})\.(\d{1,2})\s+(?:в\s+)?(\d{1,2}):(\d{2})', time_str)
    if match:
        day, month, hour, minute = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
        if 1 <= day <= 31 and 1 <= month <= 12 and 0 <= hour <= 23 and 0 <= minute <= 59:
            try:
                year = now_moscow.year
                # Создаём naive datetime, потом добавляем часовой пояс
                game_time_naive = datetime(year, month, day, hour, minute)
                game_time_moscow = MOSCOW_TZ.localize(game_time_naive)

                # Если дата в прошлом, берём следующий год
                if game_time_moscow < now_moscow:
                    game_time_naive = datetime(year + 1, month, day, hour, minute)
                    game_time_moscow = MOSCOW_TZ.localize(game_time_naive)

                # Конвертируем в UTC
                return game_time_moscow.astimezone(pytz.UTC).replace(tzinfo=None)
            except (ValueError, pytz.exceptions.NonExistentTimeError, pytz.exceptions.AmbiguousTimeError):
                pass

    # "10 мая 18:00" или "10 мая в 18:00"
    months = {
        'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
        'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
        'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
    }
    for month_name, month_num in months.items():
        match = re.search(rf'(\d{{1,2}})\s+{month_name}\s+(?:в\s+)?(\d{{1,2}}):(\d{{2}})', time_str)
        if match:
            day, hour, minute = int(match.group(1)), int(match.group(2)), int(match.group(3))
            if 1 <= day <= 31 and 0 <= hour <= 23 and 0 <= minute <= 59:
                try:
                    year = now_moscow.year
                    game_time_naive = datetime(year, month_num, day, hour, minute)
                    game_time_moscow = MOSCOW_TZ.localize(game_time_naive)

                    # Если дата в прошлом, берём следующий год
                    if game_time_moscow < now_moscow:
                        game_time_naive = datetime(year + 1, month_num, day, hour, minute)
                        game_time_moscow = MOSCOW_TZ.localize(game_time_naive)

                    # Конвертируем в UTC
                    return game_time_moscow.astimezone(pytz.UTC).replace(tzinfo=None)
                except (ValueError, pytz.exceptions.NonExistentTimeError, pytz.exceptions.AmbiguousTimeError):
                    pass

    return None


def calculate_expiry_time(game_time: datetime) -> datetime:
    """
    Вычисляет время удаления игры (через 2 часа после времени игры).
    game_time уже в UTC.
    """
    return game_time + timedelta(hours=2)
