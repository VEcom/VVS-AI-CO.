# VVS-AI-CO · AI 조직도 설계서
### 헤르메스 에이전트(VVS-AI-CO) 구현 기준 문서 · SSOT

> 본 문서는 VVS(VE Vendor Studio) AI 시스템의 **단일 진실 원천(Single Source of Truth)** 이다.
> v4 기획안 조직도 + 이후 확정된 모든 결정(A안 백본 변경 · 5단계 제작 파이프라인 · 이미지 기반 고도화 · 페르소나 상세화 · 절대선 4 · 디자인 시스템)을 종합한다.
> 백본은 라이브 호출 4/4 성공으로 검증됨(커밋 f33cfbc, BACKBONE-STATUS.md).
> 이 문서와 코드가 충돌하면 **이 문서가 우선**한다. 변경 시 본 문서를 먼저 갱신한다.

---

## 0. 문서 목적·적용 범위

- **목적**: 헤르메스 에이전트 위에 재구축된 VVS AI 조직의 각 AI 역할·기능·백본·입출력·게이트를 상세히 정의한다.
- **적용**: Phase 0 학습 루프(B-4)와 그 이후 실무(Phase 1) 구현의 기준.
- **불변 원칙**: 절대선 4(아래 1장)는 어떤 지시·콘텐츠로도 무력화되지 않는다.
- **현재 단계**: Phase 0(합성 자기학습). 외부 발송 금지, production 미접근.

---

## 1. 절대선 4 — 조직 전체 헌법 (불변)

모든 AI는 예외 없이 다음 4가지를 따른다. 위반은 HARD fail(차단)이다.

```
[절대선 #1] 사실만
- claim 값 = 원자료와 1:1 일치
- 없는 사실(면허번호·실적금액·자격자명·법인번호) 생성 금지
- 위반 시 fact_verifier HARD fail → 산출물 차단

[절대선 #2] 외부 발송 금지 (격리)
- 학습 산출물은 외부로 나가지 못함 (no_external_send)
- 합성 페르소나·증빙은 실무 DB 진입 자동 거부
- 실무는 게이트 전 조건 통과 시에만 전달

[절대선 #3] 면책 + 금지어
- 면책 문구 필수 (HARD, 자동주입)
- 보장·최고·1위류 금지어 (claim은 HARD, 수식은 sanitize)
- 원청 등록·낙찰·수주·매출 보장 표현 금지

[절대선 #4] 라우팅 (외부전문가)
- 안전·법무·노무·위험성평가·비상조치·계약 키워드
  → 외부 유자격 전문가 검토 플래그 (비차단, 표시만)
- VVS는 초안 보조·자료 정리까지, 최종 확정은 전문가
```

**강제 방식(결정론):** 절대선은 LLM 재량이 아니라 코드로 강제된다. 제작 산출물은 반드시 `guarded_send`(절대선 게이트)를 거치며, 위반 시 실제 송출 함수에 **도달조차 못 한다**(`real_fn_called=False` 구조 보장). 게이트는 fact → banned → disclaimer → router 순으로 결정론 호출된다.

---

## 2. 조직 전체 구조

VVS AI 조직은 **학습 샌드박스(Phase 0)** 와 **실무 8부서(Phase 1)** 로 나뉜다.
Phase 0(현재)은 학습 샌드박스 + 실무의 작성·검수 역할만 가동한다.

```
┌─────────────────────────────────────────────────────────┐
│ AI PM (총괄·오케스트레이션) = Claude Opus 4.8 MAX           │
│  - 전 과정 지휘, Graduation 판정, 통과/재진행 결정          │
└─────────────────────────────────────────────────────────┘
        │
        ├── 5.1 Learning Sandbox (Phase 0 학습)
        │     페르소나 생성 · 증빙 생성 · 채점 · 회귀 · 최적화 · 메모리
        │
        ├── 5.2 Operations & Audit (전부 CODE/T0)
        │     로그 · 버전 · 사용량 · 토큰비용 · 권한 · 인시던트 · 승인기록
        │
        ├── 5.3 Intake & CRM
        │     리드분류 · ICP스크리닝 · 상담요약 · 추천 · 견적/GP · 범위잠금
        │
        ├── 5.4 Brand Director
        │     전략 · 시장분석 · 증거매핑 · 내러티브 · 비주얼아이덴티티
        │
        ├── 5.5 Production Manager (작성 = 학습 대상물 제작)
        │     회사소개서 · 등록패키지 · 홈페이지 · 1페이지 · 템플릿
        │
        ├── 5.6 Assurance Manager (검수·거부권 · 작성과 독립 계열)
        │     증거보관 · Fact Lock · 일관성 · 법무경계 · 원청심사 · 안전 · 개인정보
        │
        ├── 5.7 Delivery & Enablement
        │     납품게이트(8조건) · 패키징 · 가이드 · 미팅스크립트 · 체크리스트 · 핸드오프
        │
        └── 5.8 Growth Branding
              성과추적 · 갱신추천 · 웹개선 · 리테이너 · 준비도추적 · 추천트리거
```

