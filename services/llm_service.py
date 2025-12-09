"""
LLM 없이 JSON 데이터만으로 응답을 생성합니다.
"""
import json
from typing import Dict, Optional, List
from pathlib import Path
from config import JSON_DATA_PATH


class LLMService:
    """JSON 기반 간단 응답 서비스"""

    def ask_route(self, user_query: str) -> Dict:
        data_json = self._load_data_json()
        response, target_id = self._answer_from_data(user_query, data_json)
        return {
            'query': user_query,
            'response': response,
            'target_id': target_id,
            'data_loaded': bool(data_json),
        }

    def _load_data_json(self) -> Dict:
        """locations.json을 로드 (map_nodes, facilities 포함)"""
        try:
            path = Path(JSON_DATA_PATH)
            with path.open(encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _answer_from_data(self, user_query: str, data_json: Dict) -> (str, Optional[str]):
        facilities: List[Dict] = data_json.get('facilities', [])
        map_nodes: List[Dict] = data_json.get('map_nodes', [])

        matches = self._find_facility_matches(user_query, facilities)
        if not matches:
            return "죄송합니다. 해당 시설 정보를 찾지 못했습니다. 정확한 명칭을 말씀해 주세요. [[TARGET_ID:None]]", "None"

        # 건물명만 주어진 경우: 건물 내 시설들을 층별로 요약해 제공
        building_names = {m.get('building') for m in matches if m.get('building')}
        if len(matches) > 3 and len(building_names) == 1:
            bld = next(iter(building_names))
            floor_map = {}
            for m in matches:
                floor = m.get('floor', '정보없음')
                floor_map.setdefault(floor, []).append(m.get('facility', ''))
            lines = []
            for floor, facs in sorted(floor_map.items()):
                fac_list = ', '.join(f for f in facs if f)
                lines.append(f"- {floor}: {fac_list}")
            target_id = self._find_building_id(bld, map_nodes) or "None"
            region_hint = self._region_hint(bld)
            guide = f"{bld}에 있는 시설 목록입니다:\n" + "\n".join(lines)
            return f"{guide}\n{region_hint} [[TARGET_ID:{target_id}]]", target_id

        # 단일 혹은 소수 → 첫 번째 사용
        dest = matches[0]
        building = dest.get('building', '')
        floor = dest.get('floor', '')
        facility = dest.get('facility', '')

        target_id = self._find_building_id(building, map_nodes)
        region_hint = self._region_hint(building)

        guide = f"{facility}은 {building} {floor}에 있습니다. {region_hint}"
        tag = f"[[TARGET_ID:{target_id or 'None'}]]"
        return f"{guide} {tag}", target_id or "None"

    def _find_facility_matches(self, query: str, facilities: List[Dict]) -> List[Dict]:
        q = query.lower()
        results = []
        for f in facilities:
            name = f.get('facility', '')
            bld = f.get('building', '')
            if (name and name.lower() in q) or (bld and bld.lower() in q):
                results.append(f)
        return results

    def _find_building_id(self, building: str, map_nodes: List[Dict]) -> Optional[str]:
        for node in map_nodes:
            if node.get('type') == 'building' and node.get('name') == building:
                return node.get('id')
        return None

    def _region_hint(self, building: str) -> str:
        flat = {'1호관', '2호관', '8호관'}
        hill = {'3호관', '4호관', '5호관', '6호관', '7호관', '운동장'}
        if building in flat:
            return "정문 평지 구역에 있어 바로 이동하시면 됩니다."
        if building in hill:
            return "언덕 위에 있으니 가까운 계단을 이용해 올라가세요."
        return "캠퍼스 내 위치입니다. 안내 표지판을 참고하세요."

