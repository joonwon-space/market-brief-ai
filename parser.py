# parser.py
# ⭐️ 대체 라이브러리 'unstructured'를 사용하여 안정성을 높인 버전입니다.
from unstructured.partition.auto import partition

def convert_pdf_to_text(pdf_path: str) -> str:
    """
    unstructured 라이브러리를 사용하여 PDF에서 구조화된 텍스트를 추출합니다.
    - 표, 리스트, 문단 등을 인식하여 추출합니다.
    - strategy="hi_res"는 고해상도 모델을 사용하여 정확도를 높입니다.

    Parameters:
        pdf_path (str): 처리할 PDF 파일 경로

    Returns:
        str: 추출된 텍스트
    """
    print("unstructured 모델로 텍스트 추출 중... (초기 실행 시 모델 다운로드로 인해 시간이 걸릴 수 있습니다)")
    try:
        # 고해상도 전략으로 한국어, 영어를 포함하여 텍스트 추출
        elements = partition(filename=pdf_path, strategy="hi_res", languages=["kor", "eng"])
        # 추출된 모든 element의 text를 하나의 문자열로 합칩니다.
        text = "\n\n".join([str(el) for el in elements])
        print("✅ 텍스트 추출 완료.")
        return text
    except Exception as e:
        print(f"❌ unstructured(hi_res) 처리 중 오류 발생: {e}")
        # 오류 발생 시 기본 파서(fast)로 재시도
        print("기본 파서(fast)로 재시도합니다.")
        try:
            elements = partition(filename=pdf_path, strategy="fast", languages=["kor", "eng"])
            text = "\n\n".join([str(el) for el in elements])
            print("✅ 기본 파서로 텍스트 추출 완료.")
            return text
        except Exception as fallback_e:
            print(f"❌ 기본 파서 처리 중 오류 발생: {fallback_e}")
            return ""


def save_text(text: str, save_path: str):
    """텍스트를 파일에 저장합니다."""
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(text)

