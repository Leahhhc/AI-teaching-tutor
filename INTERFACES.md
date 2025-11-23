# Module Interface Specification (Updated for Week 2)

## Overview

This project uses a **data-driven architecture** with standardized internal formats:
- All evaluation data flows through `MasterySample` (defined in `core/types.py`)
- External formats are converted via **adapters** (`evaluation/adapters.py`)
- This design decouples upstream changes (B's quiz format) from evaluation logic (C's code)

---

## Core Data Types

### MasterySample (defined in `core/types.py`)
```python
@dataclass
class MasterySample:
    """
    Canonical internal format for a single mastery observation
    """
    user_id: str
    topic_id: str
    timestamp: str          # ISO8601 format
    mastery_observation: float  # 0-1
    num_questions: int
    difficulty: str         # "easy" / "medium" / "hard"
```

---

## B's Interface (LLM Content Processing)

### 1. `parsers/lecture_parser.py`

```python
class LectureParser:
    """
    Owner: B
    Purpose: Parse course material files
    Status: MOCK for Week 2
    """
    
    def parse(self, file_path: str) -> dict:
        """
        Parse course material
        
        Args:
            file_path: File path (supports .txt, .pdf)
        
        Returns:
            {
                'title': str,
                'chapters': [
                    {
                        'id': str,
                        'name': str,
                        'content': str,
                        'key_concepts': List[str]
                    }
                ]
            }
        
        Raises:
            FileNotFoundError: File does not exist
            ValueError: File format not supported
        """
        pass
```

### 2. `agents/tutor_agent.py`

```python
class TutorAgent:
    """
    Owner: B
    Purpose: Teaching explanation and Q&A
    Status: MOCK for Week 2
    
    NOTE: All methods should return dummy text for Week 2.
    """
    
    def __init__(self):
        """Initialize agent (no API needed for mock)"""
        pass
    
    def explain_concept(self, concept: str, difficulty: int, context: str = "") -> str:
        """
        Explain a concept with adaptive difficulty
        
        Args:
            concept: Concept name
            difficulty: Difficulty level 1-5 (from adaptive engine or default)
            context: Related course material content (optional)
        
        Returns:
            Explanation text (can be dummy text for Week 2)
            
        Example:
            "This is a mock explanation for {concept} at difficulty {difficulty}"
        """
        pass
    
    def answer_question(self, question: str, course_context: str = "") -> str:
        """
        Answer student questions
        
        Args:
            question: Student's question
            course_context: Related course material (optional)
        
        Returns:
            Answer text (can be dummy text for Week 2)
            
        Example:
            "This is a mock answer to: {question}"
        """
        pass
```

### 3. `agents/quiz_agent.py`

```python
class QuizAgent:
    """
    Owner: B
    Purpose: Generate quiz questions
    Status: MOCK for Week 2
    
    NOTE: Should return data matching the format below.
    """
    
    def __init__(self):
        pass
    
    def generate_quiz(self, topic: str, difficulty: int, num_questions: int = 5, 
                     context: str = "") -> dict:
        """
        Generate quiz with adaptive difficulty
        
        Args:
            topic: Quiz topic
            difficulty: Difficulty 1-5 (from adaptive engine or default)
            num_questions: Number of questions (default: 5)
            context: Course material context (optional)
        
        Returns:
            {
                'quiz_id': str,
                'topic': str,
                'difficulty': int,
                'questions': [
                    {
                        'question_id': str,
                        'question': str,
                        'options': List[str],
                        'correct_answer': str,
                        'explanation': str
                    }
                ]
            }
        
        Example mock return:
            {
                'quiz_id': 'mock_quiz_123',
                'topic': topic,
                'difficulty': difficulty,
                'questions': [
                    {
                        'question_id': 'q1',
                        'question': f'Mock question about {topic}',
                        'options': ['A', 'B', 'C', 'D'],
                        'correct_answer': 'A',
                        'explanation': 'Mock explanation'
                    }
                ] * num_questions
            }
        """
        pass
```

