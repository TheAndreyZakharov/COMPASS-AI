from __future__ import annotations

import json
from typing import Any

from src.agents.state import AgentState
from src.llm.ollama_client import OllamaClient, ollama_available


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
        "- модель оценила совпадение задачи, профиля сотрудника и pair features;",
        "- учтены skill match, риск, загрузка, скорость и надёжность;",
        "- итоговый ranking сформирован до LLM-объяснения.",
    ]

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
        "top_candidates": candidates,
    }

    return (
        "Сформируй краткое объяснение рекомендации на русском языке.\n"
        "Нельзя менять ranking кандидатов.\n"
        "Нельзя придумывать факты, которых нет во входных данных.\n"
        "Нужно объяснить top-1, риски и альтернативы.\n"
        "Структура: рекомендованный исполнитель, почему подходит, риски, альтернативы.\n\n"
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
        "Ты только кратко объясняешь уже готовую рекомендацию."
    )

    try:
        client = OllamaClient()
        state.explanation = client.generate(
            prompt=build_prompt(state),
            system=system,
            temperature=0.2,
            max_tokens=450,
        )
    except Exception as error:
        state.add_error("explanation_agent", str(error))
        state.explanation = fallback_explanation(state)

    return state