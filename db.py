# db.py
import psycopg2
import psycopg2.extras
import json


def get_connection():
    """PostgreSQL 연결"""
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="market_brief_ai",
        user="postgres",
        password="localhost12!@"
    )


def get_dict_cursor(conn):
    """딕셔너리 형태 결과 반환 커서"""
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def insert_chunk(file_id: str, chunk_index: int, content: str, embedding, metadata: dict = None):
    """
    report_chunks 테이블에 청크 삽입
    embedding을 f-string으로 직접 SQL에 삽입 (::vector)
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        # numpy → list 변환
        embedding_list = embedding.tolist() if hasattr(embedding, "tolist") else embedding

        # list → 문자열 "[0.1,0.2,0.3,...]"
        embedding_str = "[" + ",".join(str(float(x)) for x in embedding_list) + "]"

        # ⚠️ embedding_str만 직접 SQL에 삽입
        sql = f"""
            INSERT INTO report_chunks (file_id, chunk_index, content, embedding, metadata)
            VALUES (%s, %s, %s, '{embedding_str}'::vector, %s)
        """

        cur.execute(
            sql,
            (
                file_id,
                chunk_index,
                content,
                json.dumps(metadata) if metadata else None,
            )
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()
