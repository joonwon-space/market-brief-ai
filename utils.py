import os
from datetime import datetime

def get_date_str(date: datetime) -> str:
    return date.strftime("%Y%m%d")

def sanitize_filename(filename: str) -> str:
    return "".join(c for c in filename if c.isalnum() or c in (" ", "_", "-")).rstrip()

def get_data_path(subdir: str, date: datetime, create: bool = False) -> str:
    date_str = get_date_str(date)
    path = os.path.join("data", subdir, date_str)
    if create:
        os.makedirs(path, exist_ok=True)
    return path
