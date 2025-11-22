"""
High-level evaluation interface.

This package provides:
- Data adaptation from raw model outputs to internal structures.
- Evaluation logic to turn quiz/QA results into mastery observations.
- Progress tracking over time.
- A simple adaptive engine that proposes the next learning step.
"""

from core import MasterySample
from .adapters import (
    QuizAdapterOutput,
    QAAdapterOutput,
    adapt_quiz_result,
    adapt_qa_result,
)
from .evaluator import Evaluator
from .progress_tracker import ProgressTracker
from .adaptive_engine import AdaptiveEngine

__all__ = [
    "MasterySample",
    "QuizAdapterOutput",
    "QAAdapterOutput",
    "adapt_quiz_result",
    "adapt_qa_result",
    "Evaluator",
    "ProgressTracker",
    "AdaptiveEngine",
]
