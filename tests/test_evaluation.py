from __future__ import annotations

from evaluation import (
    Evaluator,
    ProgressTracker,
    AdaptiveEngine,
    adapt_quiz_result,
    adapt_qa_result,
)
from memory import Storage


def _make_dummy_raw_quiz(
    user_id: str = "u1",
    topic_id: str = "topicA",
    correct: int = 3,
    total: int = 5,
    difficulty: str = "medium",
) -> dict:
    """
    Construct a simple fake raw quiz result that matches the expectations
    of `adapt_quiz_result`.
    """
    questions = []
    for i in range(total):
        # First `correct` questions are correct, the rest are incorrect.
        questions.append({"is_correct": i < correct})

    return {
        "user_id": user_id,
        "topic_id": topic_id,
        "timestamp": "2025-01-01T00:00:00",
        "difficulty": difficulty,
        "questions": questions,
    }


def _make_dummy_raw_qa(
    user_id: str = "u1",
    topic_id: str = "topicA",
    llm_score: float = 0.8,
) -> dict:
    """
    Construct a simple fake raw QA result that matches the expectations
    of `adapt_qa_result`.
    """
    return {
        "user_id": user_id,
        "topic_id": topic_id,
        "timestamp": "2025-01-01T00:05:00",
        "llm_score": llm_score,
    }


def test_evaluator_quiz_score_basic():
    evaluator = Evaluator()

    raw_quiz_all_wrong = _make_dummy_raw_quiz(correct=0, total=5)
    raw_quiz_all_right = _make_dummy_raw_quiz(correct=5, total=5)

    quiz0 = adapt_quiz_result(raw_quiz_all_wrong)
    quiz1 = adapt_quiz_result(raw_quiz_all_right)

    score0 = evaluator.evaluate_quiz(quiz0)
    score1 = evaluator.evaluate_quiz(quiz1)

    assert 0.0 <= score0 <= 0.01
    assert 0.99 <= score1 <= 1.0
    assert score1 > score0


def test_evaluator_mastery_with_and_without_qa():
    evaluator = Evaluator(quiz_weight=0.5, qa_weight=0.5)

    raw_quiz = _make_dummy_raw_quiz(correct=3, total=5)
    raw_qa_good = _make_dummy_raw_qa(llm_score=0.9)

    quiz = adapt_quiz_result(raw_quiz)
    qa = adapt_qa_result(raw_qa_good)

    sample_with_qa = evaluator.build_mastery_sample(quiz, qa)
    sample_without_qa = evaluator.build_mastery_sample(quiz, None)

    assert sample_with_qa.score >= sample_without_qa.score


def test_progress_tracker_ema_increasing():
    storage = Storage()
    tracker = ProgressTracker(storage=storage, alpha=0.5)
    evaluator = Evaluator()

    # Three quiz attempts with increasing accuracy
    raw_quiz1 = _make_dummy_raw_quiz(correct=1, total=5)
    raw_quiz2 = _make_dummy_raw_quiz(correct=3, total=5)
    raw_quiz3 = _make_dummy_raw_quiz(correct=5, total=5)

    for raw in [raw_quiz1, raw_quiz2, raw_quiz3]:
        quiz = adapt_quiz_result(raw)
        sample = evaluator.build_mastery_sample(quiz, None)
        tracker.record_mastery_sample(sample)

    m = tracker.compute_topic_mastery(user_id="u1", topic_id="topicA")
    assert 0.0 < m <= 1.0


def test_adaptive_engine_focuses_on_weakest_topic():
    storage = Storage()
    tracker = ProgressTracker(storage=storage, alpha=0.5)
    evaluator = Evaluator()
    engine = AdaptiveEngine(storage=storage, tracker=tracker)

    # topicA is strong, topicB is weak
    raw_quiz_strong = _make_dummy_raw_quiz(
        user_id="u1", topic_id="topicA", correct=5, total=5
    )
    raw_quiz_weak = _make_dummy_raw_quiz(
        user_id="u1", topic_id="topicB", correct=1, total=5
    )

    for _ in range(3):
        quiz = adapt_quiz_result(raw_quiz_strong)
        sample = evaluator.build_mastery_sample(quiz, None)
        tracker.record_mastery_sample(sample)

    for _ in range(3):
        quiz = adapt_quiz_result(raw_quiz_weak)
        sample = evaluator.build_mastery_sample(quiz, None)
        tracker.record_mastery_sample(sample)

    suggestion = engine.suggest_next_step(user_id="u1")
    assert suggestion["next_topic_id"] == "topicB"
