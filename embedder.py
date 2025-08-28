# embedder.py
from sentence_transformers import SentenceTransformer
from typing import List, Tuple
import re

# 최신 멀티랭 임베딩 모델 (BGE-m3)
model = SentenceTransformer("BAAI/bge-m3", device="cpu")

def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
    """
    텍스트를 일정 단어 수 기준으로 청킹 (중첩 overlap 포함)
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))
    return chunks

def is_valid_chunk(text: str, min_length: int = 30, max_num_ratio: float = 0.5) -> bool:
    """
    유효하지 않은 chunk (짧거나 숫자/boilerplate 비율이 높은 경우) 제거
    """
    if len(text) < min_length:
        return False
    
    # 숫자 비율 계산
    num_ratio = sum(c.isdigit() for c in text) / max(len(text), 1)
    if num_ratio > max_num_ratio:
        return False

    # boilerplate 문구 제거
    boilerplates = [
        "무단복제", "재배포", "투자판단", "책임지지 않습니다", 
        "증빙으로 사용될 수 없습니다"
    ]
    if any(bp in text for bp in boilerplates):
        return False

    return True

def embed_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[Tuple[str, list]]:
    """
    텍스트 → 청킹 → 필터링 → 임베딩
    """
    chunks = chunk_text(text, chunk_size, overlap)
    valid_chunks = [c for c in chunks if is_valid_chunk(c)]

    embeddings = model.encode(valid_chunks, convert_to_tensor=False)
    return list(zip(valid_chunks, embeddings))
