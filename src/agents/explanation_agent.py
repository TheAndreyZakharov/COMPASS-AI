from __future__ import annotations

import json
from typing import Any

from src.agents.state import AgentState
from src.llm.ollama_client import OllamaClient, ollama_available

PLANE_SCOPED_SOURCES = {
    "plane_scoped_rule_based",
    "plane_project_member",
}


def _candidate_text(candidate: dict[str, Any], key: str) -> str:
    value = candidate.get(key)

    if value is None:
        return ""

    return str(value).strip()


def _is_plane_scoped_recommendation(state: AgentState) -> bool:
    for candidate in state.top_candidates:
        if not isinstance(candidate, dict):
            continue

        source = _candidate_text(candidate, "source")
        mapping_status = _candidate_text(candidate, "mapping_status")
        plane_user_id = _candidate_text(candidate, "plane_user_id")

        if source in PLANE_SCOPED_SOURCES:
            return True

        if mapping_status == "plane_unmapped" and plane_user_id:
            return True

    return False


def candidate_line(candidate: dict[str, Any]) -> str:
    factors = candidate.get("factors", {})

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
        "- модель оценила совпадение задачи и доступного списка кандидатов;",
        "- учтены skill match, риск, загрузка, скорость и надёжность;",
        "- итоговый ranking сформирован до LLM-объяснения.",
    ]

    if _is_plane_scoped_recommendation(state):
        lines.extend(
            [
                "",
                "Ограничение Plane Live:",
                "- кандидат выбран только из реальных Plane project members;",
                "- synthetic employees не участвовали в ranking;",
                "- LLM не выбирает исполнителя, а только объясняет готовый ranking.",
            ],
        )

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
    candidate_names = [
        candidate.get("name")
        for candidate in candidates
        if isinstance(candidate, dict) and candidate.get("name")
    ]

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
        "candidate_names_allowed": candidate_names,
        "top_candidates": candidates,
        "plane_scoped": _is_plane_scoped_recommendation(state),
    }

    return (
        "Сформируй краткое объяснение рекомендации на русском языке.\n"
        "Нельзя менять ranking кандидатов.\n"
        "Нельзя придумывать людей, факты, роли или навыки.\n"
        "Рекомендованный исполнитель обязан быть top-1 из top_candidates.\n"
        "Имена можно брать только из candidate_names_allowed.\n"
        "Если plane_scoped=true, кандидаты уже ограничены реальными Plane members.\n"
        "Не упоминай людей, которых нет в top_candidates.\n"
        "Структура: рекомендованный исполнитель, почему подходит, риски, альтернативы.\n\n"
        f"Данные:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def _llm_explanation_is_valid(
    explanation: str,
    state: AgentState,
) -> bool:
    if not explanation.strip():
        return False

    if not _is_plane_scoped_recommendation(state):
        return True

    allowed_names = {
        _candidate_text(candidate, "name")
        for candidate in state.top_candidates
        if isinstance(candidate, dict)
    }
    allowed_names = {name for name in allowed_names if name}

    if not allowed_names:
        return False

    top_name = _candidate_text(state.top_candidates[0], "name")

    return not (top_name and top_name not in explanation)


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
        "Ты только кратко объясняешь уже готовую рекомендацию. "
        "Если список кандидатов ограничен Plane members, нельзя упоминать людей "
        "вне этого списка."
    )

    try:
        client = OllamaClient()
        explanation = client.generate(
            prompt=build_prompt(state),
            system=system,
            temperature=0.1,
            max_tokens=450,
        )

        if _llm_explanation_is_valid(explanation=explanation, state=state):
            state.explanation = explanation
        else:
            state.add_error(
                "explanation_agent",
                "LLM explanation failed Plane scoped validation.",
            )
            state.explanation = fallback_explanation(state)

    except Exception as error:
        state.add_error("explanation_agent", str(error))
        state.explanation = fallback_explanation(state)

    return state