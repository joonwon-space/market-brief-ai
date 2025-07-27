import boto3
import os

# 환경변수 또는 ~/.aws/credentials에서 접근
s3 = boto3.client('s3')

BUCKET_NAME = 'market-brief-ai-data'

def upload_file(local_path: str, s3_key: str):
    """
    파일을 S3에 업로드
    local_path: 로컬 파일 경로
    s3_key: S3 내 경로 (예: data/raw/20250727/...)
    """
    try:
        s3.upload_file(local_path, BUCKET_NAME, s3_key)
        print(f"✅ S3 업로드 성공: s3://{BUCKET_NAME}/{s3_key}")
    except Exception as e:
        print(f"❌ S3 업로드 실패: {local_path} → {s3_key}")
        print(e)
