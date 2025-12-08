from __future__ import annotations

from typing import List, Tuple

from core import MasterySample
from memory import Storage


class ProgressTracker:
    """
    Tracks learner progress over time and computes mastery levels.

    Responsibilities:
    - Store new MasterySample observations via the storage layer.
    - Compute current topic-level mastery (e.g., using an EMA).
    - Compute overall mastery across all topics.
    - Produce learning curves for visualization.
    """

    def __init__(self, storage: Storage, alpha: float = 0.6) -> None:
        """
        :param storage: underlying storage implementation
        :param alpha:   EMA coefficient, higher means more weight on recent data
        """
        self.storage = storage
        self.alpha = alpha

    # --------------------------------------------------------------------- #
    #  Recording
    # --------------------------------------------------------------------- #

    def record_mastery_sample(self, sample: MasterySample) -> None:
        """
        Append a new mastery observation to storage.
        """
        self.storage.append_mastery_sample(sample)

    # --------------------------------------------------------------------- #
    #  Mastery computation
    # --------------------------------------------------------------------- #

    def compute_topic_mastery(self, user_id: str, topic_id: str) -> float:
        """
        Compute current mastery level for a specific topic using EMA.

        If no samples exist, returns 0.0.
        """
        samples = self.storage.get_samples(user_id=user_id, topic_id=topic_id)
        if not samples:
            return 0.0

        # Sort by timestamp in case storage does not guarantee ordering.
        samples = sorted(samples, key=lambda s: s.timestamp)

        m = samples[0].score
        for s in samples[1:]:
            obs = s.score
            m = self.alpha * obs + (1.0 - self.alpha) * m

        return m

    def compute_overall_mastery(self, user_id: str) -> float:
        """
        Compute an overall mastery score across all topics for a user.

        This is simply the mean of all topic-level mastery values.
        """
        topic_ids = self.storage.get_topics(user_id)
        if not topic_ids:
            return 0.0

        values = [self.compute_topic_mastery(user_id, t) for t in topic_ids]
        if not values:
            return 0.0
        return sum(values) / len(values)

    # --------------------------------------------------------------------- #
    #  Learning curves
    # --------------------------------------------------------------------- #

    def get_learning_curve(
        self,
        user_id: str,
        topic_id: str,
    ) -> List[Tuple[str, float]]:
        """
        Return a list of (timestamp, mastery_value) pairs for a topic.

        The mastery_value is computed incrementally using EMA to produce
        a smoother curve for visualization.
        """
        samples = self.storage.get_samples(user_id=user_id, topic_id=topic_id)
        if not samples:
            return []

        samples = sorted(samples, key=lambda s: s.timestamp)

        curve: List[Tuple[str, float]] = []
        m = samples[0].score
        curve.append((samples[0].timestamp, m))

        for s in samples[1:]:
            obs = s.score
            m = self.alpha * obs + (1.0 - self.alpha) * m
            curve.append((s.timestamp, m))

        return curve
