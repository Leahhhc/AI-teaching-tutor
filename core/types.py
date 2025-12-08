from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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
    timestamp: datetime
    score: float  # value in [0, 1]
    num_questions: Optional[int] = None
    difficulty: Optional[str] = None  # "easy" / "medium" / "hard"

    def __post_init__(self):
        """Validate the mastery sample"""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"Score must be between 0 and 1, got {self.score}")
        if self.difficulty and self.difficulty not in ["easy", "medium", "hard"]:
            raise ValueError(f"Difficulty must be easy/medium/hard, got {self.difficulty}")