import argparse
from datetime import datetime
from crawler import get_report_list
from downloader import download_pdf, get_pdf_filename
from parser import extract_text_from_pdf, save_text
from summarizer import summarize_text, save_summary
from utils import get_data_path, get_date_str, sanitize_filename
import os

def get_all_paths(date: datetime, filename: str):
    pdf_path = os.path.join(get_data_path("raw", date), filename + ".pdf")
    txt_path = os.path.join(get_data_path("text", date), filename + ".txt")
    summary_path = os.path.join(get_data_path("summary", date), filename + ".summary.txt")
    return pdf_path, txt_path, summary_path

def parse_args():
    parser = argparse.ArgumentParser(description="ETF 리포트 자동 분석기")
    parser.add_argument("--date", help="분석할 날짜 (YYYY-MM-DD)", default=None)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    # 날짜 지정
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print("❌ 날짜 형식이 잘못되었습니다. 예: --date 2025-07-25")
            exit(1)
    else:
        target_date = datetime.today()

    reports = get_report_list(target_date.strftime("%Y-%m-%d"))
    if not reports:
        print("📭 해당 날짜의 리포트가 없습니다.")
        exit()

    for i, report in enumerate(reports):
        print(f"\n{i+1}. {report['company']} - {report['title']}")
        base_filename = sanitize_filename(f"{report['company']}_{report['title']}")
        pdf_path, txt_path, summary_path = get_all_paths(target_date, base_filename)

        # 1️⃣ PDF 다운로드
        if os.path.exists(pdf_path):
            print(f"📁 PDF 있음 → 스킵: {os.path.basename(pdf_path)}")
        else:
            download_pdf(
                pdf_url=report["pdf_url"],
                company=report["company"],
                date=report["date"],
                title=report["title"],
                save_path=pdf_path
            )

        # 2️⃣ 텍스트 추출
        if os.path.exists(txt_path):
            print(f"📝 텍스트 있음 → 스킵: {os.path.basename(txt_path)}")
        else:
            text = extract_text_from_pdf(pdf_path)
            save_text(text, txt_path)

        # 3️⃣ 요약
        if os.path.exists(summary_path):
            print(f"🔍 요약 있음 → 스킵: {os.path.basename(summary_path)}")
        else:
            text = open(txt_path, encoding="utf-8").read()
            short_text = text[:3000]
            summary = summarize_text(short_text)
            save_summary(summary, summary_path)
            print(f"✅ 요약 저장: {summary_path}")
