from __future__ import annotations

import os
from typing import Any

import httpx
from dotenv import load_dotenv


class PlaneClientError(RuntimeError):
    """Base error for Plane client failures."""


class PlaneClient:
    """Minimal REST client for local/self-hosted Plane.

    Plane API currently uses the term "work items" for tasks.
    Some method aliases with "issue" are kept for roadmap compatibility.
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        workspace_slug: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        load_dotenv()

        self.base_url = (base_url or os.getenv("PLANE_BASE_URL") or "").rstrip("/")
        self.api_key = api_key or os.getenv("PLANE_API_KEY") or ""
        self.workspace_slug = workspace_slug or os.getenv("PLANE_WORKSPACE_SLUG") or ""
        self.timeout = timeout

        if not self.base_url:
            raise PlaneClientError("PLANE_BASE_URL is not configured.")
        if not self.api_key:
            raise PlaneClientError("PLANE_API_KEY is not configured.")
        if not self.workspace_slug:
            raise PlaneClientError("PLANE_WORKSPACE_SLUG is not configured.")

        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "x-api-key": self.api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> PlaneClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        response = self._client.request(method, path, **kwargs)

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            body_preview = response.text[:500]
            raise PlaneClientError(
                f"Plane API request failed: {method} {path} "
                f"status={response.status_code} body={body_preview!r}"
            ) from exc

        if not response.content:
            return None

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response.text

        return response.json()

    @staticmethod
    def _items(payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            results = payload.get("results")
            if isinstance(results, list):
                return results
        return []

    def healthcheck(self) -> bool:
        """Check that Plane API authentication and workspace access work."""
        try:
            projects = self.list_projects()
        except PlaneClientError:
            return False

        return isinstance(projects, list)

    def api_healthcheck(self) -> dict[str, Any] | str:
        return self._request("GET", "/api/")

    def list_projects(self) -> list[dict[str, Any]]:
        payload = self._request(
            "GET",
            f"/api/v1/workspaces/{self.workspace_slug}/projects/",
        )
        return self._items(payload)

    def get_workspace(self) -> dict[str, Any]:
        projects = self.list_projects()
        return {
            "slug": self.workspace_slug,
            "projects_count": len(projects),
            "projects": projects,
        }

    def list_work_items(self, project_id: str) -> list[dict[str, Any]]:
        payload = self._request(
            "GET",
            f"/api/v1/workspaces/{self.workspace_slug}/projects/{project_id}/work-items/",
        )
        return self._items(payload)

    def get_work_item(self, project_id: str, work_item_id: str) -> dict[str, Any]:
        payload = self._request(
            "GET",
            f"/api/v1/workspaces/{self.workspace_slug}/projects/{project_id}/work-items/{work_item_id}/",
        )
        if not isinstance(payload, dict):
            raise PlaneClientError("Unexpected work item detail response format.")
        return payload

    def create_work_item(
        self,
        project_id: str,
        name: str,
        description_html: str,
        priority: str = "medium",
        labels: list[str] | None = None,
        target_date: str | None = None,
    ) -> dict[str, Any]:
        """Create a work item in Plane."""
        request_payload: dict[str, Any] = {
            "name": name,
            "description_html": description_html,
            "priority": priority,
        }

        if labels:
            request_payload["labels"] = labels

        if target_date:
            request_payload["target_date"] = target_date

        payload = self._request(
            "POST",
            f"/api/v1/workspaces/{self.workspace_slug}/projects/{project_id}/work-items",
            json=request_payload,
        )

        if not isinstance(payload, dict):
            raise PlaneClientError("Unexpected create work item response format.")

        return payload

    def list_project_members(self, project_id: str) -> list[dict[str, Any]]:
        payload = self._request(
            "GET",
            f"/api/v1/workspaces/{self.workspace_slug}/projects/{project_id}/members/",
        )
        return self._items(payload)

    def list_states(self, project_id: str) -> list[dict[str, Any]]:
        payload = self._request(
            "GET",
            f"/api/v1/workspaces/{self.workspace_slug}/projects/{project_id}/states/",
        )
        return self._items(payload)

    def list_labels(self, project_id: str) -> list[dict[str, Any]]:
        payload = self._request(
            "GET",
            f"/api/v1/workspaces/{self.workspace_slug}/projects/{project_id}/labels/",
        )
        return self._items(payload)

    def create_label(
        self,
        project_id: str,
        name: str,
        color: str | None = None,
    ) -> dict[str, Any]:
        """Create a project label in Plane."""
        request_payload: dict[str, Any] = {"name": name}

        if color:
            request_payload["color"] = color

        payload = self._request(
            "POST",
            f"/api/v1/workspaces/{self.workspace_slug}/projects/{project_id}/labels/",
            json=request_payload,
        )

        if not isinstance(payload, dict):
            raise PlaneClientError("Unexpected create label response format.")

        return payload

    def list_work_item_comments(
        self,
        project_id: str,
        work_item_id: str,
    ) -> list[dict[str, Any]]:
        payload = self._request(
            "GET",
            f"/api/v1/workspaces/{self.workspace_slug}/projects/{project_id}/work-items/{work_item_id}/comments/",
        )
        return self._items(payload)

    def create_work_item_comment(
        self,
        project_id: str,
        work_item_id: str,
        text: str,
    ) -> dict[str, Any]:
        payload = self._request(
            "POST",
            f"/api/v1/workspaces/{self.workspace_slug}/projects/{project_id}/work-items/{work_item_id}/comments/",
            json={
                "comment_html": text,
                "access": "INTERNAL",
                "external_source": "COMPASS_AI",
            },
        )
        if not isinstance(payload, dict):
            raise PlaneClientError("Unexpected create comment response format.")
        return payload

    def update_work_item_assignee(
        self,
        project_id: str,
        work_item_id: str,
        assignee_id: str,
    ) -> dict[str, Any]:
        payload = self._request(
            "PATCH",
            f"/api/v1/workspaces/{self.workspace_slug}/projects/{project_id}/work-items/{work_item_id}/",
            json={
                "assignees": [assignee_id],
            },
        )
        if not isinstance(payload, dict):
            raise PlaneClientError("Unexpected update assignee response format.")
        return payload

    # Roadmap compatibility aliases.

    def list_issues(self, project_id: str) -> list[dict[str, Any]]:
        return self.list_work_items(project_id)

    def get_issue(self, project_id: str, issue_id: str) -> dict[str, Any]:
        return self.get_work_item(project_id, issue_id)

    def create_issue(
        self,
        project_id: str,
        name: str,
        description_html: str,
        priority: str = "medium",
        labels: list[str] | None = None,
        target_date: str | None = None,
    ) -> dict[str, Any]:
        return self.create_work_item(
            project_id=project_id,
            name=name,
            description_html=description_html,
            priority=priority,
            labels=labels,
            target_date=target_date,
        )

    def create_issue_comment(
        self,
        project_id: str,
        issue_id: str,
        text: str,
    ) -> dict[str, Any]:
        return self.create_work_item_comment(project_id, issue_id, text)

    def update_issue_assignee(
        self,
        project_id: str,
        issue_id: str,
        assignee_id: str,
    ) -> dict[str, Any]:
        return self.update_work_item_assignee(project_id, issue_id, assignee_id)