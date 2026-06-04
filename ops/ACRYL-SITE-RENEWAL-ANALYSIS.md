# ACRYL(www.acryl.ai) 사이트 전수 분석 — 리뉴얼 준비 문서

> 분석일: 2026-06-04
> 대상: https://www.acryl.ai (메인 마케팅 사이트, 9개 섹션 전수)
> 목적: 전면 리뉴얼(IA·디자인·콘텐츠·기술)을 위한 현황 진단 및 개선 방향 도출

---

## 0. 요약 (Executive Summary)

아크릴은 2011년 설립, 2025년 12월 코스닥 상장한 AI 풀스택 기업이다.
현재 사이트는 두 개의 주력 제품(Jonathan®, NADIA®)을 축으로 한 9개 섹션
구조이나, (1) 페이지별 메시지 중복·일관성 부족, (2) 채용 페이지의 무관한
플레이스홀더 콘텐츠, (3) KR/EN 혼재, (4) CTA 단조로움, (5) 제품 서브도메인
(jonathan.acryl.ai)과의 정보 분절 등 리뉴얼이 필요한 다수 지점이 확인된다.

---

## 1. 사이트 구조 (Information Architecture)

```
www.acryl.ai
├─ /                 홈 (히어로 + 제품 2종 + 강점 4 + 인사이트 3)
├─ /jonathan         제품① AI 풀스택 플랫폼
├─ /nadia            제품② 에이전틱 AI 헬스케어 플랫폼
├─ /business         산업별 솔루션 / 고객 사례
├─ /insights         뉴스·이벤트·사례·기술블로그·간행물
├─ /ir               투자자 관계 (상장기업 공시)
├─ /about            회사 소개 (비전·문제정의·연혁)
├─ /career           채용
└─ /contact-us       문의 폼

[글로벌] 언어 전환 KR | EN
[연계]   Family Site: Jonathan® / KIWI
[제품]   별도 서브도메인 jonathan.acryl.ai (제품 상세/기술/솔루션/포털)
[소셜]   Instagram · Facebook · YouTube
```

핵심 발견:
- 메인 마케팅(www)과 제품 상세(jonathan.acryl.ai)가 분리되어, 사용자가
  제품 깊이 있는 정보를 보려면 도메인을 이동해야 함 → 정보 분절.
- 글로벌 네비게이션은 7개 메뉴 + 문의 + 언어. 상장 이후 IR 비중이 커졌으나
  메뉴 위계상 제품과 동일선상에 노출.

---

## 2. 페이지별 콘텐츠 인벤토리

### 2-1. 홈 (/)
```
히어로 메인:  "AI Computing for Real Life"
히어로 부제:  "모든 AI 기업을 위한 기업"
CTA:         자세히 보기 → /about

섹션01 Jonathan®:  AI 풀스택 플랫폼(End-to-End)
                  GPU 최적화 · 개발 자동화 · LLM 오케스트레이션
                  이기종 지원(NVIDIA/AMD/TPU/NPU)
섹션02 NADIA®:     에이전틱 AI 헬스케어 플랫폼
                  HIS 기반 · 임상데이터 정규화 · 식약처 허가 SaMD

왜 ACRYL인가 (4강점):
  1) GPU 최적화: 소프트웨어만으로 GPU 활용률 85%
  2) End-to-End: GPUBASE → FLIGHTBASE → AGENTBASE
  3) 헬스케어 검증: 실제 병원 배포 사례
  4) 함께 만들기: PoC부터 프로덕션 파트너십

인사이트(3):  R&D 우수성과 50선 / K-AI 교육 플랫폼 / 과기부총리상
CTA 반복:     "자세히 보기" ×3, "문의하기" ×2, "전체 보기" ×1
```

### 2-2. /about
```
슬로건:   "AI to AX. Realized."
설립:     2011년 3월 — "AI 기술로 더 나은 세상" 확신으로 설립
신념:     AI가 모두에게 쉽고 편리하게 쓰여야 한다

해결 문제:
  · 인프라: "75% 기업이 보유 GPU를 제대로 못 씀" → GPUBASE 멀티패스 RDMA로 85%
  · 헬스케어: "병원 데이터 80%가 비정형 사일로" → NADIA 자동 정규화/구조화/비식별화

성과:
  2025.12 코스닥 상장
  2024    우수기업연구소 지정 · 대한민국 AI 50 선정
  2023    국무총리상 · 과기정통부 장관상
(조직/팀 상세는 미기재)
```

