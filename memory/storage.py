from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict, Dict, List

from core import MasterySample


class Storage:
    """
    Very simple in-memory storage for mastery samples.

    Data layout:
        _data[user_id][topic_id] = [MasterySample, MasterySample, ...]
    """

    def __init__(self) -> None:
        self._data: DefaultDict[str, DefaultDict[str, List[MasterySample]]] = (
            defaultdict(lambda: defaultdict(list))
        )

    # --------------------------------------------------------------------- #
    #  Write operations
    # --------------------------------------------------------------------- #

    def append_mastery_sample(self, sample: MasterySample) -> None:
        """
        Append a single MasterySample to the in-memory store.
        """
        user_id = sample.user_id
        topic_id = sample.topic_id
        self._data[user_id][topic_id].append(sample)

    # --------------------------------------------------------------------- #
    #  Read operations
    # --------------------------------------------------------------------- #

    def get_samples(self, user_id: str, topic_id: str) -> List[MasterySample]:
        """
        Return all samples for a given user and topic.

        The insertion order is preserved, but callers may still want to sort
        by timestamp explicitly if they rely on chronological order.
        """
        return list(self._data[user_id][topic_id])

    def get_topics(self, user_id: str) -> List[str]:
        """
        Return all topic_ids that have at least one sample for the user.
        """
        return list(self._data[user_id].keys())
