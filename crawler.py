import requests
from datetime import datetime

def get_report_list(target_date: str = None):
    """
    ETFCheck 리포트를 가져오되, 특정 날짜만 필터링합니다.
    
    Parameters:
        target_date (str): "YYYY-MM-DD" 형식의 날짜 (기본은 오늘)

    Returns:
        list[dict]: 리포트 목록
    """
    url = "https://www.etfcheck.co.kr/report/getReport?SHOW=2"
    headers = {
        "Referer": "https://www.etfcheck.co.kr/report/invest/main",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0"
    }

    resp = requests.get(url, headers=headers)
    data = resp.json()

    if target_date is None:
        target_date = datetime.today().strftime("%Y-%m-%d")

    reports = []

    for item in data.get("results", []):
        report_date = item["REPORT_DATE"][:10]

        if report_date != target_date:
            continue

        title = item["TITLE"]
        company = item["COMPANY_NAME"]
        file_name = item["FILE_NAME"]
        year_month = file_name[:6]
        pdf_url = f"https://www.etfcheck.co.kr/upload/file/{year_month}/{file_name}"

        reports.append({
            "title": title,
            "date": report_date,
            "company": company,
            "pdf_url": pdf_url
        })

    return reports
