# 리조트피플 모바일 리플렛 플랫폼 — 산출물

Kmong 의뢰 #226253 ("리조트피플 모바일 프로모션 리플렛 플랫폼 구축")에 대한
**제안서 + 동작 프로토타입** 산출물입니다. 레퍼런스는 `service.butfit.io/lead/mapo`.

## 구성

```
resortpeople-leaflet/
├── 제안서.md          ★ 의뢰인 질문(일정·비용·관리자·수정·확장) 직접 답변 + 범위
├── index.html         모바일 리플렛 랜딩 (9개 지점 동적)
├── admin.html         관리자 2단계(본사/지점) 컨셉 데모
├── css/style.css      반응형 스타일 (VVS Design System 15.2 · Burning Orange)
├── js/
│   ├── data.js        9개 지점 + 브랜드 공통 데이터 (실서비스=MySQL+관리자)
│   ├── app.js         렌더링 + 리드폼 + UTM + 링크공유
│   └── admin.js       권한별 리드 열람/편집/CSV
└── server/
    ├── schema.sql     MySQL 8 스키마 (branches/brand/admins/leads)
    └── app.js         Express API 스캐폴드 (공개+관리자, 권한 강제)
```

## 실행

```bash
cd deliverables/resortpeople-leaflet
python3 -m http.server 8080
# 랜딩  : http://localhost:8080/index.html?branch=mapo
# 관리자: http://localhost:8080/admin.html
```

랜딩에서 사전예약을 신청하면 관리자(admin.html)의 리드 목록에 반영됩니다.
권한을 '본사 ↔ 지점'으로 바꿔 열람 범위/편집권한 차이를 확인하세요.

## 핵심 설계

- **1 코드베이스 · 9 데이터** — 지점 확장은 데이터 1건 추가(구조 변경 없음).
- **공통(본사) / 지점별** 콘텐츠 분리 — 브랜드 일관성 + 지점 자율성.
- **권한 2단계 서버 강제** — 지점은 자사 리드 조회만(`server/app.js` 참조).
- **링크 배포 최적화** — `?branch=ID` 라우팅, OG카드, Web Share/복사, UTM 캡처.

> 본 결과물은 의뢰 평가/착수용 프로토타입입니다. 실서비스 전환 항목은 `제안서.md` 4절 참조.
