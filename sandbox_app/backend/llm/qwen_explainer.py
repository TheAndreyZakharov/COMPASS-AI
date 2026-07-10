from __future__ import annotations

import json
import re
from typing import Any

from sandbox_app.backend.llm.ollama_client import OllamaClient, OllamaClientError

MAX_CANDIDATES_FOR_PROMPT = 5
MAX_ASSIGNMENTS_FOR_PROMPT = 20


class ExplanationError(ValueError):
    """Raised when explanation payload is invalid."""


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default

    if numeric != numeric:
        return default

    return numeric


def safe_text(value: Any) -> str:
    return str(value or "").strip()


def explanation_text(value: Any) -> str:
    if isinstance(value, list):
        lines: list[str] = []

        for item in value:
            if isinstance(item, dict):
                text = (
                    item.get("message")
                    or item.get("text")
                    or item.get("explanation")
                    or item.get("summary")
                )
                if text:
                    lines.append(f"- {safe_text(text)}")
                    continue

                details = [
                    f"{key}: {safe_text(raw_value)}"
                    for key, raw_value in item.items()
                    if safe_text(raw_value)
                ]
                if details:
                    lines.append(f"- {', '.join(details)}")
            else:
                text = safe_text(item)
                if text:
                    lines.append(f"- {text}")

        return "\n".join(lines).strip()

    if isinstance(value, dict):
        lines = [
            f"{key}: {safe_text(raw_value)}"
            for key, raw_value in value.items()
            if safe_text(raw_value)
        ]
        return "\n".join(lines).strip()

    return safe_text(value)


def candidate_label(candidate: dict[str, Any]) -> str:
    name = safe_text(candidate.get("name"))
    employee_id = safe_text(candidate.get("employee_id"))

    if name and employee_id:
        return f"{name} ({employee_id})"

    return name or employee_id or "кандидат"


def allowed_candidate_tokens(candidates: list[dict[str, Any]]) -> set[str]:
    tokens: set[str] = set()

    for candidate in candidates:
        employee_id = safe_text(candidate.get("employee_id"))
        name = safe_text(candidate.get("name"))

        if employee_id:
            tokens.add(employee_id)

        if name:
            tokens.add(name)

    return tokens


def compact_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    factors = candidate.get("factors") or {}
    risks = candidate.get("risks") or []
    snapshot = candidate.get("employee_snapshot") or {}

    return {
        "employee_id": candidate.get("employee_id"),
        "name": candidate.get("name"),
        "role": candidate.get("role"),
        "grade": candidate.get("grade"),
        "score": candidate.get("score"),
        "model_score": candidate.get("model_score"),
        "matched_skills": candidate.get("matched_skills", []),
        "missing_skills": candidate.get("missing_skills", []),
        "factors": {
            "skill_match_ratio": factors.get("skill_match_ratio"),
            "quality_fit_score": factors.get("quality_fit_score"),
            "speed_fit_score": factors.get("speed_fit_score"),
            "learning_fit_score": factors.get("learning_fit_score"),
            "risk_fit_score": factors.get("risk_fit_score"),
            "workload_pressure": factors.get("workload_pressure"),
            "fatigue_risk": factors.get("fatigue_risk"),
            "availability_gap": factors.get("availability_gap"),
        },
        "employee_snapshot": {
            "current_workload": snapshot.get("current_workload"),
            "fatigue_score": snapshot.get("fatigue_score"),
            "availability_score": snapshot.get("availability_score"),
            "avg_quality_score": snapshot.get("avg_quality_score"),
            "avg_completion_speed": snapshot.get("avg_completion_speed"),
            "deadline_reliability": snapshot.get("deadline_reliability"),
        },
        "risks": [
            {
                "type": risk.get("type"),
                "level": risk.get("level"),
                "message": risk.get("message"),
            }
            for risk in risks[:5]
            if isinstance(risk, dict)
        ],
    }


