/*
 * server/app.js — 리조트피플 리플렛 백엔드 스캐폴드 (Express + MySQL)
 *
 * 본 파일은 실서비스 백엔드의 "청사진(스텁)" 입니다. 프로토타입 프론트는 서버 없이도
 * 동작하지만(localStorage), 운영 단계에서 이 라우트들이 그대로 채워집니다.
 *
 *   공개 API
 *     GET  /api/branches            지점 목록
 *     GET  /api/branches/:id        지점 상세(공통+지점별 병합)
 *     POST /api/leads               리드 등록 (랜딩 폼)
 *   관리자 API (세션/JWT 권한 검사)
 *     GET  /api/admin/leads         본사=전체 / 지점=자사만 (서버에서 강제 필터)
 *     PUT  /api/admin/branches/:id  본사 또는 해당 지점만
 *     PUT  /api/admin/brand         본사 전용
 *
 * 실행: npm i express mysql2 && node server/app.js
 */
const express = require("express");
// const mysql = require("mysql2/promise");
const app = express();
app.use(express.json());

// const pool = mysql.createPool({ host: process.env.DB_HOST, user: process.env.DB_USER,
//   password: process.env.DB_PASS, database: "resortpeople", waitForConnections: true });

// ── 권한 미들웨어: 2단계(본사/지점) 강제 ──
function auth(req, res, next) {
  // 실제로는 세션/JWT 에서 복원. 여기서는 헤더 데모.
  req.admin = { role: req.headers["x-role"] || "branch", branch_id: req.headers["x-branch"] || null };
  next();
}

// ── 공개: 지점 ──
app.get("/api/branches", async (req, res) => {
  // const [rows] = await pool.query("SELECT id,name,status FROM branches ORDER BY name");
  res.json({ ok: true, note: "stub", branches: [] });
});

app.get("/api/branches/:id", async (req, res) => {
  // const [[b]] = await pool.query("SELECT * FROM branches WHERE id=?", [req.params.id]);
  // const [[brand]] = await pool.query("SELECT * FROM brand_settings WHERE id=1");
  res.json({ ok: true, note: "stub: 공통(brand)+지점(branch) 병합 반환", id: req.params.id });
});

// ── 공개: 리드 등록 ──
app.post("/api/leads", async (req, res) => {
  const L = req.body || {};
  if (!L.branch_id || !L.name || !L.phone)
    return res.status(400).json({ ok: false, error: "branch_id, name, phone 필수" });
  // await pool.query(
  //   `INSERT INTO leads (branch_id,name,phone,program,source,marketing_agree,
  //      utm_source,utm_medium,utm_campaign,referrer_id)
  //    VALUES (?,?,?,?,?,?,?,?,?,?)`,
  //   [L.branch_id, L.name, L.phone, L.program, L.source, L.marketing_agree?1:0,
  //    L.utm?.utm_source, L.utm?.utm_medium, L.utm?.utm_campaign, L.referrer_id||null]);
  res.json({ ok: true, note: "stub: 리드 저장 + 인센티브 트리거 + 알림(슬랙/문자)" });
});

// ── 관리자: 리드 조회 (권한별 필터를 서버가 강제) ──
app.get("/api/admin/leads", auth, async (req, res) => {
  const { role, branch_id } = req.admin;
  let sql = "SELECT * FROM leads", params = [];
  if (role !== "hq") {                 // 지점: 자사만 (요청이 위조돼도 서버가 차단)
    if (!branch_id) return res.status(403).json({ ok: false, error: "소속 지점 없음" });
    sql += " WHERE branch_id=?"; params.push(branch_id);
  } else if (req.query.branch) {       // 본사: 선택 지점 필터(옵션)
    sql += " WHERE branch_id=?"; params.push(req.query.branch);
  }
  // const [rows] = await pool.query(sql + " ORDER BY created_at DESC", params);
  res.json({ ok: true, note: "stub", role, scope: role === "hq" ? "ALL" : branch_id, leads: [] });
});

// ── 관리자: 지점 콘텐츠 수정 (본사 또는 해당 지점만) ──
app.put("/api/admin/branches/:id", auth, async (req, res) => {
  const { role, branch_id } = req.admin;
  if (role !== "hq" && branch_id !== req.params.id)
    return res.status(403).json({ ok: false, error: "권한 없음(타 지점 편집 불가)" });
  res.json({ ok: true, note: "stub: 지점 content_json 갱신" });
});

// ── 관리자: 브랜드 공통요소 (본사 전용) ──
app.put("/api/admin/brand", auth, async (req, res) => {
  if (req.admin.role !== "hq") return res.status(403).json({ ok: false, error: "본사 전용" });
  res.json({ ok: true, note: "stub: brand_settings 갱신" });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log("resortpeople backend (stub) on :" + PORT));
