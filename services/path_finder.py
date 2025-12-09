"""
경로 찾기 서비스
두 장소 간의 최단 경로를 계산합니다.
"""
import math
from typing import List, Dict, Optional, Tuple
from models.location import LocationModel


class PathFinder:
    """경로 찾기 로직을 처리하는 서비스"""
    
    def __init__(self):
        self.location_model = LocationModel()
    
    def find_path(self, from_location: str, to_location: str) -> Dict:
        """
        출발지에서 목적지까지의 경로 찾기
        
        Args:
            from_location: 출발지 장소명
            to_location: 목적지 장소명
        
        Returns:
            Dict: 경로 정보 및 안내
        """
        # 장소 검색
        from_loc = self.location_model.get_location_by_name(from_location)
        to_loc = self.location_model.get_location_by_name(to_location)
        
        if not from_loc:
            return {
                'success': False,
                'error': f'출발지 "{from_location}"를 찾을 수 없습니다.'
            }
        
        if not to_loc:
            return {
                'success': False,
                'error': f'목적지 "{to_location}"를 찾을 수 없습니다.'
            }
        
        # 같은 장소인 경우
        if from_loc['id'] == to_loc['id']:
            return {
                'success': True,
                'from_location': from_loc,
                'to_location': to_loc,
                'path': [from_loc],
                'distance': 0,
                'directions': ['이미 목적지에 있습니다.']
            }
        
        # 좌표 기반 거리 계산
        distance = self._calculate_distance(
            from_loc.get('x_coordinate'),
            from_loc.get('y_coordinate'),
            to_loc.get('x_coordinate'),
            to_loc.get('y_coordinate')
        )
        
        # 방향 계산
        direction = self._calculate_direction(
            from_loc.get('x_coordinate'),
            from_loc.get('y_coordinate'),
            to_loc.get('x_coordinate'),
            to_loc.get('y_coordinate')
        )
        
        # 안내 메시지 생성
        directions = self._generate_directions(from_loc, to_loc, direction, distance)
        
        return {
            'success': True,
            'from_location': from_loc,
            'to_location': to_loc,
            'path': [from_loc, to_loc],
            'distance': distance,
            'direction': direction,
            'directions': directions
        }
    
    def _calculate_distance(self, x1: Optional[float], y1: Optional[float],
                           x2: Optional[float], y2: Optional[float]) -> Optional[float]:
        """두 좌표 간의 유클리드 거리 계산"""
        if x1 is None or y1 is None or x2 is None or y2 is None:
            return None
        
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def _calculate_direction(self, x1: Optional[float], y1: Optional[float],
                            x2: Optional[float], y2: Optional[float]) -> Optional[str]:
        """두 좌표 간의 방향 계산"""
        if x1 is None or y1 is None or x2 is None or y2 is None:
            return None
        
        dx = x2 - x1
        dy = y2 - y1
        
        # 각도 계산 (라디안)
        angle = math.atan2(dy, dx)
        angle_deg = math.degrees(angle)
        
        # 방향 변환
        if -22.5 <= angle_deg < 22.5:
            return '동쪽'
        elif 22.5 <= angle_deg < 67.5:
            return '동북쪽'
        elif 67.5 <= angle_deg < 112.5:
            return '북쪽'
        elif 112.5 <= angle_deg < 157.5:
            return '북서쪽'
        elif 157.5 <= angle_deg < 202.5:
            return '서쪽'
        elif 202.5 <= angle_deg < 247.5:
            return '남서쪽'
        elif 247.5 <= angle_deg < 292.5:
            return '남쪽'
        elif 292.5 <= angle_deg < 337.5:
            return '남동쪽'
        else:
            return '동쪽'
    
    def _generate_directions(self, from_loc: Dict, to_loc: Dict, 
                           direction: Optional[str], distance: Optional[float]) -> List[str]:
        """안내 메시지 생성"""
        directions = []
        
        # 출발지 정보
        from_info = from_loc.get('name', '')
        if from_loc.get('building_name'):
            from_info += f" ({from_loc['building_name']})"
        if from_loc.get('floor'):
            from_info += f" {from_loc['floor']}층"
        
        directions.append(f"출발지: {from_info}")
        
        # 목적지 정보
        to_info = to_loc.get('name', '')
        if to_loc.get('building_name'):
            to_info += f" ({to_loc['building_name']})"
        if to_loc.get('floor'):
            to_info += f" {to_loc['floor']}층"
        
        directions.append(f"목적지: {to_info}")
        
        # 방향 안내
        if direction:
            directions.append(f"{direction} 방향으로 이동하세요.")
        
        # 거리 정보
        if distance is not None:
            directions.append(f"예상 거리: 약 {distance:.1f}미터")
        
        # 건물이 다른 경우
        if (from_loc.get('building_name') and to_loc.get('building_name') and
            from_loc['building_name'] != to_loc['building_name']):
            directions.append(f"{from_loc['building_name']}에서 {to_loc['building_name']}로 이동해야 합니다.")
        
        # 층이 다른 경우
        if (from_loc.get('floor') and to_loc.get('floor') and
            from_loc['floor'] != to_loc['floor']):
            floor_diff = to_loc['floor'] - from_loc['floor']
            if floor_diff > 0:
                directions.append(f"{floor_diff}층 올라가세요.")
            else:
                directions.append(f"{abs(floor_diff)}층 내려가세요.")
        
        return directions

