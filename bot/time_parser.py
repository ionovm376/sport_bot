from datetime import datetime, timedelta
import re


def parse_game_time(time_str: str) -> datetime | None:
    """
    Парсит время игры из текста пользователя.
    Возвращает datetime объект в UTC или None если не удалось распарсить.
    """
    time_str = time_str.lower().strip()
    # Московское время (UTC+3)
    now_moscow = datetime.now()

    # Паттерны для парсинга

    # "Сегодня 19:00" или "сегодня в 19:00"
    match = re.search(r'сегодня\s+(?:в\s+)?(\d{1,2}):(\d{2})', time_str)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            game_time_moscow = now_moscow.replace(hour=hour, minute=minute, second=0, microsecond=0)
            # Конвертируем в UTC (Москва = UTC+3)
            return game_time_moscow - timedelta(hours=3)

    # "Завтра 14:30" или "завтра в 14:30"
    match = re.search(r'завтра\s+(?:в\s+)?(\d{1,2}):(\d{2})', time_str)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            tomorrow_moscow = now_moscow + timedelta(days=1)
            game_time_moscow = tomorrow_moscow.replace(hour=hour, minute=minute, second=0, microsecond=0)
            # Конвертируем в UTC
            return game_time_moscow - timedelta(hours=3)

    # "07.05 в 10:00" или "7.5 10:00"
    match = re.search(r'(\d{1,2})\.(\d{1,2})\s+(?:в\s+)?(\d{1,2}):(\d{2})', time_str)
    if match:
        day, month, hour, minute = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
        if 1 <= day <= 31 and 1 <= month <= 12 and 0 <= hour <= 23 and 0 <= minute <= 59:
            try:
                year = now_moscow.year
                # Если дата в прошлом этого года, берём следующий год
                game_time_moscow = datetime(year, month, day, hour, minute)
                if game_time_moscow < now_moscow:
                    game_time_moscow = datetime(year + 1, month, day, hour, minute)
                # Конвертируем в UTC
                return game_time_moscow - timedelta(hours=3)
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
                    year = now_moscow.year
                    game_time_moscow = datetime(year, month_num, day, hour, minute)
                    if game_time_moscow < now_moscow:
                        game_time_moscow = datetime(year + 1, month_num, day, hour, minute)
                    # Конвертируем в UTC
                    return game_time_moscow - timedelta(hours=3)
                except ValueError:
                    pass

    return None


def calculate_expiry_time(game_time: datetime) -> datetime:
    """
    Вычисляет время удаления игры (через 2 часа после времени игры).
    game_time уже в UTC.
    """
    return game_time + timedelta(hours=2)
