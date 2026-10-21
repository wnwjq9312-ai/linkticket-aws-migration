/**
 * LINKTICKET 관리자 페이지 로직.
 * 참조: 네이밍 컨벤션 규칙 v1.0 — 여기서 부르는 API 경로/응답 포맷은 그 문서와 스켈레톤이 정답이다.
 */
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));
const toast = $("#toast");

let currentUser = null;

/* ---------- 탭 전환 ---------- */
$$(".tab-button").forEach((btn) => {
  btn.addEventListener("click", () => {
    $$(".tab-button").forEach((b) => b.classList.remove("active"));
    $$(".panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    $(`#panel-${btn.dataset.tab}`).classList.add("active");
  });
});

/* ---------- 로그인/로그아웃 ---------- */
$("#login-btn").addEventListener("click", async () => {
  const login_id = $("#login-id").value.trim();
  const password = $("#login-password").value;
  if (!login_id || !password) return showMessage(toast, "아이디와 비밀번호를 입력하세요.", "error");
  try {
    currentUser = await api.post("/auth/login/", { login_id, password });
    window.location.reload();
  } catch (e) {
    showMessage(toast, e.message, "error");
  }
});

$("#logout-btn").addEventListener("click", async () => {
  try {
    await api.post("/auth/logout/");
  } catch (e) {
    /* 세션이 이미 끊겼어도 화면은 로그아웃 상태로 되돌린다 */
  }
  window.location.reload();
  currentUser = null;
  $("#whoami").textContent = "로그인이 필요합니다";
  $("#login-bar").hidden = false;
  $("#logout-bar").hidden = true;
});

function onLoginSuccess() {
  $("#whoami").textContent = `${currentUser.name}님 (${currentUser.role})`;
  $("#login-bar").hidden = true;
  $("#logout-bar").hidden = false;
  if (currentUser.role !== "ADMIN") {
    showMessage(toast, "ADMIN 권한 계정이 아닙니다. 대부분의 요청이 403으로 거부됩니다.", "error");
  }
  loadOverview();
  loadPerformanceOptions();
  loadStaffList();
  loadMemberList();
  loadReservations();
}

/* ---------- 대시보드 ---------- */
async function loadOverview() {
  try {
    const summary = await api.get("/admin/dashboard/overview/");
    $("#kpi-performances").textContent = formatNumber(summary.published_performances);
    $("#kpi-today-reservations").textContent = formatNumber(summary.today_confirmed_reservations);
    $("#kpi-unsold-seats").textContent = formatNumber(summary.total_unsold_seats);
    $("#kpi-revenue").textContent = formatCurrency(summary.total_revenue);
  } catch (e) {
    showMessage(toast, `대시보드 요약을 불러오지 못했습니다: ${e.message}`, "error");
  }
}

async function loadPerformanceOptions() {
  const selectEl = $("#d-performance");
  try {
    const performances = await api.get("/performances/");
    selectEl.innerHTML = (performances || [])
      .map((p) => `<option value="${p.performance_id}">${escapeHtml(p.performance_name)} (#${p.performance_id})</option>`)
      .join("");
  } catch (e) {
    selectEl.innerHTML = "";
  }
}

$("#dashboard-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const performanceId = $("#d-performance").value;
  if (!performanceId) return;
  const summaryEl = $("#performance-summary");
  const tableEl = $("#schedule-table");
  try {
    const dash = await api.get(`/admin/dashboard/performances/${performanceId}/`);
    const counts = [dash.total_reserved, dash.total_available, Math.max(0,dash.total_seats-dash.total_reserved-dash.total_available)];
    const total = dash.total_seats || 1;
    document.querySelectorAll('#ops-chart>div').forEach((bar,index)=>{bar.style.height=Math.max(2,counts[index]/total*100)+'%';bar.querySelector('span').textContent=formatNumber(counts[index]);});
    const percent=Math.round(dash.total_reserved/total*100);
    document.getElementById('ops-donut').style.background=`conic-gradient(#8150ff 0 ${percent}%,#e4edff ${percent}% 100%)`;
    document.querySelector('#ops-donut strong').textContent=percent+'%';
    summaryEl.innerHTML = `
      <div class="kpi-row">
        <div class="stat-tile"><div class="label">전체 좌석</div><div class="value">${formatNumber(dash.total_seats)}</div></div>
        <div class="stat-tile"><div class="label">판매완료 좌석</div><div class="value">${formatNumber(dash.total_reserved)}</div></div>
        <div class="stat-tile"><div class="label">미판매 좌석</div><div class="value">${formatNumber(dash.total_available)}</div></div>
        <div class="stat-tile"><div class="label">누적 매출</div><div class="value">${formatCurrency(dash.revenue)}</div></div>
      </div>`;

    if (!dash.schedules || dash.schedules.length === 0) {
      tableEl.innerHTML = '<div class="empty-state">등록된 회차가 없습니다.</div>';
      return;
    }

    tableEl.innerHTML = `
      <table>
        <thead>
          <tr><th>회차</th><th>판매 상태</th><th>좌석 현황</th><th>예매 인원</th><th>확정 예약 건수</th></tr>
        </thead>
        <tbody>
          ${dash.schedules.map(renderScheduleRow).join("")}
        </tbody>
      </table>`;
  } catch (e) {
    tableEl.innerHTML = `<div class="empty-state">불러오지 못했습니다: ${escapeHtml(e.message)}</div>`;
  }
});

