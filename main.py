import argparse
from datetime import datetime, timedelta
import os

from crawler import get_report_list
from downloader import download_pdf
from parser import extract_text_from_pdf, save_text
from uploader import upload_file
from utils import get_data_path, get_date_str, sanitize_filename
from embedder import embed_text
from db import insert_chunk   # ✅ DB 저장 함수


def get_all_paths(date: datetime, filename: str, create=False):
    pdf_path = os.path.join(get_data_path("raw", date, create=create), filename + ".pdf")
    txt_path = os.path.join(get_data_path("text", date, create=create), filename + ".txt")
    return pdf_path, txt_path


def parse_args():
    parser = argparse.ArgumentParser(description="ETF 리포트 자동 분석기")
    parser.add_argument("--date", help="단일 날짜 분석 (YYYY-MM-DD)")
    parser.add_argument("--datefrom", help="시작 날짜 (YYYY-MM-DD)")
    parser.add_argument("--dateto", help="종료 날짜 (YYYY-MM-DD)")
    return parser.parse_args()


def run_for_date(target_date: datetime):
    date_str = get_date_str(target_date)
    reports = get_report_list(target_date.strftime("%Y-%m-%d"))
    if not reports:
        print(f"\n📭 {date_str} 리포트 없음")
        return

    print(f"\n📅 {date_str} 리포트 수: {len(reports)}")
    for i, report in enumerate(reports):
        print(f"\n{i+1}. {report['company']} - {report['title']}")
        base_filename = sanitize_filename(f"{report['company']}_{report['title']}")

        # create=False → 파일 저장할 때만 폴더 생성
        pdf_path, txt_path = get_all_paths(target_date, base_filename, create=False)

        # 1️⃣ PDF 다운로드
        if os.path.exists(pdf_path):
            print(f"📁 PDF 있음 → 스킵: {os.path.basename(pdf_path)}")
        else:
            pdf_path, _ = get_all_paths(target_date, base_filename, create=True)
            download_pdf(
                pdf_url=report["pdf_url"],
                company=report["company"],
                date=report["date"],
                title=report["title"],
                save_path=pdf_path
            )

        if os.path.exists(pdf_path):
            size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
            print(f"📊 PDF 파일 크기: {size_mb:.2f} MB")
            upload_file(pdf_path, f"data/raw/{date_str}/{os.path.basename(pdf_path)}")

        # 2️⃣ 텍스트 추출
        if os.path.exists(txt_path):
            print(f"📝 텍스트 있음 → 스킵: {os.path.basename(txt_path)}")
        else:
            _, txt_path = get_all_paths(target_date, base_filename, create=True)
            text = extract_text_from_pdf(pdf_path)
            save_text(text, txt_path)

        if os.path.exists(txt_path):
            upload_file(txt_path, f"data/text/{date_str}/{os.path.basename(txt_path)}")

        # 3️⃣ 임베딩 → PostgreSQL 저장
        with open(txt_path, encoding="utf-8") as f:
            text = f.read()

        # 3️⃣ 임베딩 → PostgreSQL 저장
        try:
            chunks_and_vectors = embed_text(text)
            print(f"✅ 임베딩 완료: {len(chunks_and_vectors)} chunks 생성")

            for idx, (chunk, vector) in enumerate(chunks_and_vectors):
                metadata = {
                    "company": report["company"],
                    "title": report["title"],
                    "date": report["date"]
                }
                insert_chunk(
                    file_id=base_filename,
                    chunk_index=idx,
                    content=chunk,
                    embedding=vector,
                    metadata=metadata
                )
        except RuntimeError as e:
            err_msg = str(e)
            if "Invalid buffer size" in err_msg:
                print(f"🚨 {base_filename} 임베딩 스킵: {err_msg}")
            else:
                raise

if __name__ == "__main__":
    args = parse_args()

    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d")
            run_for_date(target_date)
        except ValueError:
            print("❌ 날짜 형식 오류: --date YYYY-MM-DD")
            exit(1)

    elif args.datefrom and args.dateto:
        try:
            start = datetime.strptime(args.datefrom, "%Y-%m-%d")
        except ValueError:
            print("❌ 시작 날짜 형식 오류: --datefrom YYYY-MM-DD")
            exit(1)
        try:
            end = datetime.strptime(args.dateto, "%Y-%m-%d")
        except ValueError:
            print("❌ 종료 날짜 형식 오류: --dateto YYYY-MM-DD")
            exit(1)

        if start > end:
            print("❌ 시작 날짜가 종료 날짜보다 이후입니다.")
            exit(1)

        cur = start
        while cur <= end:
            run_for_date(cur)
            cur += timedelta(days=1)

    else:
        run_for_date(datetime.today())