---

## C's Interface (Learning Evaluation & Adaptive Logic)

### 1. `evaluation/evaluator.py`

```python
class Evaluator:
    """
    Owner: C
    Purpose: Evaluate quiz/QA results and produce MasterySample
    Status: IMPLEMENTED
    """
    
    def __init__(self, quiz_weight: float = 0.7, qa_weight: float = 0.3):
        """
        Initialize evaluator with weights for quiz and QA components
        
        Args:
            quiz_weight: Weight for quiz score (default 0.7)
            qa_weight: Weight for QA score (default 0.3)
        """
        self.quiz_weight = quiz_weight
        self.qa_weight = qa_weight
    
    def evaluate_quiz(self, quiz: QuizAdapterOutput) -> float:
        """
        Compute score for a quiz (0-1)
        
        Args:
            quiz: QuizAdapterOutput from adapter
        
        Returns:
            Score in range [0, 1]
            
        Implementation:
            - Basic: correct_count / total_questions
            - Can be enhanced with difficulty weighting
        """
        pass
    
    def build_mastery_sample(
        self,
        quiz: QuizAdapterOutput,
        qa: Optional[QAAdapterOutput] = None
    ) -> MasterySample:
        """
        Convert quiz (and optional QA) into MasterySample
        
        Args:
            quiz: Adapted quiz result (required)
            qa: Adapted QA result (optional, for future use)
        
        Returns:
            MasterySample for storage
            
        Process:
            1. Compute quiz score using evaluate_quiz()
            2. If qa exists, compute qa score
            3. Combine scores with weights
            4. Build MasterySample with all metadata
        """
        pass
```

### 2. `evaluation/progress_tracker.py`

```python
class ProgressTracker:
    """
    Owner: C
    Purpose: Track learning progress using EMA (Exponential Moving Average)
    Status: IMPLEMENTED
    """
    
    def __init__(self, storage: Storage, alpha: float = 0.6):
        """
        Initialize progress tracker
        
        Args:
            storage: Storage instance
            alpha: EMA coefficient (higher = more weight on recent data)
                   Typical range: 0.3-0.7
        """
        self.storage = storage
        self.alpha = alpha
    
    def record_mastery_sample(self, sample: MasterySample) -> None:
        """
        Store a mastery observation
        
        Args:
            sample: MasterySample to record
            
        Side effects:
            - Appends sample to storage
            - Updates user's topic list
        """
        pass
    
    def compute_topic_mastery(self, user_id: str, topic_id: str) -> float:
        """
        Compute current mastery level for a topic using EMA
        
        Args:
            user_id: User ID
            topic_id: Topic ID
        
        Returns:
            Mastery level 0-1 (returns 0.0 if no data exists)
            
        Algorithm:
            EMA = alpha * current_observation + (1 - alpha) * previous_EMA
            Starting value = first observation
        """
        pass
    
    def compute_overall_mastery(self, user_id: str) -> float:
        """
        Compute overall mastery across all topics
        
        Args:
            user_id: User ID
        
        Returns:
            Mean mastery across all topics (0.0 if no topics)
            
        Implementation:
            Average of all topic masteries for the user
        """
        pass
    
    def get_learning_curve(self, user_id: str, topic_id: str) -> List[Tuple[str, float]]:
        """
        Get learning curve data for visualization (used by D's frontend)
        
        Args:
            user_id: User ID
            topic_id: Topic ID
        
        Returns:
            List of (timestamp, mastery_value) pairs, ordered chronologically
            Empty list if no data exists
            
        Example:
            [
                ('2024-01-15T10:30:00', 0.45),
                ('2024-01-15T14:20:00', 0.62),
                ('2024-01-16T09:15:00', 0.78)
            ]
            
        Note:
            This computes cumulative EMA at each timestamp, not just raw observations
        """
        pass
```

