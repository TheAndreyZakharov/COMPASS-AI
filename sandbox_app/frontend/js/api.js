const JSON_HEADERS = {
  "Content-Type": "application/json",
};

export class ApiError extends Error {
  constructor(message, status, payload) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    const message =
      typeof payload === "object"
        ? payload.error || payload.detail || JSON.stringify(payload)
        : payload;

    throw new ApiError(message || "API request failed", response.status, payload);
  }

  return payload;
}

export async function apiGet(path) {
  const response = await fetch(path, {
    headers: JSON_HEADERS,
  });

  return parseResponse(response);
}

export async function apiPost(path, payload) {
  const response = await fetch(path, {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify(payload),
  });

  return parseResponse(response);
}

export async function apiUpload(path, formData) {
  const response = await fetch(path, {
    method: "POST",
    body: formData,
  });

  return parseResponse(response);
}

export const api = {
  health: () => apiGet("/api/health"),
  status: () => apiGet("/api/status"),
  config: () => apiGet("/api/config"),
  settings: () => apiGet("/api/config/settings"),
  sessions: () => apiGet("/api/sessions"),
  contractsSummary: () => apiGet("/api/contracts/summary"),
  featureSchemas: () => apiGet("/api/feature-schemas?preview=true"),
  datasets: () => apiGet("/api/data-viewer/datasets"),

  datasetSummary: (datasetId, query = "") =>
    apiGet(
      `/api/data-viewer/datasets/${encodeURIComponent(datasetId)}/summary${query}`,
    ),

  datasetTable: (datasetId, tableName, query = "") =>
    apiGet(
      `/api/data-viewer/datasets/${encodeURIComponent(datasetId)}/` +
        `${encodeURIComponent(tableName)}${query}`,
    ),

  kanban: (datasetId, query = "") =>
    apiGet(
      `/api/data-viewer/datasets/${encodeURIComponent(datasetId)}/kanban${query}`,
    ),

  generateTeam: (payload) => apiPost("/api/generate/team", payload),
  generateTasks: (payload) => apiPost("/api/generate/tasks", payload),
  generateHistory: (payload) => apiPost("/api/generate/history", payload),
  generateDataset: (payload) => apiPost("/api/generate/dataset", payload),

  importSupportedTables: () => apiGet("/api/import-data/supported-tables"),
  importPreview: (formData) => apiUpload("/api/import-data/preview", formData),
  importDataset: (formData) => apiUpload("/api/import-data/datasets", formData),
};