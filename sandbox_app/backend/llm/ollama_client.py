from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen2.5:1.5b-instruct"
DEFAULT_TIMEOUT_SECONDS = 30


class OllamaClientError(RuntimeError):
    """Raised when Ollama request fails."""


@dataclass(frozen=True)
class OllamaSettings:
    base_url: str = DEFAULT_OLLAMA_BASE_URL
    model: str = DEFAULT_OLLAMA_MODEL
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS

    @classmethod
    def from_env(cls) -> OllamaSettings:
        timeout_raw = os.getenv(
            "SANDBOX_LLM_TIMEOUT_SECONDS",
            str(DEFAULT_TIMEOUT_SECONDS),
        )

        try:
            timeout = int(timeout_raw)
        except ValueError:
            timeout = DEFAULT_TIMEOUT_SECONDS

        return cls(
            base_url=os.getenv("SANDBOX_OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL),
            model=os.getenv("SANDBOX_OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL),
            timeout_seconds=max(1, timeout),
        )


@dataclass(frozen=True)
class OllamaGenerateResult:
    model: str
    response: str
    raw: dict[str, Any]


class OllamaClient:
    def __init__(self, settings: OllamaSettings | None = None) -> None:
        self.settings = settings or OllamaSettings.from_env()
        self.base_url = self.settings.base_url.rstrip("/")

    def _request_json(
        self,
        path: str,
        payload: dict[str, Any] | None = None,
        method: str = "GET",
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        data = None

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url=url,
            data=data,
            method=method,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.settings.timeout_seconds,
            ) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise OllamaClientError(f"Ollama HTTP error {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise OllamaClientError(f"Ollama is unavailable: {exc.reason}") from exc
        except TimeoutError as exc:
            raise OllamaClientError("Ollama request timed out") from exc

        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            raise OllamaClientError("Ollama returned invalid JSON") from exc

        if not isinstance(parsed, dict):
            raise OllamaClientError("Ollama response must be JSON object")

        return parsed

    def health(self) -> dict[str, Any]:
        try:
            tags = self._request_json("/api/tags")
        except OllamaClientError as exc:
            return {
                "available": False,
                "base_url": self.base_url,
                "model": self.settings.model,
                "error": str(exc),
            }

        models = tags.get("models", [])
        model_names = [
            item.get("name")
            for item in models
            if isinstance(item, dict) and item.get("name")
        ]

        return {
            "available": True,
            "base_url": self.base_url,
            "model": self.settings.model,
            "model_present": self.settings.model in model_names,
            "models": model_names,
        }

    def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.2,
    ) -> OllamaGenerateResult:
        payload = {
            "model": self.settings.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": 8192,
            },
        }
        raw = self._request_json("/api/generate", payload=payload, method="POST")
        response = str(raw.get("response", "")).strip()

        if not response:
            raise OllamaClientError("Ollama returned empty response")

        return OllamaGenerateResult(
            model=self.settings.model,
            response=response,
            raw=raw,
        )