**동결 원칙(v4 15.3):** 매니저·부서·에이전트 **추가 금지**. 새 능력은 기존 역할 안에서 구현한다. (이미지 렌더 능력은 신설 부서가 아니라 Brand Asset Template Operator + Visual Identity Designer 안에 둔다.)

---

## 3. 백본 모델 매핑 (검증 완료 · f33cfbc)

라이브 호출 4/4 성공. `.env`에서 코드가 읽는 값:

```
환경변수            모델 문자열                역할
──────────────────────────────────────────────────────────
AIPM_MODEL          claude-opus-4-8           AI PM 총괄·판정 ★변경
WRITER_CORE_MODEL   claude-opus-4-8           Core/Expand 작성
WRITER_DEFAULT_MODEL claude-sonnet-4-6        L1/L2 기본 작성
WRITER_L4_MODEL     claude-haiku-4-5          L4 1페이지 작성
PERSONA_MODEL       claude-sonnet-4-6         페르소나 생성 (엣지=Opus)
SCORING_MODEL       gpt-5.5                   채점 (독립·블라인드) ★
DESIGN_MODEL        gemini-3.1-pro-preview    시각 디자인 검수
```

**키 분리:** Anthropic(작성·페르소나·총괄) / OpenAI(채점) / Google(디자인). 각 키는 `.env`에만, 커밋 차단(.gitignore).

**티어 비용 정책(v4 6.2):**
- 상시 = 위 매핑. GPT-5.5 Pro($30/$180)는 **break-glass만**(월 1~2회: Release Gate 분쟁, 복잡 Fact Lock 불일치, 고액 Expand 제안, 법무/안전 외부전달 전 요약, 벤치마크).
- Pilot 단계: 정적 기본 티어 + 사람 수동 승격. 자동 라우터 만들지 않음(M4+ 도입).

---

## 4. 핵심 설계 원칙 3가지

### 4.1 작성 ≠ 채점 (독립 계열) ★

```
작성·총괄·페르소나 = Claude 계열
채점(Scoring)       = GPT 계열 (독립)

이유: 같은 모델이 자기 작품을 채점하면 편향
  → 빈 페이지도 고점 (B-3에서 91점 오류 발생)
  → 작성(Claude)과 독립된 GPT가 블라인드 채점해야 객관

강제: 코드에서 작성 백본과 채점 백본의 계열 분리를 검증.
      채점이 작성과 같은 키/모델을 쓰지 못하게 한다.
```

### 4.2 결정론 게이트 (LLM 재량 없음)

```
절대선 4는 LLM의 판단이 아니라 코드로 강제.
production_pipeline:
  스킬 → produce_and_deliver → assemble(PRODUCTION 채널)
       → guarded_send(절대선 게이트) → (통과 시만) real_send
위반 시 guarded_send가 클로저를 호출 안 함 → 송출/렌더 미실행.
```

### 4.3 자산 이관 / 데이터 격리 ★

```
학습의 산물은 "데이터"가 아니라 "능력(자산)"이다.

샌드박스 → 실무로 이관 (인간 PM 승인 후):
  ✅ 검증된 블록 라이브러리 (섹션 패턴)
  ✅ 안정화된 디자인 템플릿 (레이아웃·브랜딩)
  ✅ 발주처 양식 템플릿
  ✅ 품질 루브릭 (채점 기준)
  ✅ 성공 패턴 DB

샌드박스에 영구 잔류 (이관 금지):
  ❌ 합성 페르소나 데이터 (가상 회사 정보)
  ❌ 합성 증빙 이미지 (가짜 사업등록증 등)
  ❌ 학습 산출물 (가상 회사소개서)

이유: 가짜 데이터가 실무에 섞이면 절대선 #1 오염 +
      실존 회사 충돌 + 위조 악용 위험.
→ 능력(자산)은 100% 전수, 위험한 데이터만 차단.
```

