"""
LLM 서비스
LLM API를 연동하여 자연어 질의응답을 처리합니다.
"""
import requests
import json
from typing import Dict, Optional
from config import LLM_API_URL, LLM_MODEL, LLM_TIMEOUT
from models.location import LocationModel


class LLMService:
    """LLM을 이용한 자연어 처리 서비스"""
    
    def __init__(self):
        self.api_url = LLM_API_URL
        self.model = LLM_MODEL
        self.timeout = LLM_TIMEOUT
        self.location_model = LocationModel()
    
    def ask_route(self, user_query: str) -> Dict:
        """
        사용자 질의를 받아서 길찾기 정보를 제공
        
        Args:
            user_query: 사용자의 자연어 질의 (예: "도서관으로 가는 길 알려줘")
        
        Returns:
            Dict: 응답 정보
        """
        # 먼저 JSON 파일에서 장소 정보를 가져와서 컨텍스트로 제공
        locations = self.location_model.get_all_locations()
        locations_context = self._format_locations_for_llm(locations)
        
        # LLM 프롬프트 생성
        prompt = self._create_route_prompt(user_query, locations_context)
        
        # LLM API 호출
        response = self._call_llm_api(prompt)
        
        return {
            'query': user_query,
            'response': response,
            'locations_context': locations_context
        }
    
    def _format_locations_for_llm(self, locations: list) -> str:
        """장소 정보를 LLM이 이해할 수 있는 형식으로 변환"""
        if not locations:
            return "등록된 장소가 없습니다."
        
        formatted = "등록된 장소 목록:\n"
        for loc in locations:
            formatted += f"- {loc['name']}"
            if loc.get('building_name'):
                formatted += f" ({loc['building_name']})"
            if loc.get('floor'):
                formatted += f" {loc['floor']}층"
            if loc.get('room_number'):
                formatted += f" {loc['room_number']}호"
            if loc.get('description'):
                formatted += f" - {loc['description']}"
            formatted += "\n"
        
        return formatted
    
    def _create_route_prompt(self, user_query: str, locations_context: str) -> str:
        """길찾기 프롬프트 생성"""
        prompt = f"""당신은 교내 길찾기 안내 키오스크입니다. 사용자의 질문에 친절하게 답변해주세요.

{locations_context}

사용자 질문: {user_query}

위의 장소 목록을 참고하여 사용자의 질문에 답변해주세요. 
만약 특정 장소로 가는 길을 묻는다면, 해당 장소의 위치 정보를 바탕으로 안내해주세요.
"""
        return prompt
    
    def _call_llm_api(self, prompt: str) -> str:
        """
        LLM API 호출
        Ollama 형식을 기본으로 하되, 다른 LLM API도 지원 가능하도록 구성
        """
        try:
            # Ollama API 형식
            payload = {
                'model': self.model,
                'prompt': prompt,
                'stream': False
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                # Ollama 응답 형식에 따라 텍스트 추출
                if 'response' in result:
                    return result['response']
                elif 'text' in result:
                    return result['text']
                else:
                    return str(result)
            else:
                return f"LLM API 오류: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "LLM API 응답 시간 초과입니다."
        except requests.exceptions.ConnectionError:
            return "LLM API에 연결할 수 없습니다. LLM 서비스가 실행 중인지 확인해주세요."
        except Exception as e:
            return f"LLM API 호출 중 오류 발생: {str(e)}"
    
    def extract_location_from_query(self, user_query: str) -> Optional[str]:
        """
        사용자 질의에서 목적지 장소명 추출
        간단한 키워드 매칭 방식 (나중에 LLM으로 개선 가능)
        """
        locations = self.location_model.get_all_locations()
        
        # 질의에서 장소명 찾기
        for loc in locations:
            if loc['name'] in user_query:
                return loc['name']
            if loc.get('building_name') and loc['building_name'] in user_query:
                return loc['name']
        
        return None

