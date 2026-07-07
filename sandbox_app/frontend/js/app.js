const statusRow = document.querySelector(".status-row");
const statusText = document.querySelector("#api-status");

async function checkBackend() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const payload = await response.json();
    statusRow.dataset.state = "ok";
    statusText.textContent = `${payload.app} backend is running`;
  } catch (error) {
    statusRow.dataset.state = "error";
    statusText.textContent = "Backend health check failed";
  }
}

checkBackend();