/**
 * LINKTICKET 관리자/직원 페이지 공통 API 헬퍼.
 *
 * 참조: 네이밍 컨벤션 규칙 v1.0 9.1절 — 모든 응답은
 *   성공 시 {"success": true, "data": ...}
 *   실패 시 {"success": false, "error_code": "...", "message": "..."}
 * 로 온다는 전제로 동작한다.
 *
 * 가정: WEB Zone(nginx)이 /api/ 로 들어오는 요청을 WAS Zone(Django+Gunicorn)으로
 * 리버스 프록시한다(DMZ WAF → WEB nginx → WAS Gunicorn). 이 페이지들을 nginx 문서
 * 루트가 아닌 다른 경로에서 서빙한다면 API_BASE만 바꾸면 된다.
 */
const API_BASE = "/api";

function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

async function apiRequest(method, path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    credentials: "include", // Django 세션 쿠키 동반
    headers: {
      ...(body instanceof FormData ? {} : {"Content-Type": "application/json"}),
      "X-CSRFToken": getCsrfToken(),
    },
    body: body !== undefined ? (body instanceof FormData ? body : JSON.stringify(body)) : undefined,
  });

  let payload = null;
  try {
    payload = await res.json();
  } catch (e) {
    // 204 No Content 등 본문 없는 응답
  }

  if (!res.ok || (payload && payload.success === false)) {
    const message = (payload && payload.message) || `요청에 실패했습니다 (HTTP ${res.status}).`;
    const error = new Error(message);
    error.errorCode = payload && payload.error_code;
    error.status = res.status;
    throw error;
  }
  return payload ? payload.data : null;
}

const api = {
  get: (path) => apiRequest("GET", path),
  post: (path, body) => apiRequest("POST", path, body),
  patch: (path, body) => apiRequest("PATCH", path, body),
  delete: (path) => apiRequest("DELETE", path),
};

/** 공통 토스트/에러 표시 헬퍼 (두 페이지에서 동일하게 사용) */
function showMessage(el, text, kind = "info") {
  el.textContent = text;
  el.dataset.kind = kind;
  el.hidden = false;
  window.clearTimeout(el._hideTimer);
  el._hideTimer = window.setTimeout(() => {
    el.hidden = true;
  }, 4000);
}

function formatNumber(n) {
  return new Intl.NumberFormat("ko-KR").format(n ?? 0);
}

function formatCurrency(n) {
  return `${formatNumber(n)}원`;
}