### 2-3. /jonathan
```
정의:   AI 풀스택 플랫폼(End-to-End) — AI 개발 전 단계 자동화

3대 구성:
  GPUBASE    GPU 컴퓨팅 최적화 (소프트웨어 정의 GPU 인프라)
  FLIGHTBASE AI 개발·운영 MLOps (엔터프라이즈 End-to-End)
  AGENTBASE  LLM·에이전트 최적화 LLMOps

개발 단계:  기획 → 데이터 준비 → 모델 학습 → 성능 검증 → 배포 → 운영
기능 영역:  Infra / Models(시각·공감·의료·대화) / Data Analysis /
            Annotation(텍스트·이미지·비디오) / LLM(RAG·Playground·Finetuning)
CTA:       "전문가의 도움이 필요하신가요? … [문의하기]"
```

### 2-4. /nadia
```
정의:   에이전틱 AI 헬스케어 플랫폼 (임상문서 자동화·진단 워크플로우·기기 연동)

구성:
  NADIA CORE   병원 데이터 자동 정규화, EMR/PACS/LIS 연동
  NADIA ESTHER 혁신의료기기 인증·식약처 허가 AI 의료기기, SaMD 가속

핵심 서비스:  의료 GPT 검색 · 요약 · 분류 · CDSS(임상의사결정지원)
5대 기술:     시맨틱 레이어 · 고급 청킹 · 다단계 검증 · 연합학습 · 에이전틱 RAG
실적:        SaMD 7종 개발(4종 인허가) · 협력 병원 10,000+ 병상
CTA:         "문의하기"
```

### 2-5. /business
```
슬로건:  "Generative AI in a cheaper, easier way"

산업별 솔루션(4):
  헬스케어    NADIA 기반 임상 인텔리전스, HIS/EMR 연동, SaMD
  국방·공공   온프레미스 보안 AI, 정책연구 AI, 주권(Sovereign) AI 컴플라이언스
  제조·기업   산업특화 모델, 품질검사, 예지보전, 엔터프라이즈 80+ 고객
  글로벌      NADIA 우즈베키스탄 표준 병원 IT 채택, 말레이시아/동남아/북미 확장

플랫폼:  JONATHAN®(개발·학습·운영) / NADIA(헬스케어 HIS)
기술:    멀티 GPU 가속 · 분산학습 · 연합학습 · HPS
고객사례: 삼성서울병원, 국가보훈부, 통일부, KB손해보험 등 12건
```

### 2-6. /insights
```
카테고리:  News · Events · Use Cases · Tech Blog · Publications
레이아웃:  카드형 3열, 페이지네이션(1/3)
최근 게시물:
  · 2025 중소기업 R&D 우수성과 50선 — 공공혁신 (2026.02.05)
  · 600조 글로벌 AI 교육시장, 에듀테크 3사와 K-AI 교육 플랫폼 (2026.01.05)
  · 과기부총리상 수상, 국가공인 AX 인프라 파트너 (2025.12.19)
  · "AX 플랫폼 초격차"… 16일 코스닥 상장
```

### 2-7. /ir
```
IR 정보:  분기자료 2025.4Q / 2024.4Q / 2024.1Q,
          상장 전 월별 매출 공고(2025.10)
공시:     2025.3Q / 2025.1Q, 주주총회 기준일 설정 공고(2025.09)
공개:     2025.1Q
메시지:   "주주의 권리를 보호하고 함께 성장"
(주가·재무 대시보드 등 상장사 표준 IR 구성요소는 제한적)
```

### 2-8. /career  ⚠️ 리뉴얼 최우선 이슈
```
타이틀:  "Unlock your AI Potential! / 우리의 빛나는 여정에 함께하세요."
복지(14): 수평적 조직문화, 시차출퇴근, 사내 카페테리아, 동호회 지원,
          야근 교통지원, 자기개발비, 교육, 건강검진비 등

⚠️ 채용 공고가 회사 정체성과 무관한 플레이스홀더로 보임:
   직무 "Recruitment of experienced IT service project leaders"인데
   모집분야 "1 dispatch clerk", 업무 "Logistics dispatch work, other office work",
   우대 "dispatcher experience, MS Office" — 물류 배차 사무 내용.
   → AI 기업 채용과 불일치. 템플릿/더미 데이터 잔존 추정. 즉시 교체 필요.
```

### 2-9. /contact-us
```
섹션:   "전문가의 도움이 필요하신가요?" / 개인정보 수집·이용 안내
폼 필드: 문의유형(필수: Business/Product·Technology·IR·Careers·Others)
        이름(필수) · 전화(필수) · 이메일(필수) · 회사명(선택) · 내용(필수)
개인정보: 수집 [필수]이름·전화·이메일 [선택]회사명 / 보유 종료 후 1개월
```

