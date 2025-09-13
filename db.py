# db.py
import psycopg2
import psycopg2.extras
import json
from pgvector.psycopg2 import register_vector # pgvector에서 register_vector를 임포트합니다.
import os

def get_connection():
    """PostgreSQL 데이터베이스에 연결합니다."""
    # 실제 운영 환경에서는 보안을 위해 환경 변수에서 연결 정보를 가져오는 것이 좋습니다.
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "market_brief_ai"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "localhost12!@")
    )

def insert_chunk(file_id: str, chunk_index: int, content: str, embedding, metadata: dict = None):
    """
    텍스트 청크와 임베딩 벡터를 데이터베이스에 안전하게 삽입합니다.
    동일한 file_id와 chunk_index가 이미 존재할 경우, 중복 삽입을 방지합니다.
    """
    conn = None
    try:
        conn = get_connection()
        # 연결마다 pgvector 타입을 등록해야 합니다.
        register_vector(conn)
        cur = conn.cursor()

        # numpy 배열일 경우 파이썬 리스트로 변환합니다.
        embedding_list = embedding.tolist() if hasattr(embedding, "tolist") else embedding

        # SQL 인젝션을 방지하기 위해 파라미터화된 쿼리를 사용합니다.
        # ON CONFLICT 절은 중복 데이터 삽입 시 오류를 방지합니다.
        sql = """
            INSERT INTO report_chunks (file_id, chunk_index, content, embedding, metadata)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (file_id, chunk_index) DO NOTHING;
        """
        
        cur.execute(
            sql,
            (
                file_id,
                chunk_index,
                content,
                embedding_list, # 벡터 리스트를 직접 전달합니다.
                json.dumps(metadata) if metadata else None,
            )
        )
        conn.commit()
    except psycopg2.Error as e:
        # 데이터베이스 오류 발생 시 로그를 남기고 롤백합니다.
        print(f"데이터베이스 오류 발생: {e}")
        if conn:
            conn.rollback()
    finally:
        # 모든 작업 후 연결을 안전하게 닫습니다.
        if conn:
            cur.close()
            conn.close()

