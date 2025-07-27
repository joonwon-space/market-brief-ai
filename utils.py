import os
from datetime import datetime

def get_date_str(date: datetime = None) -> str:
    if date is None:
        date = datetime.now()
    return date.strftime("%Y%m%d")

def get_data_path(base: str, date: datetime) -> str:
    date_str = get_date_str(date)
    path = os.path.join("data", base, date_str)
    os.makedirs(path, exist_ok=True)
    return path

def sanitize_filename(name: str) -> str:
    return name.replace("/", "_").replace(" ", "_").replace(":", "_")
