"""
건물/장소 데이터 모델
엑셀에서 읽은 데이터를 JSON 파일로 저장하고 관리합니다.
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from config import JSON_DATA_PATH


class LocationModel:
    """건물/장소 데이터를 JSON 파일로 관리하는 모델"""
    
    def __init__(self):
        self.json_path = JSON_DATA_PATH
        self.init_json_file()
    
    def init_json_file(self):
        """JSON 파일 초기화 (없으면 생성)"""
        if not self.json_path.exists():
            initial_data = {
                'locations': [],
                'connections': [],
                'last_updated': None
            }
            self._save_json(initial_data)
    
    def _load_json(self) -> Dict:
        """JSON 파일에서 데이터 로드"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # 파일이 없거나 손상된 경우 초기화
            initial_data = {
                'locations': [],
                'connections': [],
                'last_updated': None
            }
            self._save_json(initial_data)
            return initial_data
    
    def _save_json(self, data: Dict):
        """JSON 파일에 데이터 저장"""
        data['last_updated'] = datetime.now().isoformat()
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_location(self, location_data: Dict) -> int:
        """새로운 장소 추가"""
        data = self._load_json()
        
        # ID 생성 (기존 최대 ID + 1)
        max_id = 0
        if data['locations']:
            max_id = max(loc.get('id', 0) for loc in data['locations'])
        
        new_location = {
            'id': max_id + 1,
            'name': location_data.get('name', ''),
            'building_name': location_data.get('building_name'),
            'floor': location_data.get('floor'),
            'room_number': location_data.get('room_number'),
            'x_coordinate': location_data.get('x_coordinate'),
            'y_coordinate': location_data.get('y_coordinate'),
            'description': location_data.get('description'),
            'category': location_data.get('category'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        data['locations'].append(new_location)
        self._save_json(data)
        
        return new_location['id']
    
    def get_location_by_name(self, name: str) -> Optional[Dict]:
        """이름으로 장소 검색"""
        data = self._load_json()
        
        for loc in data['locations']:
            if name.lower() in loc.get('name', '').lower():
                return loc
        return None
    
    def get_location_by_id(self, location_id: int) -> Optional[Dict]:
        """ID로 장소 검색"""
        data = self._load_json()
        
        for loc in data['locations']:
            if loc.get('id') == location_id:
                return loc
        return None
    
    def get_all_locations(self) -> List[Dict]:
        """모든 장소 조회"""
        data = self._load_json()
        return data.get('locations', [])
    
    def search_locations(self, query: str) -> List[Dict]:
        """장소 검색 (이름, 건물명, 설명에서 검색)"""
        data = self._load_json()
        query_lower = query.lower()
        results = []
        
        for loc in data.get('locations', []):
            name = loc.get('name', '').lower()
            building = loc.get('building_name', '').lower()
            description = loc.get('description', '').lower()
            
            if (query_lower in name or 
                query_lower in building or 
                query_lower in description):
                results.append(loc)
        
        return results
    
    def clear_all_locations(self):
        """모든 장소 데이터 삭제 (엑셀 재업로드 시 사용)"""
        data = {
            'locations': [],
            'connections': [],
            'last_updated': datetime.now().isoformat()
        }
        self._save_json(data)
    
    def add_connection(self, from_id: int, to_id: int, distance: float = None, 
                      direction: str = None, description: str = None):
        """두 장소 간 연결 추가"""
        data = self._load_json()
        
        # ID 생성
        max_id = 0
        if data['connections']:
            max_id = max(conn.get('id', 0) for conn in data['connections'])
        
        new_connection = {
            'id': max_id + 1,
            'from_location_id': from_id,
            'to_location_id': to_id,
            'distance': distance,
            'direction': direction,
            'description': description
        }
        
        data['connections'].append(new_connection)
        self._save_json(data)
    
    def get_connections(self, location_id: int = None) -> List[Dict]:
        """연결 정보 조회"""
        data = self._load_json()
        
        if location_id is None:
            return data.get('connections', [])
        
        # 특정 장소와 연결된 경로만 반환
        connections = []
        for conn in data.get('connections', []):
            if (conn.get('from_location_id') == location_id or 
                conn.get('to_location_id') == location_id):
                connections.append(conn)
        
        return connections
