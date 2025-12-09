"""
엑셀 파일 파싱 서비스
엑셀 파일을 읽어서 JSON 파일에 저장합니다.
"""
import pandas as pd
from typing import List, Dict
from pathlib import Path
from models.location import LocationModel


class ExcelParser:
    """엑셀 파일을 파싱하여 JSON 파일에 저장"""
    
    def __init__(self):
        self.location_model = LocationModel()
    
    def parse_excel(self, file_path: Path) -> Dict:
        """
        엑셀 파일을 파싱하여 JSON 파일에 저장
        
        예상 엑셀 형식:
        - name: 장소명
        - building_name: 건물명
        - floor: 층수
        - room_number: 호수
        - x_coordinate: X 좌표
        - y_coordinate: Y 좌표
        - description: 설명
        - category: 카테고리
        
        Returns:
            Dict: 파싱 결과 (성공 여부, 저장된 레코드 수 등)
        """
        try:
            # 엑셀 파일 읽기
            df = pd.read_excel(file_path)
            
            # 기존 데이터 삭제 (선택사항 - 필요시 주석 처리)
            # self.location_model.clear_all_locations()
            
            saved_count = 0
            errors = []
            
            # 각 행을 JSON 파일에 저장
            for index, row in df.iterrows():
                try:
                    location_data = {
                        'name': str(row.get('name', row.get('장소명', ''))),
                        'building_name': str(row.get('building_name', row.get('건물명', ''))),
                        'floor': self._safe_int(row.get('floor', row.get('층수', None))),
                        'room_number': str(row.get('room_number', row.get('호수', ''))),
                        'x_coordinate': self._safe_float(row.get('x_coordinate', row.get('x좌표', None))),
                        'y_coordinate': self._safe_float(row.get('y_coordinate', row.get('y좌표', None))),
                        'description': str(row.get('description', row.get('설명', ''))),
                        'category': str(row.get('category', row.get('카테고리', '')))
                    }
                    
                    # 필수 필드 검증
                    if not location_data['name']:
                        errors.append(f"행 {index + 2}: 장소명이 없습니다.")
                        continue
                    
                    self.location_model.add_location(location_data)
                    saved_count += 1
                    
                except Exception as e:
                    errors.append(f"행 {index + 2}: {str(e)}")
            
            return {
                'success': True,
                'saved_count': saved_count,
                'total_rows': len(df),
                'errors': errors
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'saved_count': 0
            }
    
    def _safe_int(self, value):
        """안전하게 정수로 변환"""
        if pd.isna(value) or value == '':
            return None
        try:
            return int(float(value))
        except:
            return None
    
    def _safe_float(self, value):
        """안전하게 실수로 변환"""
        if pd.isna(value) or value == '':
            return None
        try:
            return float(value)
        except:
            return None
    
    def get_sample_excel_format(self) -> Dict:
        """예상 엑셀 형식 샘플 반환"""
        return {
            'columns': [
                'name', 'building_name', 'floor', 'room_number',
                'x_coordinate', 'y_coordinate', 'description', 'category'
            ],
            'korean_columns': [
                '장소명', '건물명', '층수', '호수',
                'x좌표', 'y좌표', '설명', '카테고리'
            ],
            'description': {
                'name': '장소명 (필수)',
                'building_name': '건물명',
                'floor': '층수 (숫자)',
                'room_number': '호수',
                'x_coordinate': 'X 좌표 (숫자)',
                'y_coordinate': 'Y 좌표 (숫자)',
                'description': '설명',
                'category': '카테고리'
            }
        }