### 공통 푸터
```
주소:  7F/8F, Chungdam Venture Plaza, 704 Seolleung-ro, Gangnam-gu, Seoul (06069)
TEL +82.2.557.4958 · FAX +82.2.558.4958 · MAIL info@acryl.ai
© 2026 ACRYL inc. · Instagram/Facebook/YouTube · Family Site: Jonathan®/KIWI
```

---

## 3. 브랜드·메시지 체계 (현황)

```
설립연도:  2011 (업력 15년)
상장:      2025.12 코스닥
태그라인:  복수 혼재 — "AI Computing for Real Life"
                     "AI to AX. Realized."
                     "모든 AI 기업을 위한 기업"
                     "Generative AI in a cheaper, easier way"
제품축:    Jonathan®(인프라/MLOps/LLMOps) · NADIA®(헬스케어 AI)
핵심기술:  GPU 최적화(활용률 85%) · 연합학습 · 에이전틱 RAG · SaMD
```

진단: 페이지마다 상위 슬로건이 달라 **브랜드 메시지의 단일 축이 불명확**.
리뉴얼 시 1개 마스터 태그라인 + 제품별 서브 메시지 위계 정립 필요.

---

## 4. 리뉴얼 관점 주요 이슈 (우선순위)

```
[P0 — 즉시]
 1. /career 무관 플레이스홀더(물류 배차 사무) 공고 → 실제 AI 직무로 전면 교체
 2. KR/EN 콘텐츠 혼재(특히 career 영어 더미) → 언어별 완역·일관화

[P1 — 구조]
 3. 마스터 태그라인 1개로 통일, 제품/회사/IR 메시지 위계 재설계
 4. www(마케팅) ↔ jonathan.acryl.ai(제품상세) 정보 분절 통합/연결 전략
 5. CTA 다양화 — "자세히 보기/문의하기" 단조 반복 → 데모요청·자료다운로드·
    PoC상담 등 맥락별 전환 경로 설계

[P2 — 콘텐츠/신뢰]
 6. /about에 조직·팀·리더십·연혁 타임라인 보강(상장사 신뢰도)
 7. /ir 상장사 표준화 — 주가·재무하이라이트·전자공시·IR캘린더·배당정책
 8. /business 고객사례 12건을 정량성과(KPI) 포함 케이스스터디로 고도화
 9. 제품 수치 근거(GPU 85%, 1.5배, 10,000 병상 등) 출처/조건 명기

[P3 — 디자인/기술/운영]
10. 반응형·접근성(WCAG)·코어웹바이탈 점검
11. 메타/OG/구조화데이터(SEO), 다국어 hreflang 정비
12. 폼 스팸/검증·개인정보 처리방침 링크·쿠키 동의 등 컴플라이언스
13. 디자인시스템(타이포·컬러·컴포넌트) 정립 — 카드/CTA 일관화
```

---

## 5. 리뉴얼 권고 IA(안)

```
GNB:  Products(Jonathan/NADIA) · Solutions(산업별) · Customers(사례) ·
      Insights · Company(About/Career) · Investors(IR) · [Contact/Demo]

핵심 전환 동선:
  방문자 유형 분기 → 기업(데모요청) / 의료기관(NADIA 상담) /
                    개발자(Jonathan 기술문서·포털) / 투자자(IR) / 구직자(Career)

제품 정보 통합:
  www 제품 개요 → "기술 상세/문서/포털"을 jonathan.acryl.ai로 자연 연결
  (도메인 경계를 사용자가 인지하지 못하도록 내비/디자인 일관)
```

---

## 6. 다음 단계 (리뉴얼 실행 준비)

```
1) 콘텐츠 전수 마이그레이션 시트 작성(페이지×요소×KR/EN×교체여부)
2) P0 이슈(career 더미·언어 혼재) 별도 핫픽스 트랙으로 선처리
3) 마스터 메시지/브랜드 가이드 확정 워크숍
4) 신규 IA·와이어프레임·디자인시스템 설계
5) 상장사 IR/컴플라이언스 요건 체크리스트 확정
6) SEO·성능·접근성 베이스라인 측정 → 리뉴얼 후 비교 KPI 설정
```

---

*본 문서는 공개된 www.acryl.ai 페이지의 외부 관찰 기반 분석이며,
내부 비공개 정보·CMS·트래픽 데이터는 포함하지 않는다. 수치/문구는 사이트
게시 내용을 인용한 것으로, 리뉴얼 착수 시 사내 사실확인(fact-check)이 필요하다.*
