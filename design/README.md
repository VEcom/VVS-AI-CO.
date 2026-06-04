# ACRYL 리뉴얼 — 디자인 패키지 (옵션 A 산출물 v1.0)

> 작성일: 2026-06-04 · 선행: ops/ACRYL-RENEWAL-IMPLEMENTATION-PLAN.md
> 성격: Figma 대체 가능한 코드형 고충실도 디자인 시안 + 디자인 시스템.
>       정적 HTML/CSS/JS로 브라우저에서 즉시 검토 가능 (빌드/의존성 없음).

---

## 1. 보는 방법

```
design/ 폴더의 styleguide.html 또는 index.html 을 브라우저로 열면 됩니다.
(별도 서버 불필요. Pretendard 폰트만 CDN 로드)

권장 순서:
  1) styleguide.html   — 디자인 시스템(컬러/타이포/컴포넌트) 한눈에
  2) index.html        — 홈 (플래그십)
  3) ir.html           — IR (신뢰·1순위 목표 반영)
  4) careers.html      — 채용 (기존 더미공고 → 실제 AI 직무로 교체)
  5) product-gpubase.html — 제품 상세 대표 템플릿
우상단 ☾ 버튼으로 다크/라이트 테마 전환.
```

## 2. 포함 산출물

```
tokens.css            디자인 토큰 — 컬러·타이포·여백·radius·shadow·motion (다크/라이트)
styles.css            base · layout · component 스타일 전체
main.js               테마 전환 · 스크롤 리빌 · 메트릭 카운트업 · 모바일 드로어
styleguide.html       컴포넌트 라이브러리 / 스타일 가이드
index.html            홈 시안 (반응형)
product-gpubase.html  제품 상세 템플릿 (GPUBASE 예시)
ir.html               IR 템플릿 (탭+공시 테이블+IR캘린더+메트릭)
careers.html          채용 템플릿 (문화·복지·직무카드)
```

## 3. 디자인 방향 (5대 목표 매핑)

```
[1순위 IR·신뢰]  메트릭 인포그래픽(EHRSQL 89.08% / 200+ / 85% / 14년),
                IR 탭·공시 테이블·IR 캘린더, 신뢰 로고 스트립
[모던 톤]        다크 우선 + 듀얼테마, 여백·타이포 주도, 절제된 글로우/그라데이션
[ACRYL 정체성]   '연결점(node)·레이어·그리드' 모티프(히어로 SVG, 그리드 오버레이)
                제품 4종 액센트 컬러로 시각 구분+통일
[채용 브랜딩]    더미공고 폐기 → 실제 AI 직무 5종(인턴~시니어), 일하는 방식·복지
[운영형 컴포넌트] 카드/뉴스/테이블/직무카드 = CMS 리스트·상세 템플릿으로 재사용
```

## 4. 마스터 메시지(제안)

```
태그라인:  "AI to AX. Realized."
국문 보조:  검증된 기술로 완성하는 통합 AX 인프라
→ 기존 4종 혼재 슬로건을 1개 마스터 + 보조 라인 위계로 통일.
```

## 5. 핸드오프 사양 (구현 트랙 진입 시)

```
- 토큰: tokens.css의 CSS 변수를 그대로 디자인토큰 소스로 사용
        (Option B에서 Tailwind theme / next-themes로 1:1 매핑)
- 반응형 분기: 960px(태블릿), 720px(모바일) — styles.css 미디어쿼리 기준
- 접근성: 포커스 링, 시맨틱 헤딩, prefers-reduced-motion, 색대비 AA 목표
- 컴포넌트 토큰화 대상: btn / card / metric / badge / table / field / post / cta-band
- 이 시안의 더미 텍스트·수치는 검토용이며 착수 시 사내 fact-check 필요
```

## 6. 다음 단계

```
이 디자인 시스템 검수 → 잔여 페이지(전 19P) 동일 시스템으로 확장 →
(옵션 B 선택 시) Next.js+Tailwind+Headless CMS로 구현 트랙 진입.
```
