const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export class ApiError extends Error {
  constructor(message, status, detail) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

async function parseError(response) {
  let detail = null;
  let rawText = '';
  try {
    rawText = await response.text();
    detail = JSON.parse(rawText);
  } catch {
    detail = rawText || null;
  }

  const message =
    (detail && typeof detail === 'object' && detail.detail) ||
    (typeof detail === 'string' && detail) ||
    `Request failed with status ${response.status}`;

  return new ApiError(message, response.status, detail);
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...options.headers,
      },
      ...options,
    });
  } catch (err) {
    throw new ApiError(
      'Unable to reach the TutorTrace backend. Check your connection or that the server is running.',
      0,
      null
    );
  }

  if (!response.ok) {
    throw await parseError(response);
  }

  return response.json();
}

export function startStudent(studentId) {
  return request(`/students/${encodeURIComponent(studentId)}/start`, {
    method: 'POST',
  });
}

export function getNextQuestion(studentId) {
  return request(`/students/${encodeURIComponent(studentId)}/next-question`);
}

export function submitAnswer(studentId, payload) {
  return request(`/students/${encodeURIComponent(studentId)}/submit-answer`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getMastery(studentId) {
  return request(`/students/${encodeURIComponent(studentId)}/mastery`);
}

export function getDiagnostics(studentId) {
  return request(`/students/${encodeURIComponent(studentId)}/diagnostics`);
}

export function getTeacherClassroom() {
  return request('/teacher/classroom');
}

export function getTeacherAlerts() {
  return request('/teacher/alerts');
}