### 3. `evaluation/adaptive_engine.py`

```python
class AdaptiveEngine:
    """
    Owner: C
    Purpose: Recommend next learning steps and adaptive difficulty
    Status: IMPLEMENTED
    """
    
    def __init__(
        self,
        storage: Storage,
        tracker: ProgressTracker,
        low_threshold: float = 0.4,
        mid_threshold: float = 0.7
    ):
        """
        Initialize adaptive engine
        
        Args:
            storage: Storage instance
            tracker: ProgressTracker instance
            low_threshold: Below this = weak/struggling (needs easier content)
            mid_threshold: Above this = strong/mastered (needs harder content)
        """
        self.storage = storage
        self.tracker = tracker
        self.low = low_threshold
        self.mid = mid_threshold
    
    def suggest_next_step(self, user_id: str) -> Dict[str, Any]:
        """
        Suggest next learning activity based on weakest topic
        
        Args:
            user_id: User ID
        
        Returns:
            {
                "next_topic_id": str,          # Topic to study
                "difficulty": str,              # "easy" / "medium" / "hard"
                "action_type": str,             # "review_quiz" / "quiz_with_explanation" / etc
                "reason": str                   # Explanation (optional)
            }
            
        Algorithm:
            1. Get all topics for user
            2. Compute mastery for each topic
            3. Find weakest topic (lowest mastery)
            4. Recommend difficulty based on mastery level
            5. Recommend action type based on mastery
            
        Action Types:
            - mastery < 0.4: "review_basics" or "easy_quiz"
            - 0.4 <= mastery < 0.7: "practice_quiz"
            - mastery >= 0.7: "challenge_quiz" or "advanced_problems"
        """
        pass
    
    def get_adaptive_difficulty(self, user_id: str, topic_id: str) -> int:
        """
        Get recommended difficulty level for a topic based on current mastery
        
        Args:
            user_id: User ID
            topic_id: Topic ID
        
        Returns:
            Difficulty level 1-5:
                2: Easy (mastery < 0.4)
                3: Medium (0.4 <= mastery < 0.7)
                4: Hard (mastery >= 0.7)
            Returns 3 (medium) if no data exists
            
        Note:
            This is a RECOMMENDED addition to C's AdaptiveEngine to support
            the main application's need for numeric difficulty levels.
            C's existing suggest_next_step() returns difficulty as strings
            ("easy"/"medium"/"hard"), while B's agents expect integers (1-5).
            
        Implementation suggestion:
            ```python
            topics = self.storage.get_topics(user_id)
            if topic_id not in topics:
                return 3  # default medium
            
            mastery = self.tracker.compute_topic_mastery(user_id, topic_id)
            if mastery < self.low:
                return 2  # easy
            elif mastery < self.mid:
                return 3  # medium
            else:
                return 4  # hard
            ```
            
        Alternative (if not implemented by C):
            A's main.py can directly implement this logic inline.
        """
        pass
```

### 4. `evaluation/adapters.py`

```python
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class QuizAdapterOutput:
    """
    Standardized quiz result format (C's internal format)
    """
    user_id: str
    topic_id: str
    timestamp: str
    difficulty: str
    questions: List[Dict[str, Any]]  # List of {is_correct: bool, ...}
    num_questions: int

@dataclass
class QAAdapterOutput:
    """
    Standardized Q&A result format (for future use)
    """
    user_id: str
    topic_id: str
    timestamp: str
    question: str
    answer: str
    correctness: float  # 0-1 score

def adapt_quiz_result(raw_quiz: Dict[str, Any]) -> QuizAdapterOutput:
    """
    Convert raw quiz data to standardized format
    
    Args:
        raw_quiz: Raw quiz data with format:
            {
                'user_id': str,
                'topic_id': str,
                'timestamp': str (ISO8601),
                'difficulty': str,
                'questions': [
                    {'is_correct': bool},
                    ...
                ]
            }
    
    Returns:
        QuizAdapterOutput instance
        
    Purpose:
        If B changes quiz format, only this adapter needs updating.
        C's evaluation logic remains unchanged.
    """
    pass

def adapt_qa_result(raw_qa: Optional[Dict[str, Any]]) -> Optional[QAAdapterOutput]:
    """
    Convert raw QA data to standardized format
    
    Args:
        raw_qa: Raw QA data (optional, for future implementation)
    
    Returns:
        QAAdapterOutput instance or None
        
    Note:
        QA evaluation is planned for future weeks.
        For Week 2, this can return None.
    """
    pass
```

