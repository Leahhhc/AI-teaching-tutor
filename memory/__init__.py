"""
Memory module: persistence abstraction for learner state.

The current implementation is an in-memory storage class that is sufficient
for demos and unit tests. It can be replaced with a database-backed version
without affecting the evaluation logic.
"""

from .storage import Storage

__all__ = ["Storage"]