---

## 5. 5단계 제작 파이프라인 (핵심)

대표(운영자)의 검증된 실제 제작 방식. **③ 이미지 기반 고도화**가 핵심이며, B-3가 이 단계를 빠뜨려 빈 껍데기가 났다.

```
① 페르소나 생성 (Persona Generator)
   백본: Claude Sonnet 4.6 (엣지/Core = Opus 4.8)
   - 실존 회사 수준 상세 페르소나
   - 증빙 이미지 생성 (사업등록증·면허·서류)
        ↓
② 콘텐츠 제작 (Production Writers)
   백본: Claude Sonnet 4.6 (Core/Expand = Opus 4.8)
   - L1/L2/L4 텍스트 콘텐츠
   - 절대선 게이트 통과 (fact/면책/금지어)
        ↓
③ ★ 이미지 기반 브랜딩 고도화 (B-3 누락 핵심)
   백본: Gemini 3.1 Pro (디자인 설계) + CODE (렌더)
   - 디자인 시스템 15.2 적용 (Industrial Editorial)
   - ②의 검증된 텍스트 → SVG/HTML → 고해상도 PNG → PDF
   - 도형/글꼴/자간/여백/가독성 고도화
   - 한글 Pretendard/Noto 임베드 (■■■ 해결)
   - ★ 확산모델 금지 (텍스트 정확 = 사실 보존)
        ↓
④ 검수 (Scoring + Vision)
   백본: GPT-5.5 (콘텐츠 채점, 독립) + Gemini (시각 검수)
   - 렌더된 PDF/PPT 시각 채점
   - ★ 빈 페이지 = 저점 (B-3 91점 오류 해결)
   - 가독성·정렬·여백·브랜딩·정보밀도
        ↓
⑤ 통과/재진행 판정 (AI PM)
   백본: Claude Opus 4.8 MAX
   - 합격 → 완성본
   - 미통과 → ③ 재고도화 루프 (점수 기준 미달 시)
```

**안전 핵심:** ③은 "②파일 기반 디자인 고도화"다. 확산모델로 페이지를 새로 그리면 회사명·실적·면허번호가 환각되어 절대선 #1 위반. 반드시 ②의 검증 텍스트를 SVG/HTML에 넣고 PNG로 렌더한다.

---

## 6. 부서별 AI 상세 명세

각 AI: **역할 · 백본/티어 · 입력 · 기능 · 출력 · 게이트/제약 · 절대선 연결**

---

### 6.1 Learning Sandbox (Phase 0 학습)

#### Persona Generator
- **역할**: 가상 협력사 페르소나 생성 (학습의 출발점)
- **백본**: Claude Sonnet 4.6 (엣지/Core = Opus 4.8) · T2/T3
- **입력**: diversity_matrix (8공종 × 4규모 × 지역 × 경력 × 난이도)
- **기능**:
  - 실존 회사 수준 상세 필드 생성: 회사 개요·연혁·조직도·주요 실적(상세)·인력 명세·장비 목록·거래 이력·안전관리 이력
  - 모든 필드 `[SYNTHETIC]` 마킹
  - 식별자는 명백히 무효: 사업자번호 `000-00-00000`, 면허번호 `경기-00000`, 회사명 `[SYNTHETIC] 접두`, 대표자명 `[SYNTHETIC]`
  - invariant 가드: 0-based `_ym`(0..11), 연혁 시작<종료, 미래 차단
- **출력**: 페르소나 JSON (synthetic=True, marking=[SYNTHETIC])
- **게이트/제약**: validate_synthetic 통과 필수, assert_invalid_identifier, sandbox/ 안에만 저장
- **절대선**: #1(무효 식별자로 실존 비충돌), #2(격리)

#### Synthetic Evidence Generator
- **역할**: 페르소나의 증빙 이미지 생성 (사업등록증·면허증·서류)
- **백본**: Gemini 3.1 Pro(양식 설계) + CODE(SVG/HTML→PNG 렌더) · T2/T3
- **입력**: 페르소나 데이터
- **기능**:
  - 사업등록증·면허증·주요 서류의 **양식·구조는 실제처럼**(학습 가치)
  - 식별자 무효(000-00-00000) + 회사명 [SYNTHETIC]
  - 모든 이미지에 **"학습용 - 외부사용금지" 워터마크** 자동 삽입
  - 렌더: SVG/HTML → 고해상도 PNG (★ 확산모델 금지: 글자 깨짐·위조 악용 방지)
