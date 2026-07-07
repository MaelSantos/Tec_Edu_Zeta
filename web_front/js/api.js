const API_BASE = "http://localhost:8001/api";
const API_URL_CHAT = API_BASE + "/chat";
const API_URL_ALUNO = API_BASE + "/alunos";

async function apiPost(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    let detail = `Erro ${response.status}`;
    try {
      const err = await response.json();
      detail = err.detail || JSON.stringify(err);
    } catch (_) {
      detail = await response.text().catch(() => detail);
    }
    throw new Error(detail);
  }
  return response;
}

async function apiGet(url) {
  const response = await fetch(url);
  if (!response.ok) {
    if (response.status === 404) return null;
    let detail = `Erro ${response.status}`;
    try {
      const err = await response.json();
      detail = err.detail || JSON.stringify(err);
    } catch (_) {
      detail = await response.text().catch(() => detail);
    }
    throw new Error(detail);
  }
  return response.json();
}
