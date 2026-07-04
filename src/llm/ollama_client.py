from __future__ import annotations

import os
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class OllamaConfig:
    base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b-instruct")
    timeout_seconds: float = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "30"))


class OllamaClient:
    def __init__(self, config: OllamaConfig | None = None) -> None:
        self.config = config or OllamaConfig()

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 500,
    ) -> str:
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        if system:
            payload["system"] = system

        try:
            with httpx.Client(timeout=self.config.timeout_seconds) as client:
                response = client.post(
                    f"{self.config.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPError as error:
            raise RuntimeError(f"Ollama request failed: {error}") from error

        data = response.json()
        text = str(data.get("response", "")).strip()

        if not text:
            raise RuntimeError("Ollama returned an empty response.")

        return text


def ollama_available(config: OllamaConfig | None = None) -> bool:
    config = config or OllamaConfig()

    try:
        with httpx.Client(timeout=3.0) as client:
            response = client.get(f"{config.base_url}/api/tags")
            return response.status_code == 200
    except httpx.HTTPError:
        return False


def main() -> None:
    client = OllamaClient()
    response = client.generate(
        "Кратко объясни на русском, почему низкая загрузка важна при назначении задачи.",
        max_tokens=120,
    )
    print(response)


if __name__ == "__main__":
    main()