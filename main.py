# main.py
import argparse
from datetime import datetime, timedelta
import os

from crawler import get_report_list
from downloader import download_pdf
# ⭐️ 수정된 부분: unstructured를 사용하는 새 함수를 import합니다.
from parser import convert_pdf_to_text, save_text
from summarizer import summarize_text, save_summary
from uploader import upload_file
from utils import get_data_path, get_date_str, sanitize_filename
from embedder import embed_text
from db import insert_chunk

def get_all_paths(date: datetime, filename: str, create=False):
    """필요한 모든 파일 경로를 생성하여 반환합니다."""
    pdf_path = os.path.join(get_data_path("raw", date, create=create), filename + ".pdf")
    txt_path = os.path.join(get_data_path("text", date, create=create), filename + ".txt")
    sum_path = os.path.join(get_data_path("summary", date, create=create), filename + ".sum") # 요약 경로 추가
    return pdf_path, txt_path, sum_path

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
        print(f"\n{'='*40}\n{i+1}. {report['company']} - {report['title']}")
        base_filename = sanitize_filename(f"{report['company']}_{report['title']}")

        pdf_path, txt_path, sum_path = get_all_paths(target_date, base_filename, create=False)

        # 1️⃣ PDF 다운로드
        if not os.path.exists(pdf_path):
            pdf_path, _, _ = get_all_paths(target_date, base_filename, create=True)
            download_pdf(
                pdf_url=report["pdf_url"],
                company=report["company"],
                date=report["date"],
                title=report["title"],
                save_path=pdf_path
            )
        else:
            print(f"📁 PDF 있음 → 스킵: {os.path.basename(pdf_path)}")

        if not os.path.exists(pdf_path):
            print(f"❌ PDF 다운로드 실패, 다음 리포트로 넘어갑니다.")
            continue
            
        size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        print(f"📊 PDF 파일 크기: {size_mb:.2f} MB")
        upload_file(pdf_path, f"data/raw/{date_str}/{os.path.basename(pdf_path)}")

        # 2️⃣ 텍스트 추출 (unstructured 사용)
        if not os.path.exists(txt_path):
            _, txt_path, _ = get_all_paths(target_date, base_filename, create=True)
            try:
                # ⭐️ 수정된 부분: 변경된 함수를 호출합니다.
                text = convert_pdf_to_text(pdf_path)
                if text:
                    save_text(text, txt_path)
                else:
                    print("❌ 텍스트 추출 실패: 내용이 비어있습니다.")
                    continue
            except Exception as e:
                print(f"❌ 텍스트 추출 프로세스 실패: {e}")
                continue
        else:
            print(f"📝 텍스트 있음 → 스킵: {os.path.basename(txt_path)}")
            
        if not os.path.exists(txt_path):
            print(f"❌ 텍스트 파일이 없어 다음 단계를 진행할 수 없습니다.")
            continue

        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()

        # 3️⃣ 리포트 요약
        if not os.path.exists(sum_path):
            print("🤖 리포트 요약 생성 중...")
            _, _, sum_path = get_all_paths(target_date, base_filename, create=True)
            summary = summarize_text(text)
            
            # ⭐️ 요약 실패 시 다음 단계로 넘어가도록 수정
            if "요약 생성 실패" in summary:
                print("⚠️ 요약에 실패하여 다음 단계(임베딩)로 넘어갑니다.")
            else:
                save_summary(summary, sum_path)
                print(f"✅ 요약 완료: {os.path.basename(sum_path)}")
                if os.path.exists(sum_path):
                    upload_file(sum_path, f"data/summary/{date_str}/{os.path.basename(sum_path)}")
        else:
            print(f"🤖 요약 파일 있음 → 스킵: {os.path.basename(sum_path)}")

        # 4️⃣ 임베딩 및 DB 저장
        print("🧠 임베딩 및 DB 저장 중...")
        try:
            chunks_and_vectors = embed_text(text)
            if not chunks_and_vectors:
                print("⚠️ 유효한 청크가 없어 임베딩을 건너뜁니다.")
                continue

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
            print("✅ DB 저장 완료.")
        except Exception as e:
            print(f"🚨 임베딩 또는 DB 저장 중 오류 발생: {e}")

if __name__ == "__main__":
    args = parse_args()
    if args.date:
        run_for_date(datetime.strptime(args.date, "%Y-%m-%d"))
    elif args.datefrom and args.dateto:
        start = datetime.strptime(args.datefrom, "%Y-%m-%d")
        end = datetime.strptime(args.dateto, "%Y-%m-%d")
        cur = start
        while cur <= end:
            run_for_date(cur)
            cur += timedelta(days=1)
    else:
        run_for_date(datetime.today())

