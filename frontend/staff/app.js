/**
 * LINKTICKET 직원 페이지 로직.
 * 참조: 네이밍 컨벤션 규칙 v1.0 — 여기서 부르는 API 경로/응답 포맷은 그 문서와 스켈레톤이 정답이다.
 */
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));
const toast = $("#toast");

let currentUser = null; // {member_id, login_id, name, role, ...} — 로그인 성공 시 세팅

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
    onLoginSuccess();
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
  currentUser = null;
  $("#whoami").textContent = "로그인이 필요합니다";
  $("#login-bar").hidden = false;
  $("#logout-bar").hidden = true;
});

function onLoginSuccess() {
  $("#whoami").textContent = `${currentUser.name}님 (${currentUser.role})`;
  $("#login-bar").hidden = true;
  $("#logout-bar").hidden = false;
  if (currentUser.role !== "STAFF" && currentUser.role !== "ADMIN") {
    showMessage(toast, "STAFF/ADMIN 권한 계정이 아닙니다. 등록/삭제 요청이 403으로 거부될 수 있습니다.", "error");
  }
  loadPerformances();
  loadNotices();
}

/* ---------- 공연/회차/좌석 ---------- */
$("#performance-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const form = ev.target;
  const body = {
    performance_name: form.performance_name.value,
    genre: form.genre.value,
    venue_name: form.venue_name.value,
    address: form.address.value,
    base_price: Number(form.base_price.value),
    total_seats: Number(form.total_seats.value),
    description: form.description.value,
  };
  try {
    await api.post("/staff/performances/", body);
    showMessage(toast, "공연이 등록되었습니다.", "success");
    form.reset();
    loadPerformances();
  } catch (e) {
    showMessage(toast, e.message, "error");
  }
});

$("#schedule-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const form = ev.target;
  const performanceId = form.performance_id.value;
  if (!performanceId) return showMessage(toast, "공연을 먼저 선택하세요.", "error");
  const body = {
    performance_date: form.performance_date.value,
    start_time: form.start_time.value,
    end_time: form.end_time.value,
    sale_start_at: form.sale_start_at.value,
    sale_end_at: form.sale_end_at.value,
  };
  try {
    const schedule = await api.post(`/staff/performances/${performanceId}/schedules/`, body);
    showMessage(toast, `회차가 등록되었습니다 (회차 ID: ${schedule.schedule_id}).`, "success");
    form.reset();
  } catch (e) {
    showMessage(toast, e.message, "error");
  }
});

$("#seat-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const form = ev.target;
  const scheduleId = form.schedule_id.value;
  const grade = form.seat_grade.value;
  const price = Number(form.seat_price.value);
  const seatNumbers = form.seat_numbers.value
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  if (seatNumbers.length === 0) return showMessage(toast, "좌석 번호를 하나 이상 입력하세요.", "error");

  const seats = seatNumbers.map((seat_number) => ({
    seat_number,
    seat_grade: grade,
    seat_price: price,
  }));

  try {
    const created = await api.post(`/staff/schedules/${scheduleId}/seats/`, { seats });
    showMessage(toast, `좌석 ${created.length}석이 등록되었습니다.`, "success");
    form.reset();
  } catch (e) {
    showMessage(toast, e.message, "error");
  }
});

async function loadPerformances() {
  const listEl = $("#performance-list");
  const selectEl = $("#s-performance");
  try {
    const performances = await api.get("/performances/");
    if (!performances || performances.length === 0) {
      listEl.innerHTML = '<div class="empty-state">등록된 공연이 없습니다.</div>';
      selectEl.innerHTML = "";
      return;
    }
    listEl.innerHTML = `
      <table>
        <thead><tr><th>ID</th><th>공연명</th><th>장르</th><th>상태</th><th>공연장</th></tr></thead>
        <tbody>
          ${performances
            .map(
              (p) => `<tr>
                <td>${p.performance_id}</td>
                <td>${escapeHtml(p.performance_name)}</td>
                <td>${escapeHtml(p.genre)}</td>
                <td>${escapeHtml(p.performance_status)}</td>
                <td>${escapeHtml(p.venue_name)}</td>
              </tr>`
            )
            .join("")}
        </tbody>
      </table>`;
    selectEl.innerHTML = performances
      .map((p) => `<option value="${p.performance_id}">${escapeHtml(p.performance_name)} (#${p.performance_id})</option>`)
      .join("");
  } catch (e) {
    listEl.innerHTML = `<div class="empty-state">불러오지 못했습니다: ${escapeHtml(e.message)}</div>`;
  }
}

/* ---------- 공지사항 ---------- */
$("#notice-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const form = ev.target;
  const body = {
    notice_type: form.notice_type.value,
    title: form.title.value,
    content: form.content.value,
    is_published: form.is_published.checked,
  };
  try {
    await api.post("/staff/notices/", body);
    showMessage(toast, "공지가 등록되었습니다.", "success");
    form.reset();
    $("#n-published").checked = true;
    loadNotices();
  } catch (e) {
    showMessage(toast, e.message, "error");
  }
});

async function loadNotices() {
  const listEl = $("#notice-list");
  try {
    const notices = await api.get("/staff/notices/");
    if (!notices || notices.length === 0) {
      listEl.innerHTML = '<div class="empty-state">등록된 공지가 없습니다.</div>';
      return;
    }
    listEl.innerHTML = `
      <table>
        <thead><tr><th>ID</th><th>유형</th><th>제목</th><th>공개 여부</th><th>조회수</th><th></th></tr></thead>
        <tbody>
          ${notices
            .map(
              (n) => `<tr>
                <td>${n.notice_id}</td>
                <td>${escapeHtml(n.notice_type)}</td>
                <td>${escapeHtml(n.title)}</td>
                <td>${n.is_published ? "공개" : "비공개"}</td>
                <td>${formatNumber(n.view_count)}</td>
                <td><button class="danger" data-delete-notice="${n.notice_id}">삭제</button></td>
              </tr>`
            )
            .join("")}
        </tbody>
      </table>`;
    $$("[data-delete-notice]").forEach((btn) => {
      btn.addEventListener("click", () => deleteNotice(btn.dataset.deleteNotice));
    });
  } catch (e) {
    listEl.innerHTML = `<div class="empty-state">불러오지 못했습니다: ${escapeHtml(e.message)}</div>`;
  }
}

async function deleteNotice(noticeId) {
  if (!window.confirm(`공지 #${noticeId}를 삭제할까요?`)) return;
  try {
    await api.delete(`/staff/notices/${noticeId}/`);
    showMessage(toast, "공지가 삭제되었습니다.", "success");
    loadNotices();
  } catch (e) {
    showMessage(toast, e.message, "error");
  }
}

/* ---------- 검표 ---------- */
$("#verify-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const form = ev.target;
  const resultEl = $("#verify-result");
  try {
    const ticket = await api.post("/staff/tickets/verify/", { qr_token: form.qr_token.value });
    resultEl.innerHTML = `<p style="color:var(--status-good)">입장 처리 완료 — 티켓 #${ticket.ticket_id} (${escapeHtml(
      ticket.ticket_status
    )})</p>`;
    form.reset();
  } catch (e) {
    resultEl.innerHTML = `<p style="color:var(--status-critical)">${escapeHtml(e.errorCode || "")} ${escapeHtml(
      e.message
    )}</p>`;
  }
});

function escapeHtml(str) {
  return String(str ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
