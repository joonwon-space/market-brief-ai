# embedder.py

from sentence_transformers import SentenceTransformer
from typing import List, Tuple

# 사전 학습된 E5 임베딩 모델 로딩
model = SentenceTransformer("intfloat/e5-base-v2")

def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
    """
    긴 텍스트를 일정한 단어 수 기준으로 청킹
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))
    return chunks

def embed_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[Tuple[str, List[float]]]:
    """
    텍스트를 청킹한 뒤 각 청크에 대해 임베딩 수행
    Returns: [(chunk_text, embedding_vector), ...]
    """
    chunks = chunk_text(text, chunk_size, overlap)
    embeddings = model.encode(chunks, convert_to_tensor=False)
    return list(zip(chunks, embeddings))
