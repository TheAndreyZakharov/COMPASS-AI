import { api } from "./api.js";
import { renderAssignmentLab } from "./pages/assignment_lab.js";
import { renderDashboard } from "./pages/dashboard.js";
import { renderGenerator } from "./pages/generator.js";
import { renderModels } from "./pages/models.js";
import { renderReports } from "./pages/reports.js";
import { renderSettings } from "./pages/settings.js";
import { renderTraining } from "./pages/training.js";
import { renderViewer } from "./pages/viewer.js";
import { renderImportData } from "./pages/import_data.js";

const routes = {
  "/": {
    title: "Dashboard",
    eyebrow: "Overview",
    render: renderDashboard,
  },
  "/generator": {
    title: "Data Generator",
    eyebrow: "Datasets",
    render: renderGenerator,
  },
  "/viewer": {
    title: "Data Viewer",
    eyebrow: "Browse data",
    render: renderViewer,
  },
  "/training": {
    title: "Training",
    eyebrow: "Models pipeline",
    render: renderTraining,
  },
  "/models": {
    title: "Models",
    eyebrow: "Artifacts",
    render: renderModels,
  },
  "/assignment-lab": {
    title: "Assignment Lab",
    eyebrow: "Recommendations",
    render: renderAssignmentLab,
  },
  "/reports": {
    title: "Reports",
    eyebrow: "Exports",
    render: renderReports,
  },
  "/settings": {
    title: "Settings",
    eyebrow: "Configuration",
    render: renderSettings,
  },
  "/import-data": {
    title: "Import Data",
    eyebrow: "External datasets",
    render: renderImportData,
  },
};

const appState = {
  lastDatasetId: window.localStorage.getItem("sandbox:lastDatasetId") || "",
};

function normalizePath(pathname) {
  if (pathname.length > 1 && pathname.endsWith("/")) {
    return pathname.slice(0, -1);
  }
  return pathname;
}

function getCurrentRoute() {
  const path = normalizePath(window.location.pathname);
  return routes[path] ? path : "/";
}

export function htmlEscape(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

export function prettyJson(value) {
  return htmlEscape(JSON.stringify(value, null, 2));
}

export function setLastDatasetId(datasetId) {
  appState.lastDatasetId = datasetId;
  window.localStorage.setItem("sandbox:lastDatasetId", datasetId);
}

export function getLastDatasetId() {
  return appState.lastDatasetId;
}

export function toast(title, message) {
  const stack = document.querySelector("#toastStack");
  const item = document.createElement("div");
  item.className = "toast";
  item.innerHTML = `<strong>${htmlEscape(title)}</strong><span>${htmlEscape(message)}</span>`;
  stack.append(item);
  window.setTimeout(() => item.remove(), 5200);
}

export function renderError(error) {
  return `
    <article class="card">
      <h2>Ошибка</h2>
      <p class="muted">${htmlEscape(error.message || error)}</p>
    </article>
  `;
}

export function tableFromRows(rows, columns) {
  if (!Array.isArray(rows) || rows.length === 0) {
    return '<div class="empty">Нет данных для отображения.</div>';
  }

  const resolvedColumns = columns || Object.keys(rows[0]);
  const head = resolvedColumns.map((column) => `<th>${htmlEscape(column)}</th>`).join("");
  const body = rows
    .map((row) => {
      const cells = resolvedColumns
        .map((column) => {
          const value = row[column];
          const displayValue =
            typeof value === "object" ? JSON.stringify(value) : String(value ?? "");
          return `<td>${htmlEscape(displayValue)}</td>`;
        })
        .join("");
      return `<tr>${cells}</tr>`;
    })
    .join("");

  return `
    <div class="table-wrap">
      <table class="table">
        <thead><tr>${head}</tr></thead>
        <tbody>${body}</tbody>
      </table>
    </div>
  `;
}

export function pageNotice(title, body, badge = "Backend stage pending") {
  return `
    <article class="card">
      <span class="badge">${htmlEscape(badge)}</span>
      <h2>${htmlEscape(title)}</h2>
      <p class="muted">${htmlEscape(body)}</p>
    </article>
  `;
}

async function updateBackendStatus() {
  const statusElement = document.querySelector("#backendStatus");

  try {
    await api.health();
    statusElement.className = "status-pill status-ok";
    statusElement.innerHTML = '<span class="status-dot"></span><span>Online</span>';
  } catch (error) {
    statusElement.className = "status-pill status-error";
    statusElement.innerHTML = '<span class="status-dot"></span><span>Offline</span>';
  }
}

async function renderRoute() {
  const routePath = getCurrentRoute();
  const route = routes[routePath];
  const root = document.querySelector("#appRoot");

  document.querySelector("#pageTitle").textContent = route.title;
  document.querySelector("#routeEyebrow").textContent = route.eyebrow;
  document.title = `${route.title} · COMPASS AI Sandbox`;

  document.querySelectorAll("[data-route]").forEach((link) => {
    link.classList.toggle("active", link.dataset.route === routePath);
  });

  root.classList.add("loading");
  root.innerHTML = '<div class="empty">Загрузка...</div>';

  try {
    root.innerHTML = await route.render();
  } catch (error) {
    root.innerHTML = renderError(error);
  } finally {
    root.classList.remove("loading");
  }
}

function bindNavigation() {
  document.body.addEventListener("click", (event) => {
    const link = event.target.closest("[data-link]");
    if (!link) {
      return;
    }

    const url = new URL(link.href);
    if (url.origin !== window.location.origin) {
      return;
    }

    event.preventDefault();
    window.history.pushState({}, "", url.pathname);
    renderRoute();
  });

  window.addEventListener("popstate", renderRoute);

  document.querySelector("#refreshButton").addEventListener("click", async () => {
    await updateBackendStatus();
    await renderRoute();
    toast("Обновлено", "Данные страницы запрошены заново.");
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  bindNavigation();
  await updateBackendStatus();
  await renderRoute();
});