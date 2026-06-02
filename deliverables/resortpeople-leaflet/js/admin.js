/*
 * admin.js — 관리자 권한 2단계 컨셉 데모
 *
 *  본사(hq)  : 전 지점 리드 조회 + 콘텐츠 편집(데모 버튼) + CSV
 *  지점(branch): 자사 지점 리드 "조회만" — 편집 버튼 숨김, 지점 선택 고정
 *
 * 데이터 출처: index.html 에서 localStorage("rp_leads") 에 쌓인 리드.
 * 실서비스: GET /api/admin/leads (세션 권한에 따라 서버가 필터링·권한제어)
 */
(function () {
  "use strict";
  var D = window.RP_DATA;
  var roleSel = document.getElementById("roleSel");
  var branchSel = document.getElementById("branchSel");

  // 지점 셀렉트 채우기
  branchSel.innerHTML = '<option value="ALL">전체 지점</option>' +
    D.branches.map(function (b) { return '<option value="' + b.id + '">' + b.name + "</option>"; }).join("");

  function leads() { try { return JSON.parse(localStorage.getItem("rp_leads") || "[]"); } catch (e) { return []; } }

  function applyRole() {
    var hq = roleSel.value === "hq";
    document.getElementById("roleLabel").textContent = "권한: " + (hq ? "본사(HQ)" : "지점(BRANCH)");
    document.getElementById("permNote").innerHTML = hq
      ? "🔑 <b>본사 권한</b> — 브랜드 공통요소·전 지점 콘텐츠 편집 및 모든 지점 리드 열람이 가능합니다."
      : "🔒 <b>지점 권한</b> — 자사 지점 리드 <b>조회만</b> 가능합니다. 콘텐츠 편집/타 지점 열람은 차단됩니다.";
    // 지점 권한이면: 편집 버튼 숨김 + 지점 고정(전체 선택 불가)
    document.querySelectorAll(".hq-only").forEach(function (el) { el.style.display = hq ? "" : "none"; });
    var allOpt = branchSel.querySelector('option[value="ALL"]');
    if (!hq) {
      allOpt.disabled = true;
      if (branchSel.value === "ALL") branchSel.value = D.branches[0].id;
    } else {
      allOpt.disabled = false;
    }
    branchSel.disabled = false; // 데모에서는 지점 전환 허용(실서비스는 세션에 고정)
    draw();
  }

  function filtered() {
    var hq = roleSel.value === "hq", sel = branchSel.value;
    return leads().filter(function (l) {
      if (!hq && sel === "ALL") return false;
      return sel === "ALL" ? true : l.branch_id === sel;
    });
  }

  function draw() {
    var rows = filtered();
    // 통계
    var stats = document.getElementById("stats");
    var mkt = rows.filter(function (r) { return r.marketing_agree; }).length;
    var bySrc = {};
    rows.forEach(function (r) { bySrc[r.source] = (bySrc[r.source] || 0) + 1; });
    var topSrc = Object.keys(bySrc).sort(function (a, b) { return bySrc[b] - bySrc[a]; })[0] || "-";
    stats.innerHTML =
      stat(rows.length, "총 리드") +
      stat(mkt, "마케팅 동의") +
      stat(roleSel.value === "hq" && branchSel.value === "ALL" ? new Set(rows.map(function (r) { return r.branch_id; })).size : 1, "지점 수") +
      stat(topSrc, "최다 유입경로");

    var thead = document.querySelector("#leadTable thead");
    var tbody = document.querySelector("#leadTable tbody");
    var empty = document.getElementById("empty");
    if (!rows.length) { thead.innerHTML = ""; tbody.innerHTML = ""; empty.style.display = "block"; return; }
    empty.style.display = "none";
    thead.innerHTML = "<tr><th>일시</th><th>지점</th><th>이름</th><th>연락처</th><th>관심</th><th>유입</th><th>마케팅</th><th>UTM</th></tr>";
    tbody.innerHTML = rows.slice().reverse().map(function (l) {
      var utm = l.utm && l.utm.utm_source ? l.utm.utm_source + "/" + (l.utm.utm_medium || "") : "-";
      return "<tr><td>" + fmt(l.created_at) + "</td><td>" + l.branch_name + "</td><td>" + l.name +
        "</td><td>" + maskPhone(l.phone) + "</td><td>" + (l.program || "-") + "</td><td>" + (l.source || "-") +
        "</td><td>" + (l.marketing_agree ? "✅" : "—") + "</td><td>" + utm + "</td></tr>";
    }).join("");
  }

  function stat(n, l) { return '<div class="stat"><div class="n">' + n + '</div><div class="l">' + l + "</div></div>"; }
  function fmt(iso) { var d = new Date(iso); return d.toLocaleString("ko-KR", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" }); }
  function maskPhone(p) { return String(p).replace(/(\d{3})[- ]?(\d{3,4})[- ]?(\d{4})/, "$1-****-$3"); }

  function exportCSV() {
    var rows = filtered();
    if (!rows.length) return alert("내보낼 리드가 없습니다.");
    var head = ["created_at", "branch_name", "name", "phone", "program", "source", "marketing_agree"];
    var csv = head.join(",") + "\n" + rows.map(function (l) {
      return head.map(function (k) { return '"' + String(l[k] == null ? "" : l[k]).replace(/"/g, '""') + '"'; }).join(",");
    }).join("\n");
    var blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8;" });
    var a = document.createElement("a"); a.href = URL.createObjectURL(blob);
    a.download = "resortpeople_leads_" + (branchSel.value) + ".csv"; a.click();
  }

  roleSel.addEventListener("change", applyRole);
  branchSel.addEventListener("change", draw);
  document.getElementById("refresh").addEventListener("click", draw);
  document.getElementById("exportBtn").addEventListener("click", exportCSV);
  document.getElementById("editBtn").addEventListener("click", function () {
    alert("[본사 전용] 콘텐츠 편집\n\n실서비스에서는 브랜드 공통요소(소개·콘텐츠·디자인)와\n각 지점의 트레이너·시간표·이벤트를 폼으로 직접 수정합니다.\n(텍스트·이미지 교체는 추가비용 없이 관리자에서 상시 가능)");
  });

  applyRole();
})();
