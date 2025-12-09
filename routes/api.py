"""
API 라우터
Flask 엔드포인트를 정의합니다.
"""
from flask import Blueprint, request, jsonify, send_file
from pathlib import Path
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, allowed_file
from services.excel_parser import ExcelParser
from services.llm_service import LLMService
from services.path_finder import PathFinder
from models.location import LocationModel

api = Blueprint('api', __name__)

# 서비스 인스턴스 생성
excel_parser = ExcelParser()
llm_service = LLMService()
path_finder = PathFinder()
location_model = LocationModel()


@api.route('/health', methods=['GET'])
def health_check():
    """서비스 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'message': 'Campus Navigation Backend is running'
    })


@api.route('/upload', methods=['POST'])
def upload_excel():
    """
    엑셀 파일 업로드 및 파싱
    
    요청 형식:
    - multipart/form-data
    - 파일 필드명: 'file'
    """
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': '파일이 없습니다.'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': '파일명이 없습니다.'
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': '엑셀 파일(.xlsx, .xls)만 업로드 가능합니다.'
        }), 400
    
    try:
        # 파일 저장
        filename = secure_filename(file.filename)
        file_path = UPLOAD_FOLDER / filename
        file.save(str(file_path))
        
        # 엑셀 파싱
        result = excel_parser.parse_excel(file_path)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f'{result["saved_count"]}개의 장소가 등록되었습니다.',
                'saved_count': result['saved_count'],
                'total_rows': result.get('total_rows', 0),
                'errors': result.get('errors', [])
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', '파싱 중 오류가 발생했습니다.')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'파일 처리 중 오류 발생: {str(e)}'
        }), 500


@api.route('/locations', methods=['GET'])
def get_locations():
    """
    모든 장소 목록 조회
    
    쿼리 파라미터:
    - search: 검색어 (선택)
    """
    search_query = request.args.get('search', '')
    
    if search_query:
        locations = location_model.search_locations(search_query)
    else:
        locations = location_model.get_all_locations()
    
    return jsonify({
        'success': True,
        'count': len(locations),
        'locations': locations
    })


@api.route('/locations/<int:location_id>', methods=['GET'])
def get_location(location_id):
    """특정 장소 정보 조회"""
    location = location_model.get_location_by_id(location_id)
    
    if not location:
        return jsonify({
            'success': False,
            'error': '장소를 찾을 수 없습니다.'
        }), 404
    
    return jsonify({
        'success': True,
        'location': location
    })


@api.route('/route', methods=['POST'])
def find_route():
    """
    경로 찾기
    
    요청 본문 (JSON):
    {
        "from": "출발지명",
        "to": "목적지명"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': '요청 본문이 없습니다.'
        }), 400
    
    from_location = data.get('from')
    to_location = data.get('to')
    
    if not from_location or not to_location:
        return jsonify({
            'success': False,
            'error': '출발지와 목적지를 모두 입력해주세요.'
        }), 400
    
    result = path_finder.find_path(from_location, to_location)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 404


@api.route('/ask', methods=['POST'])
def ask_llm():
    """
    LLM을 이용한 자연어 질의응답
    
    요청 본문 (JSON):
    {
        "query": "도서관으로 가는 길 알려줘"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': '요청 본문이 없습니다.'
        }), 400
    
    query = data.get('query', '')
    
    if not query:
        return jsonify({
            'success': False,
            'error': '질문을 입력해주세요.'
        }), 400
    
    result = llm_service.ask_route(query)
    
    return jsonify({
        'success': True,
        **result
    })


@api.route('/excel-format', methods=['GET'])
def get_excel_format():
    """엑셀 파일 형식 안내"""
    format_info = excel_parser.get_sample_excel_format()
    
    return jsonify({
        'success': True,
        **format_info
    })


@api.route('/data/export', methods=['GET'])
def export_data():
    """현재 저장된 데이터를 JSON으로 내보내기"""
    locations = location_model.get_all_locations()
    
    return jsonify({
        'success': True,
        'count': len(locations),
        'locations': locations
    })