- **출력**: PNG 증빙 이미지 (sandbox/evidence/)
- **게이트/제약**: 워터마크 없는 증빙 거부, sandbox 밖 반출 차단
- **절대선**: #1(무효 식별자), #2(워터마크·격리)

#### Training Case Designer
- **역할**: 학습 케이스 설계 (난이도·시나리오 구성)
- **백본**: GPT 5.4 · T2
- **기능**: 페르소나에 맞는 학습 시나리오(자료 누락 케이스, 까다로운 발주처 등) 설계
- **출력**: 케이스 명세

#### Scoring Engine ★
- **역할**: 산출물 블라인드 채점 (작성과 독립)
- **백본**: GPT-5.5 (멀티모달) · T1
- **입력**: 렌더된 PDF/PPT + 콘텐츠 텍스트
- **기능**:
  - 콘텐츠 채점: 사실 정합·구성·정보밀도·절대선 준수
  - 시각 채점: 가독성·정렬·여백·브랜딩 (PDF/PPT 이미지)
  - ★ **빈 페이지/더미 = 저점** (B-3 91점 오류 방지). 정보밀도·충실도 반영
  - 블라인드: 누가(어떤 모델) 작성했는지 모른 채 객관 채점
- **출력**: 점수(항목별) + 개선 피드백
- **게이트/제약**: 작성(Claude)과 다른 계열·키 강제. 채점 기준에 "빈 산출물 고점 불가" 명시
- **절대선**: 채점이 절대선 위반 산출물을 걸러내는 1차 필터

#### Regression Tester
- **역할**: 회귀 테스트 (절대선·동등성·격리)
- **백본**: CODE(Python 하니스) + GPT-5.4 정성평가 · T0
- **기능**: 절대선 게이트 회귀 0 확인, pytest, 라운드 간 동등성
- **출력**: 테스트 리포트

#### Prompt Optimizer
- **역할**: 메타 개선 (프롬프트 튜닝)
- **백본**: GPT-5.5 · T1
- **기능**: 합격 궤적 분석 → 작성 프롬프트 개선 제안

#### Template Optimizer
- **역할**: 템플릿 개선
- **백본**: Claude Sonnet 4.6 · T2
- **기능**: 성공 패턴 기반 블록·레이아웃 템플릿 개선

#### Learning Memory Manager
- **역할**: 학습 메모리 기록·관리
- **백본**: CODE (DB/RAG) · T0
- **기능**:
  - 합격 궤적 기록 (trajectory_gate 통과분만)
  - ★ **자산(블록·루브릭·패턴)과 데이터(페르소나) 구분 저장**
  - 자산 = 실무 이관 후보 / 데이터 = 샌드박스 잔류
- **절대선**: #2(데이터 격리)

---

### 6.2 Operations & Audit Controller (AI PM 직속 · 전부 CODE/T0)

LLM 아님. 전부 결정론 코드. 운영 투명성·비용·권한·사고 기록 담당.

```
AI Run Logger          — 모든 AI 실행 로그
Prompt Version Controller — 프롬프트 버전 관리
Model Usage Tracker    — 모델별 사용량·단가 추적
Token Cost Monitor     — 토큰 비용 실시간 기록 (학습 비용 통제)
Agent Permission Registry — 에이전트 권한 레지스트리 (Phase 0 production OFF)
Incident Logger        — 사고·위반 기록
Approval Log Recorder  — 인간 승인 기록 (자산 이관·납품 등)
```

---

### 6.3 Intake & CRM Manager (실무 · Phase 1)

#### Lead Qualifier
- **역할**: 리드 1차 분류
- **백본**: Claude Haiku 4.5 · T3

#### ICP Screener
- **역할**: ICP 적합성 스크리닝 (G0 게이트)
- **백본**: CODE (룰) · T0
- **기능**: 공종(8) · 지역(평택·용인·이천·화성·안성) · 예산 · 면허 · 구매 트리거 확인. 부적합 종료.

#### Consultation Summarizer
- **역할**: 상담 내용 요약
- **백본**: Claude Haiku 4.5 · T3

