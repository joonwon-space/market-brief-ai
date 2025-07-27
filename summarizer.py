import ollama
import os

def summarize_text(text: str) -> str:
    system_prompt = """
당신은 증권사 리포트를 분석하는 전문가입니다.

아래는 리포트 본문입니다. 이 내용을 바탕으로 다음 항목을 정리해 주세요:

1. 현재 시장 상황은 어떤가요? (거시경제, 업종, 수급 등)
2. 어떤 대응 전략이 필요한가요? (투자 관점에서)
3. 리포트에서 나타난 투자 심리는 어떤 상태인가요? (낙관/불안/보수 등)
4. 주목해야 할 트렌드나 키워드는 무엇인가요? (국가, 산업, 테마 중심)
5. 이 분석에서 특히 의미 있는 관찰 지점이나 인사이트는 무엇인가요?
"""
    response = ollama.chat(model="llama3", messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ])
    return response["message"]["content"]

def save_summary(summary: str, path: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(summary)
