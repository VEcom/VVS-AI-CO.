/*
 * data.js — 리조트피플 모바일 리플렛 데이터 (프로토타입)
 *
 * 실서비스에서는 이 데이터가 MySQL + 관리자 페이지로 대체된다.
 *  - BRAND  : 본사가 통제하는 공통 요소(브랜드 소개·콘텐츠 카테고리·디자인 토큰).
 *  - BRANCHES : 9개 지점. 공통 구조는 동일하되 지점별 내용만 차별화.
 *
 * 관리자 권한 2단계 매핑:
 *   - 본사 : BRAND 전체 + 모든 BRANCH 편집
 *   - 지점 : 자사 BRANCH 의 leads 조회만 (편집 불가)  ← admin.html 데모에서 확인
 */

window.RP_DATA = {
  brand: {
    name: "리조트피플",
    nameEn: "RESORT PEOPLE",
    tagline: "도심 속 리조트, 매일이 휴양처럼",
    intro:
      "리조트피플은 ‘운동’을 ‘휴양’의 경험으로 바꾸는 프리미엄 피트니스 & 웰니스 브랜드입니다. " +
      "넓은 공간, 충분한 기구, 밀착 트레이닝, 그리고 지점마다 다른 시그니처 프로그램으로 " +
      "당신의 하루에 리조트의 여유를 더합니다.",
    // 본사 공통 콘텐츠 카테고리 (모든 지점 동일 노출)
    contents: [
      { icon: "🏋️", title: "프리웨이트 존", desc: "넉넉한 기구 수로 대기 없이, 원하는 무게는 마음껏." },
      { icon: "🏃", title: "디지털 카디오", desc: "기록을 측정하며 성장하는 몰입형 유산소 라운지." },
      { icon: "🧘", title: "웰니스 스튜디오", desc: "필라테스·요가·스트레칭 — 회복과 밸런스." },
      { icon: "🤸", title: "펑셔널 존", desc: "러닝·클라이밍·서킷에 대비한 기능성 트레이닝." },
    ],
    // 인센티브(리드 등록 보상) — 본사 정책, 지점 공통
    incentive: {
      headline: "사전등록하면 오픈 특가 + 네이버페이",
      reward: "네이버페이 상품권 1만원권",
      condition: "사전등록 후 오픈일 방문 상담 시 100% 지급",
      referral: "친구에게 링크 공유 시, 친구 등록당 추가 5,000원권",
    },
    privacy: {
      purpose: "지점 오픈세일 알림 및 서비스 이용 개시 안내",
      retention: "개인정보 보유 및 이용기간 : 3년",
    },
  },

  // ── 9개 지점 ──
  branches: [
    {
      id: "mapo",
      name: "마포점",
      status: "사전예약",
      headline: "마포에 압도적 웰니스 성지가 생깁니다",
      openDate: "2026-07-01",
      address: "서울 마포구 마포대로 100, 리조트피플타워 3–5F",
      area: "공덕역 2번 출구 도보 3분",
      hero: "linear-gradient(135deg,#1A2233,#FF5A1F)",
      signature: "디지털 카디오 라운지 + 펑셔널 존 국내 최대 규모",
      milestone: { label: "사전예약 50명 달성 시 평생회원가 고정", current: 38, target: 50 },
      trainers: [
        { name: "김도윤", role: "퍼포먼스 코치", tag: "근력·체형교정", img: "💪" },
        { name: "이서연", role: "필라테스 마스터", tag: "재활·코어", img: "🧘‍♀️" },
        { name: "박준호", role: "러닝 디렉터", tag: "마라톤·심폐", img: "🏃‍♂️" },
      ],
      schedule: [
        { time: "06:00", mon: "모닝버닝", wed: "모닝버닝", fri: "모닝버닝" },
        { time: "12:00", mon: "런치필라테스", wed: "코어서킷", fri: "런치필라테스" },
        { time: "19:00", mon: "그룹펑셔널", wed: "디지털러닝", fri: "그룹펑셔널" },
        { time: "21:00", mon: "스트레칭&회복", wed: "스트레칭&회복", fri: "스트레칭&회복" },
      ],
      event: {
        title: "7월 오픈 캐치업 이벤트",
        desc: "사전예약 고객 한정 — 12개월권 결제 시 PT 4회 + 인바디 무제한.",
        until: "2026-06-30",
      },
    },
    { id: "gangnam", name: "강남점", status: "운영중", headline: "강남 한복판, 리조트의 여유",
      openDate: "운영중", address: "서울 강남구 테헤란로 152, 5F", area: "강남역 11번 출구 도보 5분",
      hero: "linear-gradient(135deg,#1A2233,#D94510)", signature: "프리웨이트 존 2배 확장 + 사우나",
      milestone: { label: "6월 재등록 회원 PT 2회 적립", current: 120, target: 150 },
      trainers: [ { name:"정유진", role:"헤드 코치", tag:"다이어트·근비대", img:"🏋️‍♀️" }, { name:"최민석", role:"웨이트 코치", tag:"파워리프팅", img:"🏋️" } ],
      schedule: [ {time:"07:00",mon:"모닝웨이트",wed:"모닝웨이트",fri:"모닝웨이트"}, {time:"18:30",mon:"그룹GX",wed:"스피닝",fri:"그룹GX"}, {time:"20:00",mon:"코어&스트레칭",wed:"코어&스트레칭",fri:"코어&스트레칭"} ],
      event: { title:"6월 데일리 출석 챌린지", desc:"월 20회 출석 시 단백질 보충제 증정.", until:"2026-06-30" } },
    { id: "songpa", name: "송파점", status: "운영중", headline: "송파 패밀리 웰니스 클럽",
      openDate: "운영중", address: "서울 송파구 올림픽로 300, 2–3F", area: "잠실역 3번 출구 도보 4분",
      hero: "linear-gradient(135deg,#1A2233,#FF7A3C)", signature: "키즈존 + 패밀리 라커",
      milestone: { label: "가족 동반 등록 시 1인 무료", current: 64, target: 80 },
      trainers: [ { name:"한지원", role:"키즈 PT", tag:"성장·체형", img:"🧒" }, { name:"오세훈", role:"재활 트레이너", tag:"통증·자세", img:"🩹" } ],
      schedule: [ {time:"10:00",mon:"키즈짐",wed:"키즈짐",fri:"키즈짐"}, {time:"19:00",mon:"패밀리요가",wed:"코어서킷",fri:"패밀리요가"} ],
      event: { title:"여름방학 키즈 패키지", desc:"키즈 8주 프로그램 + 체형분석 리포트.", until:"2026-07-15" } },
    { id: "bundang", name: "분당점", status: "운영중", headline: "분당 직장인 회복 거점",
      openDate: "운영중", address: "경기 성남시 분당구 황새울로 200, 4F", area: "서현역 1번 출구 도보 2분",
      hero: "linear-gradient(135deg,#1A2233,#E85A2A)", signature: "런치 회복 프로그램 + 마사지건 라운지",
      milestone: { label: "런치회원 전용 라커 무료", current: 90, target: 100 },
      trainers: [ { name:"신예린", role:"회복 코치", tag:"스트레칭·이완", img:"💆‍♀️" } ],
      schedule: [ {time:"12:00",mon:"런치필라테스",wed:"런치HIIT",fri:"런치필라테스"}, {time:"19:30",mon:"이브닝웨이트",wed:"이브닝웨이트",fri:"이브닝웨이트"} ],
      event: { title:"런치 멤버십 30%", desc:"평일 11–14시 전용권 한정 특가.", until:"2026-06-30" } },
    { id: "ilsan", name: "일산점", status: "운영중", headline: "일산 호수처럼 넓은 공간",
      openDate: "운영중", address: "경기 고양시 일산동구 중앙로 1000, 3F", area: "정발산역 도보 6분",
      hero: "linear-gradient(135deg,#1A2233,#C9420F)", signature: "대형 GX홀 + 스피닝 전용관",
      milestone: { label: "GX 무제한권 런칭가", current: 45, target: 60 },
      trainers: [ { name:"문가영", role:"GX 디렉터", tag:"줌바·스피닝", img:"💃" } ],
      schedule: [ {time:"10:00",mon:"줌바",wed:"스피닝",fri:"줌바"}, {time:"20:00",mon:"바디펌프",wed:"코어",fri:"바디펌프"} ],
      event: { title:"GX 무제한 얼리버드", desc:"선착순 60명 평생 할인가 고정.", until:"2026-07-10" } },
    { id: "incheon", name: "인천점", status: "운영중", headline: "인천 베이프론트 피트니스",
      openDate: "운영중", address: "인천 연수구 컨벤시아대로 50, 2F", area: "센트럴파크역 도보 3분",
      hero: "linear-gradient(135deg,#1A2233,#FF5A1F)", signature: "오션뷰 카디오 라운지",
      milestone: { label: "오션뷰 트레드밀 예약제", current: 30, target: 50 },
      trainers: [ { name:"배성우", role:"카디오 코치", tag:"러닝·감량", img:"🏃" } ],
      schedule: [ {time:"06:30",mon:"선라이즈런",wed:"선라이즈런",fri:"선라이즈런"}, {time:"19:00",mon:"펑셔널",wed:"펑셔널",fri:"펑셔널"} ],
      event: { title:"오션뷰 오픈 기념", desc:"신규 6개월권 + 1개월 추가.", until:"2026-06-30" } },
    { id: "daejeon", name: "대전점", status: "운영중", headline: "대전 과학의 도시, 데이터 트레이닝",
      openDate: "운영중", address: "대전 유성구 대학로 99, 3F", area: "유성온천역 도보 5분",
      hero: "linear-gradient(135deg,#1A2233,#D94510)", signature: "인바디 무제한 + 데이터 코칭",
      milestone: { label: "데이터 PT 패키지 런칭", current: 22, target: 40 },
      trainers: [ { name:"노지훈", role:"데이터 코치", tag:"체성분·기록", img:"📊" } ],
      schedule: [ {time:"12:00",mon:"데이터HIIT",wed:"코어",fri:"데이터HIIT"}, {time:"19:00",mon:"웨이트",wed:"웨이트",fri:"웨이트"} ],
      event: { title:"체성분 챌린지", desc:"8주 변화 1위 100만원 상당 상품.", until:"2026-07-31" } },
    { id: "busan", name: "부산점", status: "사전예약", headline: "부산 해운대, 곧 오픈합니다",
      openDate: "2026-08-01", address: "부산 해운대구 해운대로 200, 5F", area: "해운대역 도보 4분",
      hero: "linear-gradient(135deg,#1A2233,#FF7A3C)", signature: "루프탑 요가 데크",
      milestone: { label: "사전예약 평생회원가 고정", current: 18, target: 50 },
      trainers: [ { name:"강하늘", role:"요가 마스터", tag:"빈야사·명상", img:"🧘" } ],
      schedule: [ {time:"07:00",mon:"루프탑요가",wed:"루프탑요가",fri:"루프탑요가"}, {time:"19:00",mon:"펑셔널",wed:"카디오",fri:"펑셔널"} ],
      event: { title:"8월 오픈 사전예약", desc:"선착순 50명 평생 최저가.", until:"2026-07-25" } },
    { id: "gwangju", name: "광주점", status: "운영중", headline: "광주 도심 웰니스 허브",
      openDate: "운영중", address: "광주 서구 상무중앙로 30, 4F", area: "상무역 도보 3분",
      hero: "linear-gradient(135deg,#1A2233,#E85A2A)", signature: "24시간 무인 운영존",
      milestone: { label: "심야회원 라커 무료", current: 55, target: 70 },
      trainers: [ { name:"임재현", role:"24h 코치", tag:"자율운동·홈케어", img:"🌙" } ],
      schedule: [ {time:"06:00",mon:"얼리버드",wed:"얼리버드",fri:"얼리버드"}, {time:"22:00",mon:"나이트핏",wed:"나이트핏",fri:"나이트핏"} ],
      event: { title:"24시간 멤버십 오픈", desc:"심야 전용권 첫달 무료.", until:"2026-06-30" } },
  ],
};
