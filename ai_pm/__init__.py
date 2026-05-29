"""ai_pm — VVS-AI-CO 핵심 로직 패키지 (betplay-mvp 이식).

헤르메스 에이전트 위 VVS 재구축을 위한 betplay 검증 로직 20개를 담는다.
모든 모듈은 sandbox(절대선 #2 격리)를 토대로 동작한다.

이식 순서(의존):
  1. sandbox          ← (현재 생성됨) 다른 모든 모듈의 토대
  2. doc_types → fact_verifier → banned_phrases → banned_phrase_filter
     → disclaimer_injector → legal_safety_router
  3. block_library → quality_rubric → persona_generator
  4. sqlite_db → pattern_db → Ops 도구 7개
  5. (B-1) hermes_h3_enforcement_poc
"""