---

## Storage Interface

### `memory/storage.py`

```python
class Storage:
    """
    Owner: C
    Purpose: Simple in-memory storage for mastery samples
    Status: IMPLEMENTED
    """
    
    def __init__(self):
        """Initialize in-memory storage"""
        pass
    
    def append_mastery_sample(self, sample: MasterySample) -> None:
        """
        Append a mastery sample to storage
        
        Args:
            sample: MasterySample to store
        """
        pass
    
    def get_samples(self, user_id: str, topic_id: str) -> List[MasterySample]:
        """
        Get all mastery samples for a user and topic
        
        Args:
            user_id: User ID
            topic_id: Topic ID
        
        Returns:
            List of MasterySample, ordered by timestamp (oldest first)
            Empty list if no samples exist
        """
        pass
    
    def get_topics(self, user_id: str) -> List[str]:
        """
        Get all topic IDs that a user has studied
        
        Args:
            user_id: User ID
        
        Returns:
            List of unique topic_id strings
            Empty list if user has no topics
        """
        pass
```

---

## A's Main Application Interface (test_main.py)

### `LearningAssistant` Class

```python
class LearningAssistant:
    """
    Owner: A
    Purpose: Main system orchestrator integrating all modules
    
    Components:
        - B's modules (MOCKS): parser, tutor, quiz_gen
        - C's modules (REAL): evaluator, tracker, adaptive
        - Storage: C's implementation
    """
    
    def __init__(self, user_id: str = "user1"):
        """
        Initialize learning assistant
        
        Args:
            user_id: Default user ID for this session
        """
        pass
    
    # ===== Course Management =====
    
    def upload_course(self, file_path: str) -> dict:
        """
        Upload and parse course material
        
        Returns:
            {
                'success': bool,
                'course': dict (if success),
                'message': str (if error)
            }
        """
        pass
    
    # ===== Teaching / Q&A =====
    
    def explain_concept(self, concept: str) -> dict:
        """
        Explain a concept with adaptive difficulty
        
        Flow:
            1. Check if concept exists in user's topics
            2. If exists: compute mastery and determine difficulty
            3. If new: use default medium difficulty (3)
            4. Call B's tutor with adaptive difficulty
        
        Returns:
            {
                'success': bool,
                'concept': str,
                'difficulty': int (1-5),
                'explanation': str,
                'message': str (if error)
            }
        """
        pass
    
    def ask_question(self, question: str) -> dict:
        """
        Answer student question using tutor agent
        
        Returns:
            {
                'success': bool,
                'answer': str,
                'message': str (if error)
            }
        """
        pass
    
    # ===== Quiz =====
    
    def generate_quiz(self, topic: str, num_questions: int = 5) -> dict:
        """
        Generate quiz with adaptive difficulty
        
        Flow:
            1. Check if topic exists in user's history
            2. Compute mastery to determine difficulty
            3. Call B's quiz generator with adaptive difficulty
        
        Returns:
            {
                'success': bool,
                'quiz': dict (B's quiz format),
                'difficulty': int (1-5),
                'message': str (if error)
            }
        """
        pass
    
    def submit_quiz(self, quiz_id: str, answers: List[Dict]) -> dict:
        """
        Submit quiz and evaluate using C's evaluation system
        
        CRITICAL: This is the core integration point with C's code
        
        Args:
            quiz_id: Quiz identifier
            answers: List of answer dicts:
                [
                    {
                        'question_id': str,
                        'answer': str,
                        'correct_answer': str,
                        'topic_id': str
                    },
                    ...
                ]
        
        Flow:
            1. Validate input (check if answers is empty)
            2. Build raw_quiz in C's adapter expected format
            3. Convert using adapt_quiz_result() → QuizAdapterOutput
            4. Evaluate using C's evaluator.evaluate_quiz() → score
            5. Build MasterySample using evaluator.build_mastery_sample()
            6. Record using tracker.record_mastery_sample()
        
        Returns:
            {
                'success': bool,
                'score': float (0-1),
                'correct': int,
                'total': int,
                'topic_id': str,
                'message': str (if error)
            }
        """
        pass
    
    # ===== Progress Tracking =====
    
    def get_progress(self, topic_id: str = None) -> dict:
        """
        Get learning progress for a topic or overall
        
        Args:
            topic_id: If provided, return mastery for that topic only.
                     If None, return overall mastery and all topics.
        
        Returns (if topic_id provided):
            {
                'success': bool,
                'topic_id': str,
                'mastery': float (0-1),
                'message': str (if error)
            }
            
        Returns (if topic_id is None):
            {
                'success': bool,
                'overall_mastery': float (0-1),
                'topics': {
                    'topic1': 0.75,
                    'topic2': 0.45,
                    ...
                },
                'message': str (if error)
            }
        """
        pass
    
    def get_learning_curve(self, topic_id: str) -> dict:
        """
        Get learning curve data for visualization (for D's frontend)
        
        Args:
            topic_id: Topic to get curve for
        
        Returns:
            {
                'success': bool,
                'topic_id': str,
                'curve': [(timestamp, mastery), ...],
                'message': str (if error)
            }
            
        Example curve data:
            [
                ('2024-01-15T10:30:00', 0.45),
                ('2024-01-15T14:20:00', 0.62)
            ]
        """
        pass
    
    def next_recommendation(self) -> dict:
        """
        Get next learning step recommendation from adaptive engine
        
        Returns:
            {
                'success': bool,
                'suggestion': {
                    'next_topic_id': str,
                    'difficulty': str,
                    'action_type': str
                },
                'message': str (if error)
            }
        """
        pass
```

