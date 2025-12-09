#!/bin/bash
# 리눅스 환경에서 설치 및 실행 스크립트

echo "교내 길찾기 키오스크 백엔드 설치 중..."

# Python 버전 확인
python3 --version

# 가상환경 생성 (선택사항)
if [ ! -d "venv" ]; then
    echo "가상환경 생성 중..."
    python3 -m venv venv
fi

# 가상환경 활성화
echo "가상환경 활성화 중..."
source venv/bin/activate

# pip 업그레이드
echo "pip 업그레이드 중..."
pip install --upgrade pip

# 의존성 설치
echo "의존성 설치 중..."
pip install -r requirements.txt

echo "설치 완료!"
echo ""
echo "서버 실행 방법:"
echo "  python app.py"
echo ""
echo "또는 Gunicorn 사용:"
echo "  pip install gunicorn"
echo "  gunicorn -w 4 -b 0.0.0.0:5000 app:app"

