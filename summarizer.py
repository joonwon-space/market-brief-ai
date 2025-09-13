# summarizer.py
import os
import openai
from openai import OpenAI

# ⭐️ 1. OpenAI 클라이언트를 초기화합니다.
# API 키는 환경 변수('OPENAI_API_KEY')에서 가져옵니다.
try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except TypeError:
    print("❌ OPENAI_API_KEY가 설정되지 않았습니다. 환경 변수를 확인해주세요.")
    client = None

def summarize_text(text: str) -> str:
    """
    OpenAI API (GPT-4o mini)를 사용하여 텍스트를 요약합니다.
    """
    if not client:
        return "❌ 요약 생성 실패: OpenAI 클라이언트가 초기화되지 않았습니다."

    # 시스템 프롬프트는 OpenAI 모델에서도 효과적으로 작동합니다.
    system_prompt = """
당신은 증권사 리포트를 분석하는 전문가입니다.

아래는 리포트 본문입니다. 이 내용을 바탕으로 다음 항목을 명확하고 간결하게 정리해 주세요:

1.  **시장 상황 분석**: 현재 거시 경제, 특정 업종, 수급 상황은 어떠한가?
2.  **핵심 투자 전략**: 이러한 상황에서 어떤 투자 전략 또는 대응이 필요한가?
3.  **투자 심리**: 리포트에서 드러나는 전반적인 투자 심리는 어떠한가? (예: 낙관적, 보수적, 불안 등)
4.  **주요 트렌드/키워드**: 주목해야 할 국가, 산업, 기술, 테마는 무엇인가?
5.  **핵심 인사이트**: 이 리포트가 제공하는 가장 중요한 관찰이나 독창적인 인사이트는 무엇인가?
"""
    try:
        # ⭐️ 2. OpenAI API를 호출하는 부분입니다.
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 비용 효율적인 최신 모델 사용 (또는 "gpt-4-turbo")
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.5, # 응답의 창의성을 조절 (0에 가까울수록 사실 기반)
            max_tokens=1024  # 최대 응답 길이
        )
        return response.choices[0].message.content
    # ⭐️ 3. OpenAI API 관련 예외 처리입니다.
    except openai.APIConnectionError as e:
        error_msg = f"❌ 요약 생성 실패: OpenAI 서버 연결에 실패했습니다 - {e}"
        print(error_msg)
        return error_msg
    except openai.RateLimitError as e:
        error_msg = f"❌ 요약 생성 실패: OpenAI API 사용량 한도를 초과했습니다 - {e}"
        print(error_msg)
        return error_msg
    except openai.APIStatusError as e:
        error_msg = f"❌ 요약 생성 실패: OpenAI API 오류 발생 (상태 코드: {e.status_code}) - {e.response}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"❌ 요약 생성 중 알 수 없는 오류 발생: {e}"
        print(error_msg)
        return error_msg


def save_summary(summary: str, path: str):
    """요약 내용을 파일에 저장합니다."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(summary)

