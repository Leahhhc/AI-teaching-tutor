from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MasterySample:
    """
    A single observation of the learner's mastery on a specific topic.

    This is the canonical internal format used by:
    - evaluation.progress_tracker
    - evaluation.adaptive_engine
    - memory.storage

    All external raw data (e.g. quiz results, QA grading) should eventually
    be converted into this format (or aggregated into it).
    """

    user_id: str
    topic_id: str
    timestamp: str  # ISO8601-like string, good enough for this project
    mastery_observation: float  # value in [0, 1]
    num_questions: int
    difficulty: str  # "easy" / "medium" / "hard"
