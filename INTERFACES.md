# Module Interface Specification

## Data Format Definitions

### Course Material Format
```python
{
    'title': str,              # Course title
    'chapters': [              # List of chapters
        {
            'id': str,         # Chapter ID, e.g., "chapter_1"
            'name': str,       # Chapter name
            'content': str,    # Chapter content
            'key_concepts': List[str]  # List of key concepts
        }
    ]
}
```

### Quiz Format
```python
{
    'quiz_id': str,
    'topic': str,
    'difficulty': int,         # 1-5
    'questions': [
        {
            'question_id': str,
            'question': str,
            'options': List[str],  # Multiple choice options (can be empty)
            'correct_answer': str,
            'explanation': str     # Answer explanation
        }
    ]
}
````

### Evaluation Result Format
```python
{
    'score': float,            # 0-1
    'feedback': str,           # Text feedback
    'understanding_level': int,  # 1-5
    'mastery_change': float    # Change in mastery level
}
```

### Learning Progress Format
```python
{
    'user_id': str,
    'concepts': {
        'concept_name': {
            'mastery': float,      # 0-1
            'attempts': int,       # Number of attempts
            'last_practiced': str, # ISO timestamp
            'history': [           # History records
                {
                    'timestamp': str,
                    'score': float
                }
            ]
        }
    },
    'recommended_difficulty': int  # 1-5
}
```

---

## B's Interface (LLM Content Processing)

### Classes and Methods B Must Implement

#### 1. `parsers/lecture_parser.py`

```python
class LectureParser:
    """
    Owner: B
    Purpose: Parse course material files
    """
    
    def parse(self, file_path: str) -> dict:
        """
        Parse course material
        
        Args:
            file_path: File path (supports .txt, .pdf)
        
        Returns:
            Dictionary in course material format (see data format definition above)
        
        Raises:
            FileNotFoundError: File does not exist
            ValueError: File format not supported
        """
        pass
```

#### 2. `agents/tutor_agent.py`

```python
class TutorAgent:
    """
    Owner: B
    Purpose: Teaching explanation and Q&A
    """
    
    def __init__(self, api_key: str):
        """Initialize agent, api_key from config"""
        pass
    
    def explain_concept(self, concept: str, difficulty: int, context: str = "") -> str:
        """
        Explain a concept
        
        Args:
            concept: Concept name
            difficulty: Difficulty level 1-5 (from C's adaptive_engine)
            context: Related course material content (optional)
        
        Returns:
            Explanation text
        """
        pass
    
    def answer_question(self, question: str, course_context: str) -> str:
        """
        Answer student questions
        
        Args:
            question: Student's question
            course_context: Related course material
        
        Returns:
            Answer text
        """
        pass
```

#### 3. `agents/quiz_agent.py`

```python
class QuizAgent:
    """
    Owner: B
    Purpose: Generate quiz questions
    """
    
    def __init__(self, api_key: str):
        pass
    
    def generate_quiz(self, topic: str, difficulty: int, num_questions: int = 5, 
                     context: str = "") -> dict:
        """
        Generate quiz
        
        Args:
            topic: Quiz topic
            difficulty: Difficulty 1-5
            num_questions: Number of questions
            context: Course material context
        
        Returns:
            Dictionary in quiz format (see data format definition above)
        """
        pass
```

---

## C's Interface (Learning Evaluation & Adaptive Logic)

### Classes and Methods C Must Implement

#### 1. `evaluation/evaluator.py`

```python
class Evaluator:
    """
    Owner: C
    Purpose: Evaluate student answers
    """
    
    def __init__(self, api_key: str):
        """Can use LLM to assist evaluation"""
        pass
    
    def evaluate_answer(self, question: str, student_answer: str, 
                       correct_answer: str) -> dict:
        """
        Evaluate student answer
        
        Args:
            question: Question
            student_answer: Student's answer
            correct_answer: Correct answer
        
        Returns:
            Dictionary in evaluation result format (see data format definition above)
        """
        pass
```

#### 2. `evaluation/progress_tracker.py`

```python
class ProgressTracker:
    """
    Owner: C
    Purpose: Track learning progress
    """
    
    def __init__(self, storage):
        """storage provided by A"""
        self.storage = storage
    
    def record_quiz_result(self, user_id: str, concept: str, score: float):
        """
        Record quiz result
        
        Args:
            user_id: User ID
            concept: Concept name
            score: Score 0-1
        """
        pass
    
    def get_mastery(self, user_id: str, concept: str) -> float:
        """
        Get concept mastery level
        
        Returns:
            Mastery level 0-1
        """
        pass
    
    def get_learning_curve(self, user_id: str, concept: str) -> dict:
        """
        Get learning curve data (for D's visualization)
        
        Returns:
            {
                'timestamps': List[str],
                'scores': List[float]
            }
        """
        pass
```

#### 3. `evaluation/adaptive_engine.py`

```python
class AdaptiveEngine:
    """
    Owner: C
    Purpose: Adaptive adjustment of learning strategy
    """
    
    def __init__(self, progress_tracker: ProgressTracker):
        self.tracker = progress_tracker
    
    def recommend_difficulty(self, user_id: str, concept: str) -> int:
        """
        Recommend difficulty level
        
        Returns:
            Difficulty 1-5
        """
        pass
    
    def should_review(self, user_id: str, concept: str) -> bool:
        """
        Determine if review is needed
        
        Returns:
            True/False
        """
        pass
```

---

## Call Relationship Diagram

```
User asks question [D's UI]
    ↓
main.py's handle_question()  [A writes]
    ↓
B's tutor_agent.answer_question()
    ↓
Return answer [D's UI displays]

---

User takes quiz [D's UI]
    ↓
main.py's generate_quiz()  [A writes]
    ↓
C's adaptive_engine.recommend_difficulty()  [Get difficulty]
    ↓
B's quiz_agent.generate_quiz()  [Generate quiz]
    ↓
Return quiz [D's UI displays]
    ↓
User answers questions
    ↓
main.py's evaluate_quiz()  [A writes]
    ↓
C's evaluator.evaluate_answer()
    ↓
C's progress_tracker.record_quiz_result()
    ↓
Return results [D's UI displays]
```

---

## Important Notes

1. **B and C only need to implement the classes and methods defined above; they don't need to worry about how main.py calls them**
2. **A is responsible for integrating all modules in main.py**
3. **All exception handling is unified in main.py**
4. **API keys are uniformly managed by A's config**
5. **Data storage is uniformly handled by A's storage interface**

---