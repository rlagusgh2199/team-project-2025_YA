"""
Flask 메인 애플리케이션
교내 길찾기 키오스크 백엔드 서버
"""
from flask import Flask, jsonify
from flask_cors import CORS
from config import SECRET_KEY, MAX_CONTENT_LENGTH
from routes.api import api

# Flask 앱 생성
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# CORS 설정 (프론트엔드와 통신을 위해)
CORS(app)

# API 블루프린트 등록
app.register_blueprint(api, url_prefix='/api')


@app.route('/', methods=['GET'])
def index():
    """루트 엔드포인트"""
    return jsonify({
        'message': '교내 길찾기 키오스크 백엔드 API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'upload': '/api/upload (POST)',
            'locations': '/api/locations (GET)',
            'route': '/api/route (POST)',
            'ask': '/api/ask (POST)',
            'excel_format': '/api/excel-format (GET)'
        }
    })


@app.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return jsonify({
        'success': False,
        'error': '요청한 리소스를 찾을 수 없습니다.'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500 에러 핸들러"""
    return jsonify({
        'success': False,
        'error': '서버 내부 오류가 발생했습니다.'
    }), 500


if __name__ == '__main__':
    # 리눅스 환경에서 실행
    # 개발 환경: app.run(host='0.0.0.0', port=5000, debug=True)
    # 프로덕션 환경: gunicorn 등을 사용 권장
    app.run(host='0.0.0.0', port=5000, debug=True)

