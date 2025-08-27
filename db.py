import psycopg2
import psycopg2.extras
import json

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="market_brief_ai",  # 만든 DB 이름
        user="postgres",           # 만든 계정
        password="localhost12!@"   # 설정한 비밀번호
    )

def insert_chunk(file_id: str, chunk_index: int, content: str, embedding, metadata: dict = None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO report_chunks (file_id, chunk_index, content, embedding, metadata)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                file_id,
                chunk_index,
                content,
                embedding.tolist(),  # numpy array → list
                json.dumps(metadata) if metadata else None,
            )
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()