function renderScheduleRow(s) {
  const stats = s.seat_stats || {};
  const total = stats.total || 1;
  const reserved = stats.RESERVED || 0;
  const available = stats.AVAILABLE || 0;
  const blocked = stats.BLOCKED || 0;

  const seg = (count, color, isLast) =>
    count > 0
      ? `<span style="width:${(count / total) * 100}%; background:${color}; ${isLast ? "" : "margin-right:2px;"}"></span>`
      : "";

  const bar = `<div class="seat-bar">
      ${seg(reserved, "var(--series-sold)", available === 0 && blocked === 0)}
      ${seg(available, "var(--series-unsold)", blocked === 0)}
      ${seg(blocked, "var(--series-blocked)", true)}
    </div>
    <div class="muted">판매 ${formatNumber(reserved)} · 미판매 ${formatNumber(available)} · 판매불가 ${formatNumber(blocked)}</div>`;

  return `<tr>
      <td>${s.performance_date} ${s.start_time}<div class="muted">#${s.schedule_id}</div></td>
      <td>${escapeHtml(s.sale_status)}</td>
      <td>${bar}</td>
      <td>${formatNumber(s.reserving_members)}</td>
      <td>${formatNumber(s.confirmed_reservations)}</td>
    </tr>`;
}

/* ---------- 직원 관리 ---------- */
$("#staff-create-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const form = ev.target;
  const body = {
    login_id: form.login_id.value,
    name: form.name.value,
    phone: form.phone.value,
    email: form.email.value,
    password: form.password.value,
  };
  try {
    await api.post("/admin/staff/", body);
    showMessage(toast, "직원 계정이 발급되었습니다.", "success");
    form.reset();
    loadStaffList();
  } catch (e) {
    showMessage(toast, e.message, "error");
  }
});

async function loadStaffList() {
  const listEl = $("#staff-list");
  try {
    const staff = await api.get("/admin/staff/");
    if (!staff || staff.length === 0) {
      listEl.innerHTML = '<div class="empty-state">등록된 직원이 없습니다.</div>';
      return;
    }
    listEl.innerHTML = `
      <table>
        <thead><tr><th>ID</th><th>아이디</th><th>이름</th><th>이메일</th><th>상태</th><th></th></tr></thead>
        <tbody>
          ${staff
            .map(
              (m) => `<tr>
                <td>${m.member_id}</td>
                <td>${escapeHtml(m.login_id)}</td>
                <td>${escapeHtml(m.name)}</td>
                <td>${escapeHtml(m.email)}</td>
                <td>${escapeHtml(m.member_status)}</td>
                <td>
                  <button class="secondary" data-suspend-member="${m.member_id}"
                    data-next-status="${m.member_status === "SUSPENDED" ? "ACTIVE" : "SUSPENDED"}">
                    ${m.member_status === "SUSPENDED" ? "정지 해제" : "정지"}
                  </button>
                </td>
              </tr>`
            )
            .join("")}
        </tbody>
      </table>`;
    bindMemberStatusButtons(listEl, loadStaffList);
  } catch (e) {
    listEl.innerHTML = `<div class="empty-state">불러오지 못했습니다: ${escapeHtml(e.message)}</div>`;
  }
}

