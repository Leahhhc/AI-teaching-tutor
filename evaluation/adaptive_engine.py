from __future__ import annotations

from typing import Any, Dict

from memory import Storage
from .progress_tracker import ProgressTracker


class AdaptiveEngine:
    """
    Adaptive policy that proposes the next learning step for a learner.

    It uses topic-level mastery estimates from ProgressTracker and produces
    high-level actions such as:
        - which topic to focus on next
        - which difficulty level to use
        - what type of activity to perform
    """

    def __init__(
        self,
        storage: Storage,
        tracker: ProgressTracker,
        low_threshold: float = 0.4,
        mid_threshold: float = 0.7,
    ) -> None:
        """
        :param storage:       storage layer used to query topics
        :param tracker:       ProgressTracker instance
        :param low_threshold: below this mastery, treat as weak topic
        :param mid_threshold: above this mastery, treat as strong topic
        """
        self.storage = storage
        self.tracker = tracker
        self.low = low_threshold
        self.mid = mid_threshold

    # --------------------------------------------------------------------- #
    #  Internal helpers
    # --------------------------------------------------------------------- #

    def _get_topic_masteries(self, user_id: str) -> Dict[str, float]:
        """
        Return a mapping from topic_id to mastery score for the given user.
        """
        topic_ids = self.storage.get_topics(user_id)
        return {t: self.tracker.compute_topic_mastery(user_id, t) for t in topic_ids}

    # --------------------------------------------------------------------- #
    #  Public API
    # --------------------------------------------------------------------- #

    def suggest_next_step(self, user_id: str) -> Dict[str, Any]:
        """
        Suggest the next learning step for a user.

        The output dictionary is intentionally simple and model-agnostic so that
        the orchestration layer can interpret it and decide which agent to call.

        Example return value:
            {
                "next_topic_id": "logistic_regression",
                "difficulty": "medium",
                "action_type": "quiz_with_explanation"
            }
        """
        topic_masteries = self._get_topic_masteries(user_id)

        # New user: no history available. Let the orchestration layer decide
        # how to map "FIRST_TOPIC" to an actual syllabus unit.
        if not topic_masteries:
            return {
                "next_topic_id": "FIRST_TOPIC",
                "difficulty": "easy",
                "action_type": "review",
            }

        # Choose the topic with the lowest mastery (focus on the weakest area).
        next_topic_id = min(topic_masteries, key=topic_masteries.get)
        m = topic_masteries[next_topic_id]

        if m < self.low:
            difficulty = "easy"
            action_type = "review_quiz"
        elif m < self.mid:
            difficulty = "medium"
            action_type = "quiz_with_explanation"
        else:
            difficulty = "hard"
            action_type = "summary_test"

        return {
            "next_topic_id": next_topic_id,
            "difficulty": difficulty,
            "action_type": action_type,
        }
