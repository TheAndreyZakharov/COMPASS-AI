export async function requestJson(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Accept": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const message = `Request failed: ${response.status} ${response.statusText}`;
    throw new Error(message);
  }

  return response.json();
}

export function getHealth() {
  return requestJson("/api/health");
}

export function getStatus() {
  return requestJson("/api/status");
}

export function getConfig() {
  return requestJson("/api/config");
}

export function getSessions() {
  return requestJson("/api/sessions");
}