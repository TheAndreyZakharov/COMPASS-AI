import * as dashboard from "./pages/dashboard.js";
import * as generator from "./pages/generator.js";
import * as viewer from "./pages/viewer.js";
import * as training from "./pages/training.js";
import * as models from "./pages/models.js";
import * as assignmentLab from "./pages/assignment_lab.js";
import * as reports from "./pages/reports.js";
import * as settings from "./pages/settings.js";
import { getHealth } from "./api.js";

const routes = {
  dashboard,
  generator,
  viewer,
  training,
  models,
  "assignment-lab": assignmentLab,
  reports,
  settings,
};

const appRoot = document.querySelector("#app");
const pageTitle = document.querySelector("#page-title");
const refreshButton = document.querySelector("#refresh-button");
const backendDot = document.querySelector("#backend-dot");
const backendStatus = document.querySelector("#backend-status");

function currentRoute() {
  const route = window.location.hash.replace("#", "");
  return routes[route] ? route : "dashboard";
}

function setActiveNav(route) {
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.classList.toggle("active", link.dataset.route === route);
  });
}

async function checkBackend() {
  try {
    const payload = await getHealth();
    backendDot.className = "status-dot ok";
    backendStatus.textContent = `${payload.status}`;
  } catch (error) {
    backendDot.className = "status-dot error";
    backendStatus.textContent = "offline";
  }
}

async function renderRoute() {
  const route = currentRoute();
  const page = routes[route];

  setActiveNav(route);
  pageTitle.textContent = page.title;
  appRoot.innerHTML = `<div class="loading-state">Loading ${page.title}...</div>`;

  try {
    await page.render(appRoot);
  } catch (error) {
    appRoot.innerHTML = `
      <div class="error-state">
        <strong>Failed to render ${page.title}</strong>
        <p>${error.message}</p>
      </div>
    `;
  }

  await checkBackend();
}

window.addEventListener("hashchange", renderRoute);

refreshButton.addEventListener("click", () => {
  renderRoute();
});

if (!window.location.hash) {
  window.location.hash = "#dashboard";
} else {
  renderRoute();
}