GET /api/health : 서버 상태 확인
POST /api/upload : 엑셀 업로드 → JSON 저장
GET /api/locations : 장소 목록 조회 (?search=키워드 지원)
GET /api/locations/{id} : 특정 장소 조회
POST /api/route : 출발지/도착지로 경로 계산 ({"from","to"})
POST /api/ask : LLM 질의응답 ({"query": "질문"})
GET /api/excel-format : 엑셀 컬럼 형식 안내
GET /api/data/export : 현재 저장된 장소 데이터 JSON으로 반환