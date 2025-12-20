# Module Interface Specification

**Project:** AI Teaching Tutor  
**Course:** Columbia COMS4995_032 Applied Machine Learning  
**Last Updated:** 2025.12

---

## Prerequisites & Configuration

### Environment Variables
```bash
# .env file (required)
HF_TOKEN=your_hugging_face_token_here
```

### System Requirements
- **Python:** 3.8+
- **RAM:** 8 GB minimum, 16 GB recommended
- **VRAM:** 4 GB (with 4-bit quantization)
- **First Load:** 30-60 seconds (downloads Phi-3), subsequent runs <1s

### Setup
1. Get HF token: https://huggingface.co/settings/tokens
2. `cp .env.example .env` and add your token
3. `pip install -r requirements.txt`

---

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
    timestamp: datetime
    score: float  # value in [0, 1]
    num_questions: Optional[int] = None
    difficulty: Optional[str] = None  # "easy" / "medium" / "hard"
```

---

## B's Interface (LLM Content Processing)

### 1. `parsers/lecture_parser.py`

```python
class LectureParser:
    """
    Owner: B
    Purpose: Parse course material files (PDF) and store chunks in the vector database.
    Status: IMPLEMENTED & TESTED
    """

    def __init__(self, storage=None):
        """
        Initialize the parser with storage backend.
        
        Args:
            storage: Optional Storage instance. If None, initializes default Storage.
        """
        pass

    def parse(self, file_path: str) -> dict:
        """
        Parse course material, extract text, and save to Vector DB.
        
        Args:
            file_path: Absolute path to the file (must be .pdf)
        
        Returns:
            {
                'title': str,
                'chapters': [
                    {
                        'id': 'chap_1',
                        'name': 'Extracted Content',
                        'content': str,  # Full extracted text
                        'key_concepts': []  # Empty list in current implementation
                    }
                ]
            }
        
        Raises:
            FileNotFoundError: If file path is invalid
            ValueError: If file format is not .pdf
        """
        pass
```

### 2. `agents/tutor_agent.py`

```python
class TutorAgent:
    """
    Owner: B
    Purpose: RAG-enabled teaching explanation and Q&A using Phi-3 model.
    Status: IMPLEMENTED & TESTED
    """

    def __init__(self, storage=None):
        """
        Initialize the Tutor Agent.
        
        Args:
            storage: Optional Storage instance. If None, initializes default Storage.
            
        Side Effects:
            - Loads the 'microsoft/Phi-3-mini-4k-instruct' model to GPU.
            - Initializes 4-bit quantization config.
            - Sets up the HuggingFace text-generation pipeline.
        """
        pass

    def respond(self, query: str) -> str:
        """
        Core RAG method: Retrieval + Generation.
        
        Args:
            query: The raw input string to search for and generate a response to.
            
        Returns:
            str: The direct LLM output based on retrieved context.
        """
        pass

    def explain_concept(self, concept: str, difficulty: int = 3, context: str = "") -> str:
        """
        Explain a concept with adaptive difficulty using retrieved context.
        
        Args:
            concept: The concept to explain.
            difficulty: Target difficulty level (1-5).
            context: Optional override context.
        
        Returns:
            str: The AI-generated explanation based on the course material.
        """
        pass

    def answer_question(self, question: str, course_context: str = "") -> str:
        """
        Answer a specific student question.
        
        Args:
            question: The student's natural language question.
            course_context: Optional override context.
        
        Returns:
            str: The AI-generated answer.
        """
        pass
