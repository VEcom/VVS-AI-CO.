/*
 * app.js — 리조트피플 모바일 리플렛 렌더링 + 리드 수집 + 링크공유 + UTM
 *
 * 프로토타입: 리드는 localStorage 에 저장(서버 연동 자리는 submitLead() 참고).
 * 실서비스: submitLead() 가 POST /api/leads 로 전송, 지점은 ?branch=ID 로 라우팅.
 */
(function () {
  "use strict";
  var D = window.RP_DATA;

  // ── UTM 캡처 (butfit 레퍼런스와 동일 전략) ──
  (function captureUTM() {
    var s = location.search;
    if (s && s.indexOf("utm_") !== -1) {
      var p = new URLSearchParams(s), u = {};
      ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"].forEach(function (k) {
        var v = p.get(k); if (v) u[k] = v;
      });
      if (Object.keys(u).length) { u._t = Date.now(); try { localStorage.setItem("rp_utm", JSON.stringify(u)); } catch (e) {} }
    }
  })();

  function getUTM() { try { return JSON.parse(localStorage.getItem("rp_utm") || "{}"); } catch (e) { return {}; } }

  // ── 지점 선택 (?branch=ID, 없으면 첫 지점) ──
  function currentBranch() {
    var id = new URLSearchParams(location.search).get("branch");
    return D.branches.find(function (b) { return b.id === id; }) || D.branches[0];
  }

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function render() {
    var b = currentBranch();
    document.title = D.brand.name + " " + b.name + " — " + b.headline;
    var live = b.status === "운영중";
    var pct = Math.min(100, Math.round((b.milestone.current / b.milestone.target) * 100));

    var app = document.getElementById("app");
    app.innerHTML = [
      // 상단 바 + 지점 선택
      '<header class="topbar">',
      '  <div class="logo"><b>RESORT</b> PEOPLE</div>',
      '  <select class="branch-pick" id="branchPick" aria-label="지점 선택">',
      D.branches.map(function (x) {
        return '<option value="' + x.id + '"' + (x.id === b.id ? " selected" : "") + ">" + esc(x.name) + "</option>";
      }).join(""),
      '  </select>',
      "</header>",

      // 히어로
      '<div class="hero" style="background:' + b.hero + '">',
      '  <span class="badge ' + (live ? "live" : "") + '">' + (live ? "🟢 운영중" : "⏳ " + esc(b.status)) + "</span>",
      "  <h1>" + esc(b.headline) + "</h1>",
      '  <div class="sig">' + esc(b.signature) + "</div>",
      '  <div class="open">' + (live ? "📍 " + esc(b.area) : "🗓️ <b>" + esc(b.openDate) + "</b> 오픈 예정 · " + esc(b.area)) + "</div>",
      "</div>",

      // 마일스톤
      '<div class="milestone">',
      '  <div class="ml-label">🔥 ' + esc(b.milestone.label) + "</div>",
      '  <div class="bar"><i style="width:' + pct + '%"></i></div>',
      '  <div class="ml-num"><b>' + b.milestone.current + "명</b> / " + b.milestone.target + "명 달성 (" + pct + "%)</div>",
      "</div>",

      // 브랜드 소개
      sec("브랜드 소개", '<p class="lead-txt">' + esc(D.brand.intro) + "</p>"),

      // 콘텐츠
      sec("콘텐츠 · 프로그램",
        '<div class="cards">' + D.brand.contents.map(function (c) {
          return '<div class="card"><div class="ic">' + c.icon + "</div><h3>" + esc(c.title) + "</h3><p>" + esc(c.desc) + "</p></div>";
        }).join("") + "</div>"),

      // 지점 소개
      sec(b.name + " 안내",
        '<div class="branch-box">' +
        row("시그니처", b.signature) + row("주소", b.address) + row("교통", b.area) +
        row("오픈", live ? "운영중" : b.openDate) + "</div>"),

      // 트레이너
      sec("강사 · 트레이너",
        '<div class="trainers">' + b.trainers.map(function (t) {
          return '<div class="tr"><div class="ava">' + t.img + '</div><div class="nm">' + esc(t.name) +
            '</div><div class="ro">' + esc(t.role) + '</div><div class="tg">' + esc(t.tag) + "</div></div>";
        }).join("") + "</div>"),

      // 시간표
      sec("주간 시간표",
        '<table class="tt"><thead><tr><th>시간</th><th>월</th><th>수</th><th>금</th></tr></thead><tbody>' +
        b.schedule.map(function (r) {
          return "<tr><td class='tm'>" + esc(r.time) + "</td><td>" + esc(r.mon || "-") + "</td><td>" + esc(r.wed || "-") + "</td><td>" + esc(r.fri || "-") + "</td></tr>";
        }).join("") + "</tbody></table>"),

      // 월간 이벤트
      sec("이번 달 이벤트",
        '<div class="event"><span class="tag">' + esc(b.event.title) + "</span><h3>" + esc(b.event.desc) +
        '</h3><div class="until">⏰ ' + esc(b.event.until) + " 까지</div></div>"),

      // 인센티브
      sec("사전등록 혜택",
        '<div class="incentive"><div class="gift">🎁</div><h3>' + esc(D.brand.incentive.headline) +
        '</h3><div class="rw">' + esc(D.brand.incentive.reward) + '</div><div class="cond">' +
        esc(D.brand.incentive.condition) + "<br>👥 " + esc(D.brand.incentive.referral) + "</div></div>"),

      // 리드 폼
      leadFormHTML(b),

      // 푸터
      '<footer><div class="fb">' + D.brand.name + " " + esc(b.name) + "</div>" +
      esc(b.address) + "<br>© 2026 RESORT PEOPLE. 본 페이지는 프로토타입입니다.</footer>",

      // 플로팅 CTA
      '<div class="cta-bar">',
      '  <button class="btn btn-primary" id="ctaReserve">' + (live ? "상담 신청하기" : "사전예약 신청") + "</button>",
      '  <button class="btn btn-share" id="ctaShare">🔗 공유</button>',
      "</div>",
      '<div class="toast" id="toast"></div>',
    ].join("");

    bind(b);
  }

  function sec(title, inner) {
    return '<section><div class="sec-h"><span class="bar6"></span><h2>' + esc(title) + "</h2></div>" + inner + "</section>";
  }
  function row(k, v) { return '<div class="row"><span class="k">' + esc(k) + '</span><span class="v">' + esc(v) + "</span></div>"; }

  function leadFormHTML(b) {
    var prog = D.brand.contents.map(function (c) { return '<option>' + esc(c.title) + "</option>"; }).join("");
    return [
      '<section class="lead" id="leadSec">',
      '  <div class="sec-h"><span class="bar6"></span><h2>' + (b.status === "운영중" ? "상담 신청" : "사전예약 신청") + "</h2></div>",
      '  <div id="leadBody">',
      '    <div class="field"><label>이름</label><input id="f_name" placeholder="이름을 입력해주세요"></div>',
      '    <div class="field"><label>연락처</label><input id="f_phone" type="tel" inputmode="numeric" placeholder="010-0000-0000"></div>',
      '    <div class="field"><label>관심 프로그램</label><select id="f_prog">' + prog + "</select></div>",
      '    <div class="field"><label>유입 경로</label><select id="f_src"><option>인스타그램</option><option>지인 추천</option><option>전단·리플렛</option><option>네이버 검색</option><option>지나가다</option><option>기타</option></select></div>',
      '    <label class="consent"><input type="checkbox" id="f_agree"><span>개인정보 수집 및 이용에 동의합니다. <a href="#" id="privacyLink">[보기]</a></span></label>',
      '    <label class="consent"><input type="checkbox" id="f_mkt"><span>마케팅 정보 수신(오픈·이벤트 알림)에 동의합니다. (선택)</span></label>',
      '    <div class="privacy-note">· 수집 목적 : ' + esc(D.brand.privacy.purpose) + "<br>· " + esc(D.brand.privacy.retention) + "</div>",
      '    <button class="btn btn-primary" id="submitLead">' + (b.status === "운영중" ? "상담 신청 완료하기" : "사전예약하고 혜택받기") + "</button>",
      '    <div class="share-row"><button class="btn btn-share" id="shareLink">🔗 친구에게 링크 보내기</button></div>',
      "  </div>",
      "</section>",
    ].join("");
  }

  // ── 이벤트 바인딩 ──
  function bind(b) {
    document.getElementById("branchPick").addEventListener("change", function (e) {
      var p = new URLSearchParams(location.search); p.set("branch", e.target.value);
      location.search = p.toString();
    });
    document.getElementById("ctaReserve").addEventListener("click", scrollToLead);
    document.getElementById("ctaShare").addEventListener("click", function () { shareLink(b); });
    document.getElementById("shareLink").addEventListener("click", function () { shareLink(b); });
    document.getElementById("privacyLink").addEventListener("click", function (e) {
      e.preventDefault();
      alert("[개인정보 수집·이용 동의]\n\n· 수집 항목 : 이름, 연락처, 관심 프로그램\n· 수집 목적 : " +
        D.brand.privacy.purpose + "\n· " + D.brand.privacy.retention + "\n· 동의 거부 시 사전예약/상담 신청이 제한됩니다.");
    });
    document.getElementById("submitLead").addEventListener("click", function () { submitLead(b); });
  }

  function scrollToLead() { document.getElementById("leadSec").scrollIntoView({ behavior: "smooth" }); }

  function toast(msg) {
    var t = document.getElementById("toast"); t.textContent = msg; t.classList.add("on");
    clearTimeout(toast._t); toast._t = setTimeout(function () { t.classList.remove("on"); }, 2000);
  }

  function shareLink(b) {
    var url = location.origin + location.pathname + "?branch=" + b.id;
    var data = { title: D.brand.name + " " + b.name, text: b.headline, url: url };
    if (navigator.share) { navigator.share(data).catch(function () {}); }
    else if (navigator.clipboard) { navigator.clipboard.writeText(url).then(function () { toast("링크를 복사했습니다!"); }); }
    else { prompt("아래 링크를 복사해 공유하세요", url); }
  }

  function submitLead(b) {
    var name = val("f_name"), phone = val("f_phone");
    if (!name) return toast("이름을 입력해주세요");
    if (!/^01[0-9][- ]?\d{3,4}[- ]?\d{4}$/.test(phone.replace(/\s/g, ""))) return toast("연락처를 정확히 입력해주세요");
    if (!document.getElementById("f_agree").checked) return toast("개인정보 수집에 동의해주세요");

    var lead = {
      branch_id: b.id, branch_name: b.name, name: name, phone: phone,
      program: val("f_prog"), source: val("f_src"),
      marketing_agree: document.getElementById("f_mkt").checked,
      utm: getUTM(), created_at: new Date().toISOString(),
    };

    // ── 프로토타입: localStorage 저장. 실서비스에서는 아래 fetch 로 대체 ──
    // fetch("/api/leads", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(lead)})
    var leads = JSON.parse(localStorage.getItem("rp_leads") || "[]");
    leads.push(lead); localStorage.setItem("rp_leads", JSON.stringify(leads));

    document.getElementById("leadBody").innerHTML =
      '<div class="done"><div class="chk">✅</div><h3>' + esc(name) + "님, 신청 완료!</h3>" +
      "<p>" + esc(b.name) + " 오픈/상담 안내를 보내드릴게요.<br>" + esc(D.brand.incentive.reward) +
      " 지급 대상입니다 🎁</p>" +
      '<div class="share-row" style="margin-top:18px"><button class="btn btn-share" id="shareDone">🔗 친구 초대하고 추가 혜택받기</button></div></div>';
    document.getElementById("shareDone").addEventListener("click", function () { shareLink(b); });
    scrollToLead();
  }

  function val(id) { return (document.getElementById(id).value || "").trim(); }

  document.addEventListener("DOMContentLoaded", render);
})();
