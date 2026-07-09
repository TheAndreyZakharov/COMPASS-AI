import { api } from "./api.js";

const APP_BUILD_ID = "20260709_frontend_bootstrap_fix";
const browserWindow = typeof window !== "undefined" ? window : null;
const browserDocument = typeof document !== "undefined" ? document : null;
const localStorageRef = browserWindow?.localStorage || null;

const routes = {
  "/": {
    title: "Dashboard",
    eyebrow: "Overview",
    modulePath: "./pages/dashboard.js",
    exports: ["renderDashboard", "renderPage", "default"],
  },
  "/generator": {
    title: "Data Generator",
    eyebrow: "Datasets",
    modulePath: "./pages/generator.js",
    exports: ["renderGenerator", "renderPage", "default"],
  },
  "/viewer": {
    title: "Data Viewer",
    eyebrow: "Browse data",
    modulePath: "./pages/viewer.js",
    exports: ["renderViewer", "renderPage", "default"],
  },
  "/training": {
    title: "Training",
    eyebrow: "Models pipeline",
    modulePath: "./pages/training.js",
    exports: ["renderTraining", "renderPage", "default"],
  },
  "/models": {
    title: "Models",
    eyebrow: "Artifacts",
    modulePath: "./pages/models.js",
    exports: ["renderModels", "renderPage", "default"],
  },
  "/assignment-lab": {
    title: "Assignment Lab",
    eyebrow: "Recommendations",
    modulePath: "./pages/assignment_lab.js",
    exports: [
      "renderAssignmentLab",
      "renderAssignmentLabPage",
      "renderPage",
      "default",
    ],
  },
  "/reports": {
    title: "Reports",
    eyebrow: "Exports",
    modulePath: "./pages/reports.js",
    exports: ["renderReports", "renderReportsPage", "renderPage", "default"],
  },
  "/settings": {
    title: "Settings",
    eyebrow: "Configuration",
    modulePath: "./pages/settings.js",
    exports: ["renderSettings", "renderPage", "default"],
  },
  "/import-data": {
    title: "Import Data",
    eyebrow: "External datasets",
    modulePath: "./pages/import_data.js",
    exports: ["renderImportData", "renderPage", "default"],
  },
};

const appState = {
  lastDatasetId: localStorageRef?.getItem("sandbox:lastDatasetId") || "",
};

function normalizePath(pathname) {
  if (pathname.length > 1 && pathname.endsWith("/")) {
    return pathname.slice(0, -1);
  }

  return pathname;
}

function getCurrentRoute() {
  const path = normalizePath(browserWindow?.location.pathname || "/");
  return routes[path] ? path : "/";
}

function cacheBustedModulePath(modulePath) {
  return `${modulePath}?v=${encodeURIComponent(APP_BUILD_ID)}`;
}

async function loadRouteRenderer(route) {
  const pageModule = await import(cacheBustedModulePath(route.modulePath));

  for (const exportName of route.exports) {
    const renderer = pageModule[exportName];

    if (typeof renderer === "function") {
      return renderer;
    }
  }

  throw new Error(`Page renderer was not found for ${route.modulePath}`);
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
  return htmlEscape(JSON.stringify(value ?? {}, null, 2));
}

export function setLastDatasetId(datasetId) {
  appState.lastDatasetId = datasetId;
  localStorageRef?.setItem("sandbox:lastDatasetId", datasetId);
}

export function getLastDatasetId() {
  return appState.lastDatasetId;
}

export function toast(title, message = "") {
  const stack = browserDocument?.querySelector("#toastStack");

  if (!stack) {
    console.log(`${title}: ${message}`);
    return;
  }

  const item = browserDocument.createElement("div");
  item.className = "toast";
  item.innerHTML = `<strong>${htmlEscape(title)}</strong><span>${htmlEscape(message)}</span>`;
  stack.append(item);
  browserWindow?.setTimeout(() => item.remove(), 5200);
}

browserWindow?.addEventListener("sandbox-toast", (event) => {
  const detail = event.detail || {};
  toast(detail.title || detail.type || "Info", detail.message || "");
});

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
  const head = resolvedColumns
    .map((column) => `<th>${htmlEscape(column)}</th>`)
    .join("");
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
  const statusElement = browserDocument?.querySelector("#backendStatus");

  if (!statusElement) {
    return;
  }

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
  const root = browserDocument?.querySelector("#appRoot");

  if (!root) {
    return;
  }

  browserDocument.querySelector("#pageTitle").textContent = route.title;
  browserDocument.querySelector("#routeEyebrow").textContent = route.eyebrow;
  browserDocument.title = `${route.title} · COMPASS AI Sandbox`;

  browserDocument.querySelectorAll("[data-route]").forEach((link) => {
    link.classList.toggle("active", link.dataset.route === routePath);
  });

  root.classList.add("loading");
  root.innerHTML = '<div class="empty">Загрузка...</div>';

  try {
    const renderer = await loadRouteRenderer(route);
    const rendered = await renderer(root);

    if (typeof rendered === "string") {
      root.innerHTML = rendered;
    } else if (rendered === undefined && root.innerHTML === "") {
      root.innerHTML = "";
    } else if (rendered !== undefined) {
      root.innerHTML = String(rendered);
    }
  } catch (error) {
    root.innerHTML = renderError(error);
    console.error(error);
  } finally {
    root.classList.remove("loading");
  }
}

function bindNavigation() {
  browserDocument?.body.addEventListener("click", (event) => {
    const link = event.target.closest("[data-link]");

    if (!link) {
      return;
    }

    const url = new URL(link.href);

    if (url.origin !== browserWindow?.location.origin) {
      return;
    }

    event.preventDefault();
    browserWindow.history.pushState({}, "", url.pathname);
    renderRoute();
  });

  browserWindow?.addEventListener("popstate", renderRoute);

  browserDocument
    ?.querySelector("#refreshButton")
    ?.addEventListener("click", async () => {
      await updateBackendStatus();
      await renderRoute();
      toast("Обновлено", "Данные страницы запрошены заново.");
    });
}

browserDocument?.addEventListener("DOMContentLoaded", async () => {
  bindNavigation();
  await updateBackendStatus();
  await renderRoute();
});