---

## Data Flow Diagram

```
User Input (via CLI/UI)
    ↓
A's main.py (LearningAssistant)
    ↓
B's Modules (MOCKS)              C's Modules (REAL)
    ↓                                ↓
Quiz/QA Data                     Adapters
    ↓                                ↓
                               QuizAdapterOutput
                                     ↓
                                 Evaluator
                                     ↓
                               MasterySample
                                     ↓
                              ProgressTracker
                                     ↓
                                  Storage
                                     ↓
                              AdaptiveEngine
                                     ↓
                            Recommendations
```

---

## Important Notes for Week 2

### 1. **Implementation Status**
- **C's modules**: Fully implemented (evaluator, tracker, adaptive, storage)
- **B's modules**: MOCKS only (return dummy data)
- **A's main.py**: Fully implemented integration logic

### 2. **Testing Priority**
Focus on testing the integration points:
- `submit_quiz()`: Core evaluation flow
- `explain_concept()` / `generate_quiz()`: Adaptive difficulty
- `get_progress()`: Mastery computation
- `next_recommendation()`: Adaptive suggestions

### 3. **Error Handling**
All main.py methods use try-except blocks and return:
```python
{
    "success": bool,
    # ... other fields ...
    "message": str  # Only present if success=False
}
```

### 4. **For D (Frontend Developer)**
D should call A's main.py methods. Key methods for UI:
- `get_progress()`: Display mastery dashboard
- `get_learning_curve()`: Plot progress over time
- `next_recommendation()`: Show "What to study next"
- `submit_quiz()`: Show quiz results and score