const setText = (id, text, className = "") => {
  const element = document.getElementById(id);
  if (!element) return;
  element.textContent = text;
  element.className = className;
};

const getJson = async (url) => {
  const response = await fetch(url, {
    headers: { Accept: "application/json" },
    cache: "no-store",
  });

  const payload = await response.json();

  if (!response.ok) {
    throw new Error(payload?.error?.detail || `Request failed: ${response.status}`);
  }

  return payload;
};

const loadDashboard = async () => {
  try {
    const health = await getJson("/api/health");
    setText(
      "health-status",
      `${health.status.toUpperCase()} · ${health.app} ${health.version}`,
      "status-ok",
    );
  } catch (error) {
    setText("health-status", error.message, "status-bad");
  }

  try {
    const config = await getJson("/api/config");
    const schemaCount = Object.keys(config.feature_schemas || {}).length;
    const modelCount = Object.keys(config.model_presets?.models || {}).length;
    setText("config-status", `${schemaCount} feature schemas · ${modelCount} model presets`, "status-ok");
  } catch (error) {
    setText("config-status", error.message, "status-bad");
  }

  try {
    const sessions = await getJson("/api/sessions");
    setText(
      "sessions-status",
      `${sessions.counts.training_sessions} training · ${sessions.counts.assignment_sessions} assignment`,
      "status-ok",
    );
  } catch (error) {
    setText("sessions-status", error.message, "status-bad");
  }
};

window.addEventListener("DOMContentLoaded", loadDashboard);