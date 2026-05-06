from datetime import datetime, timedelta
import re


def parse_game_time(time_str: str) -> datetime | None:
    """
    Парсит время игры из текста пользователя.
    Возвращает datetime объект или None если не удалось распарсить.
    """
    time_str = time_str.lower().strip()
    now = datetime.now()

    # Паттерны для парсинга

    # "Сегодня 19:00" или "сегодня в 19:00"
    match = re.search(r'сегодня\s+(?:в\s+)?(\d{1,2}):(\d{2})', time_str)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # "Завтра 14:30" или "завтра в 14:30"
    match = re.search(r'завтра\s+(?:в\s+)?(\d{1,2}):(\d{2})', time_str)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            tomorrow = now + timedelta(days=1)
            return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # "07.05 в 10:00" или "7.5 10:00"
    match = re.search(r'(\d{1,2})\.(\d{1,2})\s+(?:в\s+)?(\d{1,2}):(\d{2})', time_str)
    if match:
        day, month, hour, minute = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
        if 1 <= day <= 31 and 1 <= month <= 12 and 0 <= hour <= 23 and 0 <= minute <= 59:
            try:
                year = now.year
                # Если дата в прошлом этого года, берём следующий год
                game_date = datetime(year, month, day, hour, minute)
                if game_date < now:
                    game_date = datetime(year + 1, month, day, hour, minute)
                return game_date
            except ValueError:
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
                    year = now.year
                    game_date = datetime(year, month_num, day, hour, minute)
                    if game_date < now:
                        game_date = datetime(year + 1, month_num, day, hour, minute)
                    return game_date
                except ValueError:
                    pass

    return None


def calculate_expiry_time(game_time: datetime) -> datetime:
    """
    Вычисляет время удаления игры (через 2 часа после времени игры).
    """
    return game_time + timedelta(hours=2)
