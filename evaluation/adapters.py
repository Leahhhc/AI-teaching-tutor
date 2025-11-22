from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class QuizAdapterOutput:
    """
    Normalized view of a quiz result.

    This is an intermediate representation between the raw quiz agent output
    and the Evaluator. The goal is to isolate schema changes of the upstream
    quiz agent: if the raw format changes, we only need to update this file.
    """

    user_id: str
    topic_id: str
    timestamp: str
    difficulty: str
    questions: List[Dict[str, Any]]
    # Each question dict should at least contain:
    #   - "is_correct": bool
    # Optionally you may include extra fields such as:
    #   - "concept_tags": List[str]
    #   - "response_time": float


@dataclass
class QAAdapterOutput:
    """
    Normalized view of a graded open-ended QA interaction.

    The current project only requires an overall score (llm_score) in [0, 1],
    but you can extend this structure with fields like:
    - rubric
    - feedback_text
    if you want more detailed analysis later.
    """

    user_id: str
    topic_id: str
    timestamp: str
    llm_score: float


def adapt_quiz_result(raw_quiz: Dict[str, Any]) -> QuizAdapterOutput:
    """
    Adapt the raw quiz result into QuizAdapterOutput.

    IMPORTANT:
    - This is the ONLY place that should know about the raw quiz schema.
    - When the quiz agent output changes schema, you should only modify this
      function instead of touching the evaluation logic.

    For now we assume a relatively simple raw format:
        {
            "user_id": "...",              # or "user": {"id": "..."}
            "topic_id": "...",
            "timestamp": "...",
            "difficulty": "easy|medium|hard",
            "questions": [
                {"is_correct": true, ...},
                {"is_correct": false, ...},
                ...
            ]
        }

    Adjust the field extraction below to match the actual upstream output.
    """

    # Try a few common patterns to keep this robust.
    user_id = raw_quiz.get("user_id")
    if user_id is None and "user" in raw_quiz:
        user = raw_quiz["user"]
        if isinstance(user, dict):
            user_id = user.get("id")

    if user_id is None:
        raise KeyError("Cannot extract user_id from raw_quiz")

    topic_id = raw_quiz["topic_id"]
    timestamp = raw_quiz.get("timestamp", "")

    difficulty = raw_quiz.get("difficulty", "medium")
    questions: List[Dict[str, Any]] = raw_quiz.get("questions", [])

    return QuizAdapterOutput(
        user_id=user_id,
        topic_id=topic_id,
        timestamp=timestamp,
        difficulty=difficulty,
        questions=questions,
    )


def adapt_qa_result(raw_qa: Optional[Dict[str, Any]]) -> Optional[QAAdapterOutput]:
    """
    Adapt the raw QA evaluation result into QAAdapterOutput.

    If raw_qa is None or does not contain enough information, this returns None,
    and the evaluator will simply ignore the QA component.
    """

    if raw_qa is None:
        return None

    user_id = raw_qa.get("user_id")
    topic_id = raw_qa.get("topic_id")
    timestamp = raw_qa.get("timestamp", "")
    llm_score = raw_qa.get("llm_score")

    if user_id is None or topic_id is None or llm_score is None:
        # Data is incomplete; treat as "no QA signal"
        return None

    score = float(llm_score)
    # Clip the score into [0, 1] to be safe
    score = max(0.0, min(score, 1.0))

    return QAAdapterOutput(
        user_id=user_id,
        topic_id=topic_id,
        timestamp=timestamp,
        llm_score=score,
    )
