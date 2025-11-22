from __future__ import annotations

from typing import Optional

from core import MasterySample
from .adapters import QuizAdapterOutput, QAAdapterOutput


class Evaluator:
    """
    Evaluation logic to turn quiz and QA results into a MasterySample.

    It assumes that quiz and QA results have already been normalized by
    evaluation.adapters (i.e., the raw schema has been adapted).
    """

    def __init__(self, quiz_weight: float = 0.7, qa_weight: float = 0.3) -> None:
        """
        :param quiz_weight: weight assigned to the quiz score
        :param qa_weight:   weight assigned to the QA score

        If there is no QA result, only the quiz score will be used.
        """
        self.quiz_weight = quiz_weight
        self.qa_weight = qa_weight

    # --------------------------------------------------------------------- #
    #  Scoring functions
    # --------------------------------------------------------------------- #

    def evaluate_quiz(self, quiz: QuizAdapterOutput) -> float:
        """
        Compute a [0, 1] score for a single quiz attempt.

        Default implementation:
        - score = accuracy * difficulty_factor

        You can extend this to consider per-question difficulty, response time,
        concept tags, etc., if needed.
        """
        questions = quiz.questions
        if not questions:
            return 0.0

        correct = sum(1 for q in questions if q.get("is_correct"))
        base_score = correct / len(questions)

        difficulty_factor = {
            "easy": 0.9,
            "medium": 1.0,
            "hard": 1.1,
        }.get(quiz.difficulty, 1.0)

        score = base_score * difficulty_factor
        return max(0.0, min(score, 1.0))

    def evaluate_qa(self, qa: Optional[QAAdapterOutput]) -> Optional[float]:
        """
        Compute a [0, 1] score for an open-ended QA response.

        For now, this simply returns qa.llm_score (already assumed to be
        normalized). If qa is None, returns None.
        """
        if qa is None:
            return None
        return max(0.0, min(qa.llm_score, 1.0))

    # --------------------------------------------------------------------- #
    #  Fusion into MasterySample
    # --------------------------------------------------------------------- #

    def build_mastery_sample(
        self,
        quiz: QuizAdapterOutput,
        qa: Optional[QAAdapterOutput] = None,
    ) -> MasterySample:
        """
        Combine quiz and QA signals into a single MasterySample.

        If qa is not provided, only the quiz score is used.
        """
        quiz_score = self.evaluate_quiz(quiz)
        qa_score = self.evaluate_qa(qa)

        if qa_score is not None:
            raw_mastery = self.quiz_weight * quiz_score + self.qa_weight * qa_score
        else:
            raw_mastery = quiz_score

        raw_mastery = max(0.0, min(raw_mastery, 1.0))

        return MasterySample(
            user_id=quiz.user_id,
            topic_id=quiz.topic_id,
            timestamp=quiz.timestamp,
            mastery_observation=raw_mastery,
            num_questions=len(quiz.questions),
            difficulty=quiz.difficulty,
        )