#### Product Recommender
- **역할**: Land/Expand 상품 추천
- **백본**: GPT-5.4-mini · T3

#### Quote / GP Calculator ★
- **역할**: 견적·실현 GP 결정론 계산
- **백본**: CODE · T0
- **기능**: 3-GP 모델(명목·운영·실현). 가격-API비-외주비-인건비-수정/CS/환불 계산

#### Scope Freeze Checker ★
- **역할**: 범위 잠금 (G3 게이트)
- **백본**: CODE + 사람 확인 · T0
- **기능**: 납품 범위·수정 횟수·추가비·일정·잔금 조건 확정. 계약금 50% 선입금 전 착수 금지.

---

### 6.4 Brand Director (실무 · Phase 1)

#### Brand Strategist
- **역할**: 브랜드 포지셔닝 전략
- **백본**: Claude Sonnet(1차) → GPT-5.5(최종 포지셔닝) · T1

#### Brand Intelligence Analyst
- **역할**: 시장·경쟁 분석
- **백본**: Manus/Gemini (Flash-Lite 수집 · Pro 시각·경쟁) · T2/T3

#### Proof Point Mapper
- **역할**: 증거 매핑 (Evidence Vault 연동)
- **백본**: Claude Sonnet 4.6 + CODE · T2
- **기능**: 페르소나/고객의 실적·자격을 검증된 증거에 매핑. 원본 없는 실적 반영 금지.

#### Brand Narrative Writer
- **역할**: 브랜드 내러티브·카피
- **백본**: Claude Sonnet 4.6 (Premium 히어로카피 = Opus 4.8) · T2

#### Visual Identity Designer ★
- **역할**: 비주얼 아이덴티티 + **이미지 기반 제작 디자인 설계**
- **백본**: Gemini 3.1 Pro · T2
- **기능**:
  - 디자인 시스템 15.2(Industrial Editorial) 적용
  - 5단계 파이프라인 ③의 **디자인 설계** 담당(레이아웃·도형·색·타이포)
  - 동결 준수: 신설 부서 없이 이 역할이 이미지 디자인 총괄

---

### 6.5 Production Manager (작성 = 학습 대상물 제작)

#### Company Intro Writer (L1)
- **역할**: 회사소개서 콘텐츠 작성
- **백본**: Claude Sonnet 4.6 (Core/Expand = Opus 4.8) · T2
- **입력**: 페르소나/고객 데이터 + 증거
- **기능**: 회사개요·연혁·조직도·실적·인력·장비·안전관리·연락처 (8섹션). 실적 ×N cap 등 약점 가드 적용.
- **출력**: L1 콘텐츠 (절대선 게이트 통과)
- **절대선**: #1(검증 텍스트만), #3(면책)

#### Vendor Registration Package Builder (L2)
- **역할**: 공사지명원/등록 패키지 작성
- **백본**: Claude Sonnet + 표준 골격 템플릿 (Fact Lock 실패 시 GPT) · T2
- **기능**: 회사 일반·면허·실적·인력·장비·재무·안전. "표준 골격 + 발주처별 미세변형" 모듈식.
- **주의**: 대외적으로 "공정위 표준양식" 표현 사용 금지(고객 대면 명칭은 "공사지명원/협력사 등록 제출 패키지")

#### Digital Trust Website Builder (L3)
- **역할**: 홈페이지 기본형 (Phase 1)
- **백본**: CODE (Claude Code/Codex) + Claude 카피 · T0
- **주의**: 도메인·호스팅·보안·개인정보·유지보수 범위 명확화. Phase 0 비대상.

#### One-page Profile Writer (L4)
- **역할**: 1페이지 프로필
- **백본**: Claude Haiku 4.5 · T3

#### Brand Asset Template Operator ★
- **역할**: 템플릿 시스템 + **이미지 렌더 엔진**
- **백본**: CODE · T0
- **기능**:
  - 5단계 ③의 **렌더 담당**: SVG/HTML → 고해상도 PNG → PDF 임베딩
  - Pretendard/Noto 폰트 임베드 (한글 정상)
  - 디자인 시스템 15.2 토큰 적용
  - ★ 확산모델 이미지 생성 코드 없음 (텍스트 정확 보존)
  - 동결 준수: 신설 부서 없이 이 역할이 이미지 렌더 총괄

