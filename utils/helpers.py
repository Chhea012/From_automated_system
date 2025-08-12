from datetime import datetime

def format_date_with_ordinal(date_obj: datetime) -> str:
    day = date_obj.day
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return f"{day}{suffix}{date_obj.strftime(' %B %Y')}"

def format_date_without_ordinal(date_obj: datetime) -> str:
    return date_obj.strftime("%d %B %Y")

def parse_ordinal_date(date_str: str) -> datetime:
    parts = date_str.split()
    day_str = parts[0].rstrip('stndrdth')
    return datetime.strptime(f"{day_str} {' '.join(parts[1:])}", "%d %B %Y")