def compact_recommendation(recommendation: dict[str, Any]) -> dict[str, Any]:
    candidates = recommendation.get("candidates") or []
    task = recommendation.get("task") or {}

    if not isinstance(candidates, list):
        raise ExplanationError("recommendation.candidates must be list")

    return {
        "task": {
            "task_id": task.get("task_id"),
            "title": task.get("title"),
            "priority": task.get("priority"),
            "complexity": task.get("complexity"),
            "estimated_hours": task.get("estimated_hours"),
            "required_skills": task.get("required_skills", []),
        },
        "recommendation_mode": recommendation.get("recommendation_mode"),
        "model_name": recommendation.get("model_name"),
        "candidates": [
            compact_candidate(candidate)
            for candidate in candidates[:MAX_CANDIDATES_FOR_PROMPT]
            if isinstance(candidate, dict)
        ],
    }


def fallback_candidate_reason(candidate: dict[str, Any], rank: int) -> str:
    factors = candidate.get("factors") or {}
    matched = candidate.get("matched_skills") or []
    missing = candidate.get("missing_skills") or []
    risks = candidate.get("risks") or []

    skill_match = to_float(factors.get("skill_match_ratio"))
    quality = to_float(factors.get("quality_fit_score"))
    speed = to_float(factors.get("speed_fit_score"))
    risk_fit = to_float(factors.get("risk_fit_score"))

    risk_messages = [
        safe_text(risk.get("message"))
        for risk in risks
        if isinstance(risk, dict) and risk.get("message")
    ]
    risk_text = " ".join(risk_messages[:2]) or "Критичных рисков не обнаружено."

    return (
        f"{rank}. {candidate_label(candidate)}: score {to_float(candidate.get('score')):.3f}. "
        f"Навыки совпадают на {skill_match:.0%}, качество {quality:.0%}, "
        f"скорость {speed:.0%}, risk fit {risk_fit:.0%}. "
        f"Совпавшие навыки: {', '.join(matched) if matched else 'нет'}. "
        f"Недостающие навыки: {', '.join(missing) if missing else 'нет'}. "
        f"Риски: {risk_text}"
    )


