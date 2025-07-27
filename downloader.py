# downloader.py
import requests
import os
from utils import sanitize_filename, get_data_path
from datetime import datetime

def get_pdf_filename(company: str, date: str, title: str) -> str:
    base = sanitize_filename(f"{company}_{title}")
    return f"{base}.pdf"

def download_pdf(pdf_url: str, company: str, date: str, title: str, save_path: str = None):
    if not save_path:
        filename = get_pdf_filename(company, date, title)
        save_path = os.path.join(get_data_path("raw", datetime.strptime(date, "%Y-%m-%d")), filename)

    if os.path.exists(save_path):
        print(f"📁 이미 존재함 → {os.path.basename(save_path)}")
        return

    r = requests.get(pdf_url)
    if r.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(r.content)
        print(f"⬇️ 다운로드 완료: {os.path.basename(save_path)}")
    else:
        print(f"❌ 다운로드 실패: {pdf_url}")
