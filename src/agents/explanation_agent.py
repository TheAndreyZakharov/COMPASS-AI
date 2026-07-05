from __future__ import annotations

import json
import re
from typing import Any

from src.agents.state import AgentState
from src.llm.ollama_client import OllamaClient, ollama_available

RECOMMENDED_LINE_PATTERN = re.compile(
    r"рекомендованн(?:ый|ая|ое)\s+исполнитель\s*:\s*(.+)",
    flags=re.IGNORECASE,
)


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _candidate_names(state: AgentState) -> list[str]:
    names: list[str] = []

    for candidate in state.top_candidates:
        name = _clean_text(candidate.get("name"))
        if name:
            names.append(name)

    return names


def _top_candidate_name(state: AgentState) -> str:
    if not state.top_candidates:
        return ""

    return _clean_text(state.top_candidates[0].get("name"))


def _looks_like_wrong_recommended_person(
    explanation: str,
    top_name: str,
    allowed_names: list[str],
) -> bool:
    if not explanation.strip():
        return True

    if top_name and top_name not in explanation:
        return True

    for line in explanation.splitlines():
        match = RECOMMENDED_LINE_PATTERN.search(line)
        if not match:
            continue

        recommended_part = match.group(1).strip()
        return not (top_name and top_name in recommended_part)

    known_candidate_mentioned = any(name in explanation for name in allowed_names)
    return not known_candidate_mentioned


def _validate_llm_explanation(
    explanation: str,
    state: AgentState,
) -> tuple[bool, str | None]:
    allowed_names = _candidate_names(state)
    top_name = _top_candidate_name(state)

    if not allowed_names:
        return False, "no allowed candidate names"

    if _looks_like_wrong_recommended_person(
        explanation=explanation,
        top_name=top_name,
        allowed_names=allowed_names,
    ):
        return False, "LLM explanation mentioned a person outside top candidates"

    return True, None


def candidate_line(candidate: dict[str, Any]) -> str:
    factors = candidate.get("factors", {})

    if not isinstance(factors, dict):
        factors = {}

    return (
        f"{candidate.get('rank')}. {candidate.get('name')} "
        f"({candidate.get('role')}, {candidate.get('grade')}) — "
        f"score={candidate.get('score')}, "
        f"skill={factors.get('skill_match')}, "
        f"risk={factors.get('risk')}, "
        f"workload_pressure={factors.get('workload_pressure')}"
    )


def fallback_explanation(state: AgentState) -> str:
    if not state.top_candidates:
        return "Рекомендация не сформирована: нет кандидатов."

    top = state.top_candidates[0]
    alternatives = state.top_candidates[1:]

    lines = [
        "## COMPASS AI Recommendation",
        "",
        f"Рекомендованный исполнитель: {top.get('name')} ({top.get('role')}).",
        f"Режим рекомендации: {state.recommendation_mode}.",
        f"Score: {top.get('score')}.",
        "",
        "Почему подходит:",
        "- ranking уже рассчитан COMPASS AI до этапа LLM-объяснения;",
        "- кандидат входит в разрешённый список candidates для этой задачи;",
        "- учтены skill match, риск, загрузка, скорость и надёжность.",
    ]

    candidate_scope = top.get("candidate_scope")
    if candidate_scope:
        lines.append(f"- область выбора кандидатов: {candidate_scope}.")

    risks = top.get("risks", [])

    if risks:
        lines.append("")
        lines.append("Риски:")
        lines.extend(f"- {risk}" for risk in risks)

    if alternatives:
        lines.append("")
        lines.append("Альтернативы:")
        lines.extend(f"- {candidate_line(candidate)}" for candidate in alternatives)

    lines.append("")
    lines.append(
        "Важно: это recommendation support. "
        "Финальное решение остаётся за тимлидом."
    )

    return "\n".join(lines)


def build_prompt(state: AgentState) -> str:
    task = state.task_features
    candidates = state.top_candidates
    allowed_names = _candidate_names(state)
    top_name = _top_candidate_name(state)

    payload = {
        "task": {
            "title": task.get("title"),
            "task_type": task.get("task_type"),
            "priority": task.get("priority"),
            "complexity": task.get("complexity"),
            "deadline_days": task.get("deadline_days"),
            "required_skills": task.get("required_skills"),
        },
        "recommendation_mode": state.recommendation_mode,
        "top_candidate_name": top_name,
        "allowed_candidate_names": allowed_names,
        "top_candidates": candidates,
    }

    return (
        "Сформируй краткое объяснение рекомендации на русском языке.\n"
        "ЖЁСТКИЕ ПРАВИЛА:\n"
        "1. Нельзя менять ranking кандидатов.\n"
        "2. Нельзя придумывать людей, имена, роли, навыки или project members.\n"
        "3. Рекомендованный исполнитель обязан быть top-1 из top_candidates.\n"
        "4. В строке 'Рекомендованный исполнитель' можно написать только top-1.\n"
        "5. Альтернативы можно брать только из allowed_candidate_names.\n"
        "6. Если данных мало, честно скажи, что профиль неполный.\n\n"
        "Структура ответа:\n"
        "## COMPASS AI Recommendation\n"
        "Рекомендованный исполнитель: <строго top-1>\n"
        "Почему подходит:\n"
        "Риски:\n"
        "Альтернативы:\n\n"
        f"Данные:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def run_explanation_agent(
    state: AgentState,
    use_llm: bool = True,
) -> AgentState:
    if not state.top_candidates:
        state.add_error("explanation_agent", "Top candidates are empty.")
        state.explanation = fallback_explanation(state)
        return state

    if not use_llm:
        state.explanation = fallback_explanation(state)
        return state

    if not ollama_available():
        state.explanation = fallback_explanation(state)
        return state

    system = (
        "Ты объясняющий агент COMPASS AI. "
        "Ты не выбираешь исполнителя, не меняешь ranking и не придумываешь данные. "
        "Ты обязан использовать только кандидатов из top_candidates. "
        "Если кандидат не указан во входных данных, его нельзя упоминать."
    )

    try:
        client = OllamaClient()
        explanation = client.generate(
            prompt=build_prompt(state),
            system=system,
            temperature=0.0,
            max_tokens=450,
        )
        is_valid, reason = _validate_llm_explanation(
            explanation=explanation,
            state=state,
        )

        if not is_valid:
            state.add_error("explanation_agent", reason or "Invalid LLM explanation.")
            state.explanation = fallback_explanation(state)
            return state

        state.explanation = explanation
    except Exception as error:
        state.add_error("explanation_agent", str(error))
        state.explanation = fallback_explanation(state)

    return state