```

### 3. `agents/quiz_agent.py`

```python
class QuizAgent:
    """
    Owner: B
    Purpose: Generate multiple-choice quiz questions based on course material using Phi-3.
    Status: IMPLEMENTED & TESTED
    """

    def __init__(self, storage):
        """
        Initialize the Quiz Agent.
        
        Args:
            storage: The Storage instance containing the vector DB.
            
        Side Effects:
            - Loads the 'microsoft/Phi-3-mini-4k-instruct' model to GPU.
            - Initializes 4-bit quantization config.
            - Sets up the HuggingFace text-generation pipeline.
        """
        pass

    def generate_quiz(self, topic: str, difficulty: int = 3, num_questions: int = 5, context: str = "") -> dict:
        """
        Generate a structured quiz with multiple questions.
        
        Args:
            topic: The topic to generate questions for.
            difficulty: Integer 1-5 (Adjusts complexity of questions).
            num_questions: Number of questions to generate.
            context: Optional manual context (default uses RAG).
        
        Returns:
            {
                'quiz_id': str,
                'topic': str,
                'difficulty': int,
                'questions': [
                    {
                        'question_id': str,
                        'question': str,
                        'options': {
                            'A': str,
                            'B': str,
                            'C': str,
                            'D': str
                        },
                        'correct_answer': str (e.g., "A"),
                        'explanation': str
                    },
                    ...
                ]
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
    Status: IMPLEMENTED & TESTED
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
    Status: IMPLEMENTED & TESTED
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
                ('2026-01-13T10:30:00', 0.45),
                ('2026-01-14T14:20:00', 0.62),
                ('2026-01-15T09:15:00', 0.78)
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
    Status: IMPLEMENTED & TESTED
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
```

**Difficulty Mapping Reference:**
| Mastery Range | Difficulty | Integer | Used By |
|---------------|------------|---------|---------|
| < 0.2         | Very Easy  | 1       | -       |
| 0.2 - 0.4     | Easy       | 2       | A's helper |
| 0.4 - 0.7     | Medium     | 3 (default) | A's helper |
| 0.7 - 0.9     | Hard       | 4       | A's helper |
| >= 0.9        | Very Hard  | 5       | -       |

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

## D's Interface (Frontend & Visualization)

### `app.py` - Streamlit Dashboard

**Owner:** Team D  
**Status:** IMPLEMENTED & TESTED  
**Framework:** Streamlit  
**Run:** `streamlit run app.py`

#### Main Components

```python
# Four main tabs in the interface:

# 1. 💬 Tutor Chat
#    - Ask questions
#    - Explain concepts
#    - Uses TutorAgent with adaptive difficulty

# 2. 📝 Quiz
#    - Generate adaptive quizzes
#    - Interactive question answering
#    - Submit and get detailed feedback

# 3. 📊 Progress
#    - Overall mastery metric
#    - Topic-by-topic breakdown
#    - Learning curve visualization

# 4. 🎯 Next Step
#    - Personalized recommendations
#    - Suggested topic and difficulty
```

#### Key UI Functions

```python
def get_assistant() -> LearningAssistant:
    """Get or create a LearningAssistant bound to the current user."""
    pass

def init_state():
    """Initialize UI-related session state."""
    # Session state includes:
    # - chat_history: List of chat messages
    # - current_course: Uploaded course info
    # - current_quiz: Active quiz data
    # - last_quiz_result: Latest quiz submission result
    pass
```

#### Features Implemented

**Course Upload:**
- PDF file upload via `st.file_uploader`
- Temporary file handling
- Vector DB indexing

**Chat Interface:**
- Two modes: "Ask a question" and "Explain a concept"
- Chat history display
- Real-time responses from TutorAgent

**Quiz Interface:**
- Topic input and question count slider
- Adaptive difficulty generation
- Radio button answer selection
- Detailed feedback with explanations

**Progress Visualization:**
- Pandas DataFrame for topic overview
- Streamlit metrics for overall mastery
- Plotly line charts for learning curves

**Dependencies:**
- `streamlit>=1.31.0`
- `plotly>=5.18.0`
- `pandas>=2.0.0`

---

## Storage Interface

### `memory/storage.py`

```python
class Storage:
    """
    Owner: C & B
    Purpose: Shared storage handling both In-Memory Mastery data (C) and Vector Database (B).
    Status: IMPLEMENTED & TESTED
    """

    def __init__(self):
        """
        Initialize both the Mastery storage (dict) and Vector DB (Chroma).
        """
        pass

    # --- Part 1: Mastery Storage (Owner: C) ---

    def append_mastery_sample(self, sample: MasterySample) -> None:
        """
        Append a mastery sample to in-memory storage.
        
        Args:
            sample: The MasterySample object to store.
        """
        pass

    def get_samples(self, user_id: str, topic_id: str) -> List[MasterySample]:
        """
        Get all mastery samples for a specific user and topic.
        
        Args:
            user_id: The ID of the student.
            topic_id: The ID of the topic.
            
        Returns:
            List[MasterySample]: Ordered list of samples (oldest first).
        """
        pass

    def get_topics(self, user_id: str) -> List[str]:
        """
        Get a list of all topic IDs a user has studied.
        
        Args:
            user_id: The ID of the student.
            
        Returns:
            List[str]: Unique topic IDs.
        """
        pass

    # --- Part 2: Vector DB Operations (Owner: B) ---

    def add_documents(self, documents) -> None:
        """
        Store parsed text chunks into the Chroma Vector Database.
        
        Args:
            documents: List of LangChain Document objects.
        """
        pass

    def query(self, question: str, k: int = 3) -> list:
        """
        Retrieve relevant text chunks for a given query.
        
        Args:
            question: The search query string.
            k: Number of results to return.
            
        Returns:
            List[Document]: The matched text chunks with similarity scores.
        """
        pass
```

---

## A's Main Application Interface

### `main.py` - LearningAssistant Class

```python
class LearningAssistant:
    """
    Owner: A
    Purpose: Main system orchestrator integrating all modules
    Status: IMPLEMENTED & TESTED
    
    Components:
        - B's modules: parser, tutor, quiz_gen
        - C's modules: evaluator, tracker, adaptive
        - Storage: Shared implementation
    """
    
    def __init__(self, user_id: str = "user1"):
        """Initialize learning assistant with all components"""
        pass
    
    # ===== Helper Methods =====
    
    def _get_adaptive_difficulty_int(self, topic_id: str) -> int:
        """
        Convert mastery level to integer difficulty (1-5)
        
        Bridges C's mastery calculation with B's difficulty scale:
        - mastery < 0.4  → difficulty 2 (easy)
        - 0.4 ≤ mastery < 0.7 → difficulty 3 (medium)
        - mastery ≥ 0.7 → difficulty 4 (hard)
        - no data → difficulty 3 (default medium)
        """
        pass
    
    def _map_difficulty_to_string(self, difficulty_int: int) -> str:
        """
        Map integer difficulty (1-5) to string for C's evaluation system
        
        Returns: "easy", "medium", or "hard"
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
            1. Get adaptive difficulty based on mastery
            2. Call TutorAgent with appropriate difficulty
        
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
            1. Get adaptive difficulty based on mastery
            2. Generate quiz with QuizAgent
            3. Store quiz for later submission
        
        Returns:
            {
                'success': bool,
                'quiz': dict (B's quiz format),
                'difficulty': int (1-5),
                'message': str (if error)
            }
        """
        pass
    
    def show_quiz(self, show_answers: bool = False) -> dict:
        """
        Display the current quiz questions
        
        Args:
            show_answers: If True, show correct answers (for debugging)
        
        Returns:
            {
                'success': bool,
                'quiz': dict,
                'show_answers': bool,
                'message': str (if error)
            }
        """
        pass
    
    def submit_quiz(self, user_answers: List[str] = None) -> dict:
        """
        Submit quiz answers and evaluate using C's evaluation system
        
        **CRITICAL INTEGRATION POINT** - Where B and C connect
        
        Args:
            user_answers: List like ["A", "B", "C", "D", "A"]
                         If None, auto-fill with correct answers for testing
        
        Flow:
            1. Validate answers or auto-fill
            2. Build raw_quiz in C's adapter expected format
            3. Convert using adapt_quiz_result() → QuizAdapterOutput
            4. Evaluate using evaluator.evaluate_quiz() → score
            5. Build MasterySample using evaluator.build_mastery_sample()
            6. Record using tracker.record_mastery_sample()
        
        Returns:
            {
                'success': bool,
                'score': float (0-1),
                'correct': int,
                'total': int,
                'topic_id': str,
                'details': [
                    {
                        'question_num': int,
                        'user_answer': str,
                        'correct_answer': str,
                        'is_correct': bool
                    },
                    ...
                ],
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
User Input (CLI/Streamlit UI)
    ↓
A's main.py (LearningAssistant)
    ↓
B's Modules                    C's Modules
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
                                     ↓
                         D's Streamlit UI
```

---

## Quick Reference

### Typical Workflow (CLI)
```bash
# Start the system
python main.py

# Upload course
>>> upload data/lecture.pdf

# Generate adaptive quiz
>>> quiz neural_networks 5

# Submit answers
>>> submit A B C D A

# Check progress
>>> progress neural_networks

# Get recommendation
>>> next
```

### Typical Workflow (Streamlit)
```bash
# Start web app
streamlit run app.py

# Then in browser:
# 1. Upload PDF in sidebar
# 2. Chat with tutor or generate quiz
# 3. View progress in Progress tab
# 4. Get recommendations in Next Step tab
```

### Performance Expectations
- **Model Loading:** 30-60s first time, <1s cached
- **Quiz Generation:** ~5-10s for 5 questions
- **Evaluation:** <100ms
- **RAG Query:** 1-3s

### Common Errors
```python
# Missing HF_TOKEN
# → Add HF_TOKEN to .env file

# No quiz generated
# → Call generate_quiz() before submit_quiz()

# Wrong number of answers
# → submit_quiz() expects list matching number of questions
```

---

**Last Updated:** December 2025  
**Course:** Columbia COMS4995_032 Applied Machine Learning