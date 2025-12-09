"""
설정 파일
환경 변수나 설정값을 관리합니다.
"""
import os
from pathlib import Path

# 기본 경로 설정 (리눅스 환경 고려)
BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / 'data' / 'uploads'
DATA_FOLDER = BASE_DIR / 'data'
JSON_DATA_PATH = DATA_FOLDER / 'locations.json'

# 디렉토리 생성
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
DATA_FOLDER.mkdir(parents=True, exist_ok=True)

# Flask 설정
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 최대 파일 크기

# LLM 설정 (환경 변수로 설정 가능)
LLM_API_URL = os.environ.get('LLM_API_URL', 'http://localhost:11434/api/generate')  # Ollama 기본 URL
LLM_MODEL = os.environ.get('LLM_MODEL', 'llama3')
LLM_TIMEOUT = int(os.environ.get('LLM_TIMEOUT', '30'))

# 허용된 파일 확장자
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    """파일 확장자 검증"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