def fallback_recommendation_explanation(
    recommendation: dict[str, Any],
    reason: str = "",
) -> dict[str, Any]:
    candidates = recommendation.get("candidates") or []
    task = recommendation.get("task") or {}
    top_candidates = [
        candidate
        for candidate in candidates[:MAX_CANDIDATES_FOR_PROMPT]
        if isinstance(candidate, dict)
    ]

    candidate_lines = [
        fallback_candidate_reason(candidate, index + 1)
        for index, candidate in enumerate(top_candidates)
    ]

    task_title = safe_text(task.get("title")) or safe_text(task.get("task_id")) or "задача"
    explanation = (
        f"Для задачи «{task_title}» модель уже рассчитала ranking, "
        "а это объяснение только описывает готовый результат. "
        + " ".join(candidate_lines)
    )

    return {
        "status": "fallback",
        "language": "ru",
        "ranking_source": "model_output_unchanged",
        "llm_used": False,
        "reason": reason,
        "summary": explanation,
        "candidate_explanations": candidate_lines,
    }


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()

    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?", "", stripped, flags=re.IGNORECASE).strip()
        stripped = re.sub(r"```$", "", stripped).strip()

    start = stripped.find("{")
    end = stripped.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ExplanationError("LLM response does not contain JSON object")

    try:
        parsed = json.loads(stripped[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ExplanationError("LLM response JSON is invalid") from exc

    if not isinstance(parsed, dict):
        raise ExplanationError("LLM response must be JSON object")

    return parsed


def validate_candidate_references(
    parsed: dict[str, Any],
    candidates: list[dict[str, Any]],
) -> None:
    allowed_ids = {
        safe_text(candidate.get("employee_id"))
        for candidate in candidates
        if safe_text(candidate.get("employee_id"))
    }
    candidate_explanations = parsed.get("candidate_explanations", [])

    if not isinstance(candidate_explanations, list):
        raise ExplanationError("candidate_explanations must be list")

    for item in candidate_explanations:
        if not isinstance(item, dict):
            raise ExplanationError("candidate explanation item must be object")

        employee_id = safe_text(item.get("employee_id"))
        if employee_id not in allowed_ids:
            raise ExplanationError(f"LLM mentioned unknown employee_id: {employee_id}")

    mentioned_ids = {
        safe_text(item.get("employee_id"))
        for item in candidate_explanations
        if isinstance(item, dict)
    }

    if not mentioned_ids:
        raise ExplanationError("LLM did not explain any allowed candidate")


def recommendation_prompt(recommendation: dict[str, Any]) -> str:
    compact = compact_recommendation(recommendation)

    return (
        "Объясни готовую рекомендацию на русском языке. "
        "Нельзя менять ranking, score, кандидатов, навыки или риски. "
        "Нельзя придумывать новых кандидатов, новые навыки или новые факты. "
        "Используй только JSON ниже. "
        "Пиши как опытный руководитель/аналитик, который объясняет назначение задачи человеку: "
        "живым языком, но строго по фактам и метрикам из JSON. "
        "Обязательно используй конкретные числа score, model_score, skill_match_ratio, "
        "quality_fit_score, speed_fit_score, workload_pressure, fatigue_score, "
        "availability_score и риски, если они есть. "
        "Не просто перечисляй метрики: коротко объясняй, что каждая важная цифра значит "
        "для этой задачи, почему кандидат подходит, где слабые места и чем он отличается "
        "от соседних кандидатов в ranking. "
        "Верни строго JSON object с полями: summary, candidate_explanations, risks_note. "
        "candidate_explanations должен быть массивом объектов с полями "
        "employee_id, explanation, strengths, concerns. "
        "employee_id должен быть только из входных candidates. "
        "summary — 4-6 предложений: общий вывод, почему top-1 выбран, "
        "какой есть компромисс по нагрузке/риску и на что обратить внимание. "
        "explanation — 4-6 предложений по каждому кандидату: роль, совпадение навыков, "
        "качество, скорость, нагрузка, усталость/доступность, риски и итоговый смысл этих цифр. "
        "strengths и concerns — списки из 2-4 строк каждый; в строках тоже указывай числа, "
        "если число есть во входных данных. concerns не должен быть Python/JSON object, "
        "только обычные человеческие строки. "
        "В строковых значениях можно использовать короткие markdown-списки, "
        "но весь ответ всё равно должен быть валидным JSON.\n\n"
        f"{json.dumps(compact, ensure_ascii=False, indent=2)}"
    )


def normalize_llm_explanation(
    parsed: dict[str, Any],
    recommendation: dict[str, Any],
    model_name: str,
) -> dict[str, Any]:
    candidates = recommendation.get("candidates") or []
    validate_candidate_references(parsed, candidates)

    summary = explanation_text(parsed.get("summary"))
    risks_note = explanation_text(parsed.get("risks_note"))
    candidate_explanations = parsed.get("candidate_explanations", [])

    if not summary:
        raise ExplanationError("LLM summary is empty")

    normalized_candidates: list[dict[str, Any]] = []
    for item in candidate_explanations:
        if not isinstance(item, dict):
            continue

        normalized_candidates.append(
            {
                **item,
                "explanation": explanation_text(item.get("explanation")),
                "strengths": item.get("strengths", []),
                "concerns": item.get("concerns", []),
            }
        )

    return {
        "status": "ok",
        "language": "ru",
        "ranking_source": "model_output_unchanged",
        "llm_used": True,
        "llm_model": model_name,
        "summary": summary,
        "risks_note": risks_note,
        "candidate_explanations": normalized_candidates,
    }


def explain_recommendation(
    recommendation: dict[str, Any],
    use_llm: bool = True,
    client: OllamaClient | None = None,
) -> dict[str, Any]:
    candidates = recommendation.get("candidates") or []

    if not isinstance(candidates, list) or not candidates:
        raise ExplanationError("recommendation.candidates must be non-empty list")

    if not use_llm:
        return fallback_recommendation_explanation(
            recommendation,
            reason="LLM explanations disabled",
        )

    ollama = client or OllamaClient()
    system = (
        "Ты объясняешь результаты ML ranking. "
        "Ты не принимаешь решений и не меняешь порядок кандидатов. "
        "Отвечай только валидным JSON. Не добавляй текст вне JSON."
    )

    try:
        generated = ollama.generate(
            prompt=recommendation_prompt(recommendation),
            system=system,
            temperature=0.15,
        )
        parsed = extract_json_object(generated.response)
        return normalize_llm_explanation(
            parsed=parsed,
            recommendation=recommendation,
            model_name=generated.model,
        )
    except (OllamaClientError, ExplanationError) as exc:
        return fallback_recommendation_explanation(recommendation, reason=str(exc))


def compact_assignment_session(session: dict[str, Any]) -> dict[str, Any]:
    assigned = session.get("assigned_tasks") or []
    unassigned = session.get("unassigned_tasks") or []

    return {
        "assignment_session_id": session.get("assignment_session_id"),
        "assignment_mode": session.get("assignment_mode"),
        "recommendation_mode": session.get("recommendation_mode"),
        "model_name": session.get("model_name"),
        "summary": session.get("summary", {}),
        "fairness_report": session.get("fairness_report", {}),
        "assigned_tasks": assigned[:MAX_ASSIGNMENTS_FOR_PROMPT],
        "unassigned_tasks": unassigned[:MAX_ASSIGNMENTS_FOR_PROMPT],
        "workload_after_assignment": session.get("workload_after_assignment", []),
    }


def fallback_assignment_explanation(
    assignment_session: dict[str, Any],
    reason: str = "",
) -> dict[str, Any]:
    summary = assignment_session.get("summary") or {}
    fairness = assignment_session.get("fairness_report") or {}
    assigned = summary.get("assigned_tasks", 0)
    unassigned = summary.get("unassigned_tasks", 0)
    spread = fairness.get("assignment_spread", 0)
    max_workload = fairness.get("max_projected_workload", 0)

    text = (
        "Bulk assignment уже выполнен моделью и optimizer, "
        "а это объяснение только описывает сохранённый результат. "
        f"Назначено задач: {assigned}. Неназначено задач: {unassigned}. "
        f"Разброс назначений между людьми: {spread}. "
        f"Максимальная прогнозная загрузка: {max_workload}."
    )

    return {
        "status": "fallback",
        "language": "ru",
        "ranking_source": "model_output_unchanged",
        "llm_used": False,
        "reason": reason,
        "summary": text,
        "fairness_note": text,
    }


def assignment_prompt(assignment_session: dict[str, Any]) -> str:
    compact = compact_assignment_session(assignment_session)

    return (
        "Объясни bulk assignment на русском языке. "
        "Нельзя менять назначения, ranking, score, людей, задачи или fairness metrics. "
        "Нельзя придумывать новых людей, задачи, навыки или причины. "
        "Используй только JSON ниже. "
        "Пиши как понятный аналитик: объясни подробнее, сколько задач назначено, "
        "сколько осталось без назначения, как распределилась нагрузка, где есть риски, "
        "какие числа это подтверждают и почему итог выглядит логичным. "
        "Верни строго JSON object с полями: summary, fairness_note, workload_note, "
        "unassigned_note, risks_note. "
        "Каждое непустое поле должно быть 3-5 предложений или короткий markdown-список "
        "с конкретными числами из JSON. "
        "В строковых значениях можно использовать короткие markdown-списки, "
        "но весь ответ всё равно должен быть валидным JSON.\n\n"
        f"{json.dumps(compact, ensure_ascii=False, indent=2)}"
    )


def explain_assignment_session(
    assignment_session: dict[str, Any],
    use_llm: bool = True,
    client: OllamaClient | None = None,
) -> dict[str, Any]:
    if not assignment_session.get("assignment_session_id"):
        raise ExplanationError("assignment_session_id is required")

    if not use_llm:
        return fallback_assignment_explanation(
            assignment_session,
            reason="LLM explanations disabled",
        )

    ollama = client or OllamaClient()
    system = (
        "Ты объясняешь сохранённый результат batch assignment. "
        "Ты не меняешь назначения, порядок, score и fairness metrics. "
        "Отвечай только валидным JSON. Не добавляй текст вне JSON."
    )

    try:
        generated = ollama.generate(
            prompt=assignment_prompt(assignment_session),
            system=system,
            temperature=0.15,
        )
        parsed = extract_json_object(generated.response)
        summary = explanation_text(parsed.get("summary"))

        if not summary:
            raise ExplanationError("LLM summary is empty")

        return {
            "status": "ok",
            "language": "ru",
            "ranking_source": "model_output_unchanged",
            "llm_used": True,
            "llm_model": generated.model,
            "summary": summary,
            "fairness_note": explanation_text(parsed.get("fairness_note")),
            "workload_note": explanation_text(parsed.get("workload_note")),
            "unassigned_note": explanation_text(parsed.get("unassigned_note")),
            "risks_note": explanation_text(parsed.get("risks_note")),
        }
    except (OllamaClientError, ExplanationError) as exc:
        return fallback_assignment_explanation(assignment_session, reason=str(exc))