/* ---------- 회원 관리 ---------- */
async function loadMemberList() {
  const listEl = $("#member-list");
  try {
    const members = await api.get("/admin/members/");
    if (!members || members.length === 0) {
      listEl.innerHTML = '<div class="empty-state">회원이 없습니다.</div>';
      return;
    }
    listEl.innerHTML = `
      <table>
        <thead><tr><th>ID</th><th>아이디</th><th>이름</th><th>역할</th><th>상태</th><th></th></tr></thead>
        <tbody>
          ${members
            .map(
              (m) => `<tr>
                <td>${m.member_id}</td>
                <td>${escapeHtml(m.login_id)}</td>
                <td>${escapeHtml(m.name)}</td>
                <td>${escapeHtml(m.role)}</td>
                <td>${escapeHtml(m.member_status)}</td>
                <td>
                  <button class="secondary" data-suspend-member="${m.member_id}"
                    data-next-status="${m.member_status === "SUSPENDED" ? "ACTIVE" : "SUSPENDED"}">
                    ${m.member_status === "SUSPENDED" ? "정지 해제" : "정지"}
                  </button>
                </td>
              </tr>`
            )
            .join("")}
        </tbody>
      </table>`;
    bindMemberStatusButtons(listEl, loadMemberList);
  } catch (e) {
    listEl.innerHTML = `<div class="empty-state">불러오지 못했습니다: ${escapeHtml(e.message)}</div>`;
  }
}

function bindMemberStatusButtons(container, reload) {
  Array.from(container.querySelectorAll("[data-suspend-member]")).forEach((btn) => {
    btn.addEventListener("click", async () => {
      const memberId = btn.dataset.suspendMember;
      const nextStatus = btn.dataset.nextStatus;
      try {
        await api.patch(`/admin/members/${memberId}/status/`, { member_status: nextStatus });
        showMessage(toast, `회원 #${memberId} 상태가 ${nextStatus}로 변경되었습니다.`, "success");
        reload();
      } catch (e) {
        showMessage(toast, e.message, "error");
      }
    });
  });
}

/* ---------- 예약 현황 ---------- */
$("#reservation-filter-form").addEventListener("submit", (ev) => {
  ev.preventDefault();
  loadReservations();
});

async function loadReservations() {
  const listEl = $("#reservation-list");
  const status = $("#r-status").value;
  try {
    const path = status ? `/admin/reservations/?status=${encodeURIComponent(status)}` : "/admin/reservations/";
    const reservations = await api.get(path);
    if (!reservations || reservations.length === 0) {
      listEl.innerHTML = '<div class="empty-state">예약 내역이 없습니다.</div>';
      return;
    }
    listEl.innerHTML = `
      <table>
        <thead><tr><th>예약번호</th><th>회원 ID</th><th>회차 ID</th><th>금액</th><th>상태</th></tr></thead>
        <tbody>
          ${reservations
            .map(
              (r) => `<tr>
                <td>${escapeHtml(r.reservation_code)}</td>
                <td>${r.member}</td>
                <td>${r.schedule}</td>
                <td>${formatCurrency(r.total_amount)}</td>
                <td>${escapeHtml(r.reservation_status)}</td>
              </tr>`
            )
            .join("")}
        </tbody>
      </table>`;
  } catch (e) {
    listEl.innerHTML = `<div class="empty-state">불러오지 못했습니다: ${escapeHtml(e.message)}</div>`;
  }
}

/* ---------- 티켓 관리 ---------- */
$("#ticket-block-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const ticketId = $("#t-ticket-id").value;
  const resultEl = $("#ticket-block-result");
  try {
    const ticket = await api.patch(`/admin/tickets/${ticketId}/block/`);
    resultEl.innerHTML = `<p style="color:var(--status-good)">티켓 #${ticket.ticket_id}이 차단되었습니다 (${escapeHtml(
      ticket.ticket_status
    )}).</p>`;
  } catch (e) {
    resultEl.innerHTML = `<p style="color:var(--status-critical)">${escapeHtml(e.errorCode || "")} ${escapeHtml(
      e.message
    )}</p>`;
  }
});

function escapeHtml(str) {
  return String(str ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

api.get('/auth/me/').then(user => { currentUser = user; onLoginSuccess(); }).catch(() => {});