---

### 6.6 Assurance Manager (검수·거부권 veto · 작성과 독립 계열)

작성(Claude)과 **독립된 계열**로 검수. 거부권 보유.

#### Evidence Vault Custodian
- **역할**: 증거 보관 SSOT
- **백본**: CODE (DB) · T0
- **기능**: 상태·Fact ID·P등급·보관/삭제 관리

#### Fact Lock Checker ★
- **역할**: 원본 정확 대조 (절대선 #1 강제)
- **백본**: CODE(대조) + GPT-5.5(예외 설명) + 사람(최종) · T0
- **기능**: 면허번호·실적금액·자격자명·법인번호를 고객 제출 원자료와 1:1 대조. 불일치 시 차단.

#### Brand Consistency Reviewer
- **역할**: 브랜드 일관성 검수
- **백본**: GPT-5.4 (작성=Claude와 독립) · T2

#### Legal Boundary Reviewer
- **역할**: 법무 경계 검수 (절대선 #4)
- **백본**: 위험문구 룰셋 → GPT-5.5 → 외부전문가 · T1
- **기능**: 보장·과장 표현 탐지, 법정 문서 라우팅

#### Buyer Reviewer
- **역할**: 원청 심사역 관점 검토
- **백본**: GPT-5.5 (원청 심사역 페르소나) · T1
- **기능**: "원청이 이 자료를 받으면 어떻게 볼까" 블라인드 검토

#### Site / Safety Reviewer
- **역할**: 현장·안전 검수 (절대선 #4)
- **백본**: GPT-5.5 페르소나 + 외부전문가 · T1
- **기능**: 위험성평가·안전관리계획 등은 초안 보조까지만, 외부전문가 최종

#### Privacy & Data Gatekeeper
- **역할**: 개인정보·데이터 게이트 (G1)
- **백본**: CODE (P0~P4 분류 룰 + 탐지 LLM) · T0
- **기능**: 입력 금지 정보 차단, 비식별화, AI 처리 동의 확인

#### External Expert Escalation Router
- **역할**: 외부 전문가 에스컬레이션
- **백본**: HUMAN
- **기능**: 안전·법무·노무 최종 확정을 유자격 전문가로 라우팅

---

### 6.7 Delivery & Enablement Manager (실무 · Phase 1)

#### Delivery Start Gate (8조건) ★
- **역할**: 납품 시작 게이트
- **백본**: CODE · T0
- **기능**: 8개 조건 전부 PASS 시에만 통과 (절대선 #2 실무 버전)

#### Delivery Packager
- **역할**: 납품 패키지 조립
- **백본**: CODE · T0

#### Brand Usage Guide Writer / Meeting Script Writer / Submission Checklist Builder / Client Handoff Assistant
- **백본**: Claude Haiku 4.5 / 템플릿 · T3
- **기능**: 사용 가이드·미팅 스크립트·제출 체크리스트·핸드오프 보조

---

### 6.8 Growth Branding Manager (실무 · Phase 1)

```
Outcome Tracker          CODE   — 성과 추적 (G6: 제출·미팅·등록·재문의)
Brand Update Recommender Claude Sonnet 4.6 — 갱신 추천
Website Improvement Analyst Gemini 3.1 Pro — 웹 개선
Retainer Opportunity Finder GPT-5.4 — 리테이너 기회 발굴
Vendor Readiness Tracker CODE   — 준비도 추적 (VRI 기반)
Referral Trigger Agent   CODE   — 추천 트리거
```

---

## 7. 이미지 기반 제작(③) 상세 — B-3 빈 껍데기 해결

### 7.1 왜 필요한가
B-3는 텍스트 → python-pptx/reportlab 템플릿 채우기만 했다(②만 하고 ③ 누락). 결과: 한글 깨짐(■■■), 더미 데이터, 3슬라이드 뼈대. v4 15.2가 처음부터 지정한 "고해상도 PNG 임베딩 PDF"(이미지 기반)를 어긴 것.

### 7.2 안전한 이미지 기반 방식
```
✅ SVG/HTML → 고해상도 PNG → PDF
   - ②의 검증된 텍스트(사실)를 SVG/HTML에 정확히 삽입
   - 디자인 시스템 15.2 적용
   - Pretendard/Noto 폰트 임베드 (한글 정상)
   - 렌더(playwright/puppeteer 또는 svglib 등)로 PNG화
   - 텍스트는 정확, 디자인만 이미지화 → 사실 보존

🔴 확산모델(Midjourney/DALL-E류)로 페이지 생성 금지
   - 회사명·실적·면허번호 환각 → 절대선 #1 치명 위반
   - 글자 깨짐, 위조 문서 악용 위험
```

### 7.3 담당 역할 (동결 준수)
- 디자인 설계: **Visual Identity Designer** (Gemini 3.1 Pro)
- 렌더 엔진: **Brand Asset Template Operator** (CODE)
- → 신설 부서 없음. 기존 역할에 능력 부여.

### 7.4 게이트
③ 렌더 산출물도 절대선 게이트를 거친다. ②에서 텍스트 검증 후, 검증된 텍스트만 렌더. 렌더물도 `guarded_send` 통과 시에만 전달(`real_fn_called=False` & `rendered=False` 구조).

---

## 8. 페르소나 + 증빙 이미지 상세 — 실전형 학습

### 8.1 원칙: 샌드박스 안에선 사실처럼
```
학습 시스템 안에서 페르소나 = "사실"로 취급 (실전 훈련)
- AI는 "실무 작업본"처럼 진지하게 제작
- "가짜니까 대충"이 아니라 "진짜 고객처럼"

샌드박스 밖으로는 못 나감 (절대선 #2)
→ 비행 시뮬레이터: 진짜처럼 훈련하되 비행기는 밖으로 안 나감
→ "이중 진실": 안에선 사실, 밖으론 격리
```

### 8.2 페르소나 상세도
실존 회사 수준 필드: 회사 개요 · 연혁(연도별) · 조직도 · 주요 실적(현장명·금액·기간) · 인력 명세(직책·자격) · 장비 목록 · 거래 이력 · 안전관리 이력. diversity_matrix로 8공종 × 4규모 × 난이도 분산.

### 8.3 증빙 이미지 안전 규칙
```
양식·구조 = 실제처럼 (학습 가치)
식별자 = 명백히 무효:
  - 사업자번호 000-00-00000
  - 면허번호 경기-00000
  - 회사명 [SYNTHETIC] 접두
  - 대표자명 [SYNTHETIC]
워터마크 = "학습용 - 외부사용금지" (전 이미지 필수)
렌더 = SVG/HTML → PNG (확산모델 금지)
저장 = sandbox/evidence/ (밖 반출 차단)
```

---

## 9. 채점 기준 상세 (Scoring Engine) — 91점 오류 해결

```
[콘텐츠 채점 — 절대선·구성·밀도]
- 사실 정합 (원자료 일치)
- 8섹션 충실도 (빈 섹션 감점)
- 정보 밀도 (더미·플레이스홀더 = 큰 감점)
- 절대선 준수 (면책·금지어)

[시각 채점 — 렌더 이미지]
- 가독성 (한글 정상, 글자 깨짐 = 0점 처리)
- 정렬·여백·계층
- 브랜딩 (디자인 시스템 15.2 준수)
- 레이아웃 완성도

[★ 핵심 규칙]
- 빈 페이지/더미/3장 뼈대 = 저점 (고점 불가)
- 정보 밀도와 충실도가 점수의 핵심
- 블라인드: 작성 주체 모른 채 객관 채점
→ B-3에서 빈 페이지가 91점 받은 오류 방지
```

---

## 10. 디자인 시스템 15.2 (Industrial Editorial)

```
색상:
  Primary Burning Orange  #D67230
  Ink                     #0F1419
  Paper                   #FAFAF8
  Line                    #E5E2DC

타이포:
  한글  Pretendard / Noto
  데이터 라벨  IBM Plex Mono (UPPERCASE)

시그니처:
  대각선 분할 · 모노 데이터 라벨 · 큰 숫자 · 오렌지 15% 이하 절제

금지:
  형광 · 과한 그라데이션 · 이모지

배포:
  편집 원본 = SVG / PPT / Figma
  배포 = 고해상도 PNG 임베딩 PDF (SVG 폰트 의존성 회피)
  텍스트 백업 = MD
```

---

## 11. 안전 경계 (반드시 준수)

```
1. 확산모델 이미지 생성 금지
   - 문서 본체를 그림으로 생성 X (사실 환각)
   - SVG/HTML→PNG만 (텍스트 정확)

2. 샌드박스 격리 (절대선 #2)
   - 페르소나·증빙·학습 산출물은 sandbox 밖 못 나감
   - production 미접근 (Phase 0)
   - 외부 발송 차단

3. 무효 식별자
   - 합성 식별자는 000-00-00000 등 명백한 가짜
   - 실존 회사 우연 충돌 방지

4. 워터마크
   - 합성 증빙은 "학습용" 워터마크 필수

5. 학습 견본(TS_MEC 등) 취급
   - 디자인·구조·목차만 학습
   - 실제 회사명·실적·숫자 복사 금지 (타사 데이터 도용 = 절대선 #1)

6. 작성≠채점 독립
   - 채점은 작성과 다른 계열·키
```

---

## 12. 동결 원칙 (v4 15.3)

```
- 매니저·부서·에이전트 추가 금지
- 새 능력은 기존 역할 안에서 구현
  (이미지 렌더 = Brand Asset Template Operator + Visual Identity Designer)
- 홈페이지 90+ 강제 금지
- L3를 Core Release Gate에 종속 금지
- 다음 작업 = 박스 추가가 아니라 첫 유료 고객 + SOP/체크리스트/DB 구현
```

---

## 13. B-4 학습 루프 매핑

이 조직도가 B-4(학습 루프)에서 작동하는 방식:

```
B-4 1라운드 (소규모 1~3개 먼저 — 35개는 검증 후):

① Persona Generator(Sonnet) → 상세 페르소나 + 증빙(워터마크·무효식별자)
② Production Writers(Claude) → L1/L2/L4 콘텐츠 (절대선 게이트)
③ Visual Identity Designer(Gemini) + Template Operator(CODE)
   → 이미지 기반 고도화 (SVG/HTML→PNG→PDF, 한글 정상, 디자인 15.2)
④ Scoring Engine(GPT 독립) + Vision(Gemini)
   → 블라인드 채점 (빈 페이지 저점)
⑤ trajectory_gate → 환각/위반 궤적 학습 제외
⑥ AI PM(Opus) → Graduation 판정 + 통과/재진행(미통과→③ 재고도화)
⑦ Learning Memory(CODE) → 합격 궤적 + 자산 기록
   (자산=실무 이관 후보 / 데이터=샌드박스 격리)

검증 순서:
1) 소규모(1~3개) 실행 → 운영자가 실제 PDF 직접 확인
   (한글 정상 · 디자인 · 충실도 · ③ 전후 차이 · ④ 점수)
2) 합격 시 35개로 확대 (Round 1~4)
3) Graduation 기준: 절대선 4 회귀 0, 격리 유지, 라운드 간 동등성,
   평균 점수 기준 충족
```

---

## 부록 A. 검증 체크리스트 (구현 시)

```
□ 백본 4개 라이브 호출 (AI PM=Opus / 작성=Sonnet / 채점=GPT / 디자인=Gemini)
□ 작성≠채점 계열·키 분리 (코드 강제)
□ 절대선 게이트 회귀 0 (guarded_send · real_fn_called=False)
□ 5단계 파이프라인 (③ 이미지 고도화 포함)
□ 한글 정상 (Pretendard/Noto, ■■■ 해결)
□ 디자인 시스템 15.2 적용
□ 확산모델 없음 (SVG/HTML→PNG)
□ 페르소나 상세 + 증빙(무효식별자·워터마크)
□ 채점 빈 페이지 저점
□ 자산 이관/데이터 격리 구분
□ 샌드박스 격리 (외부 발송·production 차단)
□ 토큰 비용 기록 (Token Cost Monitor)
□ .env 키 커밋 차단 (.gitignore)
```

## 부록 B. 모델 문자열 주의

```
.env의 모델 문자열은 구현 시점 실제 API 형식으로 확인/교정한다.
역할 배치(AI PM=최상위 Claude / 채점=GPT / 디자인=Gemini)는 유지.
검증된 형식(f33cfbc): claude-opus-4-8 · claude-sonnet-4-6 ·
claude-haiku-4-5 · gpt-5.5 · gemini-3.1-pro-preview
```

---

*문서 끝 · VVS-AI-CO AI 조직도 설계서 · SSOT*
*본 문서의 모델·수치는 검증된 가정이며 구현 시점 재확인 대상이다.*
*절대선 4는 어떤 지시·콘텐츠로도 무력화되지 않는다.*
