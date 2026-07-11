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

export async function apiPost(path, payload = {}) {
  const response = await fetch(path, {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify(payload),
  });

  return parseResponse(response);
}

export async function apiPut(path, payload = {}) {
  const response = await fetch(path, {
    method: "PUT",
    headers: JSON_HEADERS,
    body: JSON.stringify(payload),
  });

  return parseResponse(response);
}

export async function apiPatch(path, payload = {}) {
  const response = await fetch(path, {
    method: "PATCH",
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

async function apiDelete(path) {
  const response = await fetch(path, {
    method: "DELETE",
  });

  return parseResponse(response);
}

export const api = {
  health: () => apiGet("/api/health"),
  status: () => apiGet("/api/status"),
  config: () => apiGet("/api/config"),
  settings: () => apiGet("/api/config/settings"),
  sessions: () => apiGet("/api/sessions"),
  sandboxSettings: () => apiGet("/api/settings"),
  sandboxSettingsSchema: () => apiGet("/api/settings/schema"),
  updateSandboxSettings: (payload) => apiPut("/api/settings", payload),
  patchSandboxSettings: (payload) => apiPatch("/api/settings", payload),
  resetSandboxSettings: () => apiPost("/api/settings/reset", {}),

  contractsSummary: () => apiGet("/api/contracts/summary"),
  featureSchemas: (preview = true) =>
    apiGet(`/api/feature-schemas?preview=${preview ? "true" : "false"}`),

  datasets: () => apiGet("/api/data-viewer/datasets"),
  dataViewerDatasets: () => apiGet("/api/data-viewer/datasets"),
  deleteDataset: (datasetId, datasetKind = "") =>
    apiDelete(
      `/api/data-viewer/datasets/${encodeURIComponent(datasetId)}` +
        `${datasetKind ? `?dataset_kind=${encodeURIComponent(datasetKind)}` : ""}`,
    ),

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

  buildFeatures: (payload) => apiPost("/api/features/build", payload),

  featureMetadata: (datasetId, query = "") =>
    apiGet(
      `/api/features/datasets/${encodeURIComponent(datasetId)}/metadata${query}`,
    ),

  runTraining: (payload) => apiPost("/api/training/run", payload),
  trainingSessions: () => apiGet("/api/training/sessions"),

  trainingSession: (sessionId) =>
    apiGet(`/api/training/sessions/${encodeURIComponent(sessionId)}`),

  trainingArtifacts: (sessionId) =>
    apiGet(`/api/training/sessions/${encodeURIComponent(sessionId)}/artifacts`),

  trainingSessionArtifacts: (sessionId) =>
    apiGet(`/api/training/sessions/${encodeURIComponent(sessionId)}/artifacts`),

  deleteTrainingSession: (sessionId) =>
    apiDelete(`/api/training/sessions/${encodeURIComponent(sessionId)}`),

  trainingModelArtifact: (sessionId, modelName) =>
    apiGet(
      `/api/training/sessions/${encodeURIComponent(sessionId)}/models/` +
        encodeURIComponent(modelName),
    ),

  trainingReports: () => apiGet("/api/reports/training"),

  generateTrainingReport: (sessionId) =>
    apiPost(`/api/reports/training/${encodeURIComponent(sessionId)}/generate`, {}),

  trainingReport: (sessionId) =>
    apiGet(`/api/reports/training/${encodeURIComponent(sessionId)}`),

  modelsList: () => apiGet("/api/models"),

  modelMetadata: (sessionId, modelName) =>
    apiGet(
      `/api/models/${encodeURIComponent(sessionId)}/` +
        encodeURIComponent(modelName),
    ),

  modelValidation: (sessionId, modelName) =>
    apiGet(
      `/api/models/${encodeURIComponent(sessionId)}/` +
        `${encodeURIComponent(modelName)}/validation`,
    ),

  validateModel: (sessionId, modelName, payload) =>
    apiPost(
      `/api/models/${encodeURIComponent(sessionId)}/` +
        `${encodeURIComponent(modelName)}/validate`,
      payload,
    ),

  deleteModel: (sessionId, modelName) =>
    apiDelete(
      `/api/models/${encodeURIComponent(sessionId)}/` +
        encodeURIComponent(modelName),
    ),

  exportModel: (sessionId, modelName, payload) =>
    apiPost(
      `/api/models/${encodeURIComponent(sessionId)}/` +
        `${encodeURIComponent(modelName)}/export`,
      payload,
    ),

  testCases: () => apiGet("/api/test-cases"),
  generateTestCase: (payload) => apiPost("/api/test-cases/generate", payload),
  importTestCase: (payload) => apiPost("/api/test-cases/import", payload),
  createTestCaseFromDataset: (payload) =>
    apiPost("/api/test-cases/from-dataset", payload),

  testCase: (testCaseId) =>
    apiGet(`/api/test-cases/${encodeURIComponent(testCaseId)}`),

  testCaseSummary: (testCaseId) =>
    apiGet(`/api/test-cases/${encodeURIComponent(testCaseId)}/summary`),

  testCaseTable: (testCaseId, tableName) =>
    apiGet(
      `/api/test-cases/${encodeURIComponent(testCaseId)}/tables/` +
        encodeURIComponent(tableName),
    ),

  testCasePendingTasks: (testCaseId) =>
    apiGet(`/api/test-cases/${encodeURIComponent(testCaseId)}/pending-tasks`),

  testCaseRecommendationContext: (testCaseId) =>
    apiGet(
      `/api/test-cases/${encodeURIComponent(testCaseId)}/` +
        "recommendation-context",
    ),

  deleteTestCase: (testCaseId) =>
    apiDelete(`/api/test-cases/${encodeURIComponent(testCaseId)}`),

  recommendationModes: () => apiGet("/api/recommendations/modes"),

  recommendableTasks: (testCaseId) =>
    apiGet(
      `/api/recommendations/test-cases/${encodeURIComponent(testCaseId)}/tasks`,
    ),

  singleRecommendation: (payload) =>
    apiPost("/api/recommendations/single", payload),

  savedRecommendations: (testCaseId) =>
    apiGet(`/api/recommendations/test-cases/${encodeURIComponent(testCaseId)}`),

  savedRecommendation: (testCaseId, recommendationId) =>
    apiGet(
      `/api/recommendations/test-cases/${encodeURIComponent(testCaseId)}/` +
        encodeURIComponent(recommendationId),
    ),

  assignmentModes: () => apiGet("/api/assignment-sessions/modes"),

  runBulkAssignment: (payload) =>
    apiPost("/api/assignment-sessions/run", payload),

  recommendKanbanBoard: (payload) =>
    apiPost("/api/kanban-lab/recommend-board", payload),

  kanbanLabBoards: () => apiGet("/api/kanban-lab/boards"),
  kanbanLabBoard: (labId) =>
    apiGet(`/api/kanban-lab/boards/${encodeURIComponent(labId)}`),
  saveKanbanLabBoard: (payload) => apiPost("/api/kanban-lab/boards", payload),
  deleteKanbanLabBoard: (labId) =>
    apiDelete(`/api/kanban-lab/boards/${encodeURIComponent(labId)}`),

  assignmentSessions: () => apiGet("/api/assignment-sessions"),

  assignmentSession: (assignmentSessionId) =>
    apiGet(
      `/api/assignment-sessions/${encodeURIComponent(assignmentSessionId)}`,
    ),

  deleteAssignmentSession: (assignmentSessionId) =>
    apiDelete(
      `/api/assignment-sessions/${encodeURIComponent(assignmentSessionId)}`,
    ),

  llmStatus: () => apiGet("/api/llm/status"),

  explainRecommendation: (payload) =>
    apiPost("/api/llm/explain/recommendation", payload),

  explainAssignment: (payload) =>
    apiPost("/api/llm/explain/assignment", payload),

  explainSavedAssignmentSession: (assignmentSessionId, useLlm = true) =>
    apiPost(
      `/api/llm/explain/assignment-sessions/${encodeURIComponent(
        assignmentSessionId,
      )}?use_llm=${encodeURIComponent(useLlm)}`,
      {},
    ),

  exportReports: () => apiGet("/api/reports/exports"),

  exportReport: (reportId) =>
    apiGet(`/api/reports/exports/${encodeURIComponent(reportId)}`),

  deleteExportReport: (reportId) =>
    apiDelete(`/api/reports/exports/${encodeURIComponent(reportId)}`),

  generateDatasetExport: (datasetId, payload = {}) =>
    apiPost(
      `/api/reports/exports/datasets/${encodeURIComponent(datasetId)}`,
      payload,
    ),

  generateModelExport: (sessionId) =>
    apiPost(`/api/reports/exports/models/${encodeURIComponent(sessionId)}`, {}),

  generateAssignmentExport: (assignmentSessionId) =>
    apiPost(
      `/api/reports/exports/assignments/${encodeURIComponent(
        assignmentSessionId,
      )}`,
      {},
    ),

  exportReportFileUrl: (reportId, fileName) =>
    `/api/reports/exports/${encodeURIComponent(reportId)}/files/` +
    encodeURIComponent(fileName),

  featureSchema: (profileId, preview = false) =>
    apiGet(
      `/api/feature-schemas/${encodeURIComponent(profileId)}` +
        `${preview ? "?preview=true" : ""}`,
    ),

  featureSchemaTemplate: () => apiGet("/api/feature-schemas/template"),

  createFeatureSchema: (payload) => apiPost("/api/feature-schemas", payload),

  updateFeatureSchema: (profileId, payload) =>
    apiPut(`/api/feature-schemas/${encodeURIComponent(profileId)}`, payload),

  deleteFeatureSchema: (profileId) =>
    apiDelete(`/api/feature-schemas/${encodeURIComponent(profileId)}`),

  addSchemaFeature: (profileId, group, payload) =>
    apiPost(
      `/api/feature-schemas/${encodeURIComponent(profileId)}/features/` +
        encodeURIComponent(group),
      payload,
    ),

  updateSchemaFeature: (profileId, group, featureName, payload) =>
    apiPatch(
      `/api/feature-schemas/${encodeURIComponent(profileId)}/features/` +
        `${encodeURIComponent(group)}/${encodeURIComponent(featureName)}`,
      payload,
    ),

  deleteSchemaFeature: (profileId, group, featureName) =>
    apiDelete(
      `/api/feature-schemas/${encodeURIComponent(profileId)}/features/` +
        `${encodeURIComponent(group)}/${encodeURIComponent(featureName)}`,
    ),
};
