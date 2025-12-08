"""
AI Learning Assistant - Main Application
Owner: A

Integrates B's content management system with C's adaptive learning evaluation.
All components are now REAL implementations (no mocks).
"""

from datetime import datetime
from typing import Dict, List

# B's modules
from parsers.lecture_parser import LectureParser
from agents.tutor_agent import TutorAgent
from agents.quiz_agent import QuizAgent

# C's modules
from evaluation.evaluator import Evaluator
from evaluation.progress_tracker import ProgressTracker
from evaluation.adaptive_engine import AdaptiveEngine
from evaluation.adapters import adapt_quiz_result, adapt_qa_result

# Storage (shared by B and C)
from memory.storage import Storage

# Core types (shared data structure)
from core.types import MasterySample


class LearningAssistant:
    """
    Main system orchestrator integrating:
    - B's content management (parsing, tutoring, quiz generation)
    - C's adaptive learning (evaluation, progress tracking, recommendations)
    """

    def __init__(self, user_id="user1"):
        self.user_id = user_id
        
        print("🔧 Initializing Learning Assistant...")

        # Shared storage (used by both B and C)
        print("  📦 Storage...")
        self.storage = Storage()

        # B's content management components
        print("  📚 Content Management (B)...")
        self.parser = LectureParser(storage=self.storage)
        self.tutor = TutorAgent(storage=self.storage)
        self.quiz_gen = QuizAgent(storage=self.storage)

        # C's evaluation components
        print("  🎯 Evaluation System (C)...")
        self.evaluator = Evaluator()
        self.tracker = ProgressTracker(storage=self.storage)
        self.adaptive = AdaptiveEngine(storage=self.storage, tracker=self.tracker)

        self.current_course = None
        self.current_quiz = None
        self.current_difficulty_int = 3  # Track last used difficulty
        
        print("✅ Initialization Complete!\n")

    # ======================================================
    #                   HELPER METHODS
    # ======================================================
    
    def _get_adaptive_difficulty_int(self, topic_id: str) -> int:
        """
        Convert mastery level to integer difficulty (1-5)
        
        Bridges C's mastery calculation with B's difficulty scale:
        - mastery < 0.4  → difficulty 2 (easy)
        - 0.4 ≤ mastery < 0.7 → difficulty 3 (medium)
        - mastery ≥ 0.7 → difficulty 4 (hard)
        - no data → difficulty 3 (default medium)
        
        Args:
            topic_id: Topic to get difficulty for
            
        Returns:
            Difficulty level (1-5 scale)
        """
        topics = self.storage.get_topics(self.user_id)
        
        if topic_id not in topics:
            return 3  # Default: medium
        
        mastery = self.tracker.compute_topic_mastery(self.user_id, topic_id)
        
        # Use same thresholds as C's AdaptiveEngine (0.4, 0.7)
        if mastery < 0.4:
            return 2  # easy
        elif mastery < 0.7:
            return 3  # medium
        else:
            return 4  # hard
    
    def _map_difficulty_to_string(self, difficulty_int: int) -> str:
        """
        Map integer difficulty (1-5) to string ("easy"/"medium"/"hard")
        for C's evaluation system.
        
        Args:
            difficulty_int: Integer difficulty (1-5)
            
        Returns:
            String difficulty for C's system
        """
        if difficulty_int <= 2:
            return "easy"
        elif difficulty_int >= 4:
            return "hard"
        else:
            return "medium"

    # ======================================================
    #                   COURSE MANAGEMENT (B)
    # ======================================================
    
    def upload_course(self, file_path: str) -> dict:
        """
        Upload and parse course material using B's LectureParser.
        
        Flow:
        1. Parse PDF file
        2. Chunk text
        3. Store in vector database (automatic in parser)
        
        Returns:
            dict with success status and course info
        """
        try:
            print(f"📂 Parsing: {file_path}")
            course = self.parser.parse(file_path)
            self.current_course = course
            print(f"✅ Loaded: {course['title']}")
            return {
                "success": True,
                "course": course
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

    # ======================================================
    #                   TEACHING / QA (B)
    # ======================================================
    
    def explain_concept(self, concept: str) -> dict:
        """
        Explain a concept using B's TutorAgent with adaptive difficulty.
        
        Flow:
        1. Get adaptive difficulty based on mastery (C)
        2. TutorAgent queries vector DB for context (B)
        3. Generate explanation at appropriate level (B)
        """
        try:
            # Get adaptive difficulty
            difficulty_int = self._get_adaptive_difficulty_int(concept)
            
            print(f"🎓 Explaining '{concept}' at difficulty {difficulty_int}/5...")
            
            # Call B's tutor (will query vector DB internally)
            explanation = self.tutor.explain_concept(
                concept, 
                difficulty=difficulty_int,
                context=""
            )

            return {
                "success": True,
                "concept": concept,
                "difficulty": difficulty_int,
                "explanation": explanation
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

    def ask_question(self, question: str) -> dict:
        """
        Answer student question using B's TutorAgent.
        
        Flow:
        1. TutorAgent queries vector DB for relevant context
        2. Generate answer based on context
        """
        try:
            print(f"💭 Processing question...")
            # B's tutor will query vector DB internally
            answer = self.tutor.answer_question(
                question, 
                course_context=""  # Agent内部查询向量DB
            )
            return {
                "success": True,
                "answer": answer
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

    # ======================================================
    #                        QUIZ (B)
    # ======================================================
    
    def generate_quiz(self, topic: str, num_questions: int = 5) -> dict:
        """
        Generate a quiz using B's QuizAgent with adaptive difficulty.
        
        Flow:
        1. Get adaptive difficulty based on mastery (C)
        2. QuizAgent queries vector DB for context (B)
        3. Generate questions at appropriate level (B)
        4. Store quiz for later submission
        """
        try:
            # Get adaptive difficulty
            difficulty_int = self._get_adaptive_difficulty_int(topic)
            self.current_difficulty_int = difficulty_int  # Store for submit
            
            # Call B's quiz generator (queries vector DB internally)
            quiz = self.quiz_gen.generate_quiz(
                topic, 
                difficulty=difficulty_int, 
                num_questions=num_questions
            )
            
            # Store for submission
            self.current_quiz = quiz

            return {
                "success": True,
                "quiz": quiz,
                "difficulty": difficulty_int
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
    
    def show_quiz(self, show_answers: bool = False) -> dict:
        """
        Display the current quiz questions.
    
        Args:
            show_answers: If True, show correct answers (for debugging)
                         If False, hide answers (for actual testing)
        """
        try:
            if not self.current_quiz:
                return {
                    "success": False,
                    "message": "No quiz generated yet. Use 'quiz <topic>' first."
                }
        
            return {
                "success": True,
                "quiz": self.current_quiz,
                "show_answers": show_answers
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

    def submit_quiz(self, user_answers: List[str] = None) -> dict:
        """
        Submit quiz answers and evaluate using C's evaluation system.
        
        This is the core integration point between B and C.

        Flow:
        1. Convert user answers to internal format
        2. Adapt using C's adapter → QuizAdapterOutput
        3. Evaluate using C's evaluator → score
        4. Build MasterySample using C's evaluator
        5. Record using C's tracker

        Args:
            user_answers: List like ["A", "B", "C", "D", "A"]
                         If None, auto-fill with correct answers for testing
        """
        try:
            if not self.current_quiz:
                return {
                    "success": False,
                    "message": "No current quiz. Generate a quiz first."
                }
                
            questions = self.current_quiz['questions']
            
            # Build answers list
            if user_answers is None:
                # Auto-test mode: use correct answers
                print("⚠️  Auto-test mode: Using correct answers")
                answers = []
                for q in questions:
                    answers.append({
                        'question_id': q['question_id'],
                        'answer': q['correct_answer'],
                        'correct_answer': q['correct_answer'],
                        'topic_id': self.current_quiz['topic']
                    })
            else:
                # User answer mode
                if len(user_answers) != len(questions):
                    return {
                        "success": False,
                        "message": f"Expected {len(questions)} answers, got {len(user_answers)}"
                    }
            
                answers = []
                for i, q in enumerate(questions):
                    user_ans = user_answers[i].upper().strip()
                    if user_ans not in ['A', 'B', 'C', 'D']:
                        return {
                            "success": False,
                            "message": f"Invalid answer '{user_ans}' at question {i+1}. Use A/B/C/D."
                        }
                
                    answers.append({
                        'question_id': q['question_id'],
                        'answer': user_ans,
                        'correct_answer': q['correct_answer'],
                        'topic_id': self.current_quiz['topic']
                    })
            
            # Count correct answers
            correct_count = sum(
                1 for ans in answers 
                if ans.get("answer") == ans.get("correct_answer")
            )
            total = len(answers)
            topic_id = self.current_quiz['topic']

            # ====== Create raw_quiz in C's expected format ======
            # C's adapter expects:
            # {
            #     "user_id": str,
            #     "topic_id": str,      # ← NOT "topic"
            #     "timestamp": str,
            #     "difficulty": "easy/medium/hard",
            #     "questions": [{"is_correct": bool}, ...]  # ← NOT "answers"
            # }
            raw_quiz = {
                "user_id": self.user_id,
                "topic_id": topic_id,
                "timestamp": datetime.now().isoformat(),
                "difficulty": self._map_difficulty_to_string(self.current_difficulty_int),
                "questions": [
                    {"is_correct": ans["answer"] == ans["correct_answer"]}
                    for ans in answers
                ]
            }
            
            # === C's Evaluation Pipeline ===
            print("📊 Evaluating with the system...")
        
            # Step 1: Adapt to QuizAdapterOutput
            adapted = adapt_quiz_result(raw_quiz)
            
            # Step 2: Evaluate quiz
            # C's evaluator.evaluate_quiz() expects a QuizAdapterOutput object
            score = self.evaluator.evaluate_quiz(adapted)
            
            # Step 3: Build mastery sample
            # C's evaluator.build_mastery_sample() expects:
            # - quiz: QuizAdapterOutput
            # - qa: Optional[QAAdapterOutput]
            sample = self.evaluator.build_mastery_sample(
                quiz=adapted,
                qa=None
            )
            
            # Step 4: Record to storage
            self.tracker.record_mastery_sample(sample)
        
            print(f"✅ Recorded: {score:.1%} mastery for '{topic_id}'")
        
            # Build detailed results
            results_detail = []
            for i, ans in enumerate(answers, 1):
                is_correct = ans['answer'] == ans['correct_answer']
                results_detail.append({
                    'question_num': i,
                    'user_answer': ans['answer'],
                    'correct_answer': ans['correct_answer'],
                    'is_correct': is_correct
                })
        
            return {
                "success": True,
                "score": score,
                "correct": correct_count,
                "total": total,
                "topic_id": topic_id,
                "details": results_detail
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": str(e)
            }

    # ======================================================
    #                   PROGRESS TRACKING (C)
    # ======================================================
    
    def get_progress(self, topic_id: str = None) -> dict:
        """
        Get learning progress using C's ProgressTracker.
        
        Returns:
            If topic_id provided: mastery for that topic
            If no topic_id: overall mastery + all topics
        """
        try:
            if topic_id:
                # Specific topic mastery
                mastery = self.tracker.compute_topic_mastery(self.user_id, topic_id)
                return {
                    "success": True,
                    "topic_id": topic_id,
                    "mastery": mastery
                }
            else:
                # Overall mastery
                overall = self.tracker.compute_overall_mastery(self.user_id)
                topics = self.storage.get_topics(self.user_id)
                topic_masteries = {
                    t: self.tracker.compute_topic_mastery(self.user_id, t)
                    for t in topics
                }
                return {
                    "success": True,
                    "overall_mastery": overall,
                    "topics": topic_masteries
                }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

    def get_learning_curve(self, topic_id: str) -> dict:
        """
        Get learning curve data using C's ProgressTracker.
        
        Returns time-series data showing mastery progression over time.
        (For visualization by D)
        """
        try:
            curve = self.tracker.get_learning_curve(self.user_id, topic_id)
            return {
                "success": True,
                "topic_id": topic_id,
                "curve": curve
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

    # ======================================================
    #                   RECOMMENDATIONS (C)
    # ======================================================

    def next_recommendation(self) -> dict:
        """
        Get next learning step recommendation using C's AdaptiveEngine.
        
        Returns suggested topic, difficulty, and action type.
        """
        try:
            suggestion = self.adaptive.suggest_next_step(self.user_id)
            return {
                "success": True,
                "suggestion": suggestion
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }


# ============================================================
#                COMMAND LINE INTERFACE
# ============================================================

def main():
    """Command-line interface for testing the integrated system"""
    assistant = LearningAssistant()

    print("\n" + "="*60)
    print("🚀 AI Learning Assistant")
    print("   B's Content System + C's Adaptive Learning")
    print("="*60)
    print("\nCommands:")
    print("  upload <path>     - Upload course PDF")
    print("  ask <question>    - Ask a question")
    print("  explain <concept> - Get adaptive explanation")
    print("  quiz <topic> [n]  - Generate quiz (shows immediately)")
    print("  show              - Show quiz (without answers)")
    print("  show answers      - Show quiz with answers")
    print("  submit <A B C>    - Submit answers (e.g., 'submit A B C D A')")
    print("  submit            - Auto-test (uses correct answers)")
    print("  progress [topic]  - View progress")
    print("  curve <topic>     - View learning curve")
    print("  next              - Get recommendation")
    print("  quit              - Exit\n")

    while True:
        try:
            cmd = input(">>> ").strip()

            if not cmd:
                continue

            # === UPLOAD ===
            if cmd.startswith("upload "):
                path = cmd.split(" ", 1)[1]
                result = assistant.upload_course(path)
                if not result["success"]:
                    print(f"❌ {result['message']}")

            # === ASK ===
            elif cmd.startswith("ask "):
                question = cmd.split(" ", 1)[1]
                result = assistant.ask_question(question)
                if result["success"]:
                    print(f"\n💬 Answer:\n{result['answer']}\n")
                else:
                    print(f"❌ {result['message']}")

            # === EXPLAIN ===
            elif cmd.startswith("explain "):
                concept = cmd.split(" ", 1)[1]
                result = assistant.explain_concept(concept)
                if result["success"]:
                    print(f"\n📚 Concept: {result['concept']}")
                    print(f"🎯 Difficulty: {result['difficulty']}/5")
                    print(f"💡 Explanation:\n{result['explanation']}\n")
                else:
                    print(f"❌ {result['message']}")

            # === QUIZ ===
            elif cmd.startswith("quiz "):
                parts = cmd.split()
                topic = parts[1]
                num = int(parts[2]) if len(parts) > 2 else 5

                result = assistant.generate_quiz(topic, num)
                if result["success"]:
                    quiz = result['quiz']
                    print(f"\n📝 Quiz: {quiz['topic']}")
                    print(f"🎯 Difficulty: {result['difficulty']}/5")
                    print(f"📋 {len(quiz['questions'])} Questions\n")
                    print("─" * 60)
        
                    # Display questions immediately (without answers)
                    for i, q in enumerate(quiz['questions'], 1):
                        print(f"\nQuestion {i}: {q['question']}")
                        for opt in q['options']:
                            print(f"  {opt}")
        
                    print("\n" + "─" * 60)
                    print(f"💡 Type 'submit A B C ...' to submit your answers")
                    print(f"💡 Type 'submit' to auto-test with correct answers")
                    print(f"💡 Type 'show answers' to see correct answers\n")
                else:
                    print(f"❌ {result['message']}")
                    
            # === SHOW ===
            elif cmd.startswith("show"):
                show_answers = "answers" in cmd.lower()
                result = assistant.show_quiz(show_answers=show_answers)
    
                if result["success"]:
                    quiz = result['quiz']
                    print(f"\n📝 Quiz: {quiz['topic']}\n")
                    print("─" * 60)
        
                    for i, q in enumerate(quiz['questions'], 1):
                        print(f"\nQuestion {i}: {q['question']}")
                        for opt in q['options']:
                            print(f"  {opt}")
            
                        if show_answers:
                            print(f"  ✅ Correct: {q['correct_answer']}")
        
                    print("\n" + "─" * 60 + "\n")
                else:
                    print(f"❌ {result['message']}")

            # === SUBMIT ===
            elif cmd.startswith("submit"):
                parts = cmd.split()
    
                if len(parts) == 1:
                    # submit (no parameters) - auto-test
                    print("\n📤 Submitting quiz (auto-test mode)...")
                    result = assistant.submit_quiz()
                else:
                    # submit A B C D - user answers
                    user_answers = parts[1:]
                    print(f"\n📤 Submitting your answers: {' '.join(user_answers)}")
                    result = assistant.submit_quiz(user_answers)
    
                if result["success"]:
                    print(f"\n✅ Quiz Evaluated!")
                    print(f"  📊 Score: {result['score']:.1%}")
                    print(f"  ✓ Correct: {result['correct']}/{result['total']}")
                    print(f"  📚 Topic: {result['topic_id']}")
        
                    # Show detailed results
                    print(f"\n  📋 Details:")
                    for detail in result['details']:
                        status = "✅" if detail['is_correct'] else "❌"
                        print(f"    Q{detail['question_num']}: {status} "
                              f"You: {detail['user_answer']} | "
                              f"Correct: {detail['correct_answer']}")
                    print()
                else:
                    print(f"❌ {result['message']}")

            # === PROGRESS ===
            elif cmd.startswith("progress"):
                parts = cmd.split(maxsplit=1)
                topic = parts[1] if len(parts) > 1 else None
                result = assistant.get_progress(topic)
                
                if result["success"]:
                    if topic:
                        print(f"\n📊 Progress for '{topic}':")
                        print(f"  🎯 Mastery: {result['mastery']:.1%}\n")
                    else:
                        print(f"\n📊 Overall Progress:")
                        print(f"  🌟 Overall: {result['overall_mastery']:.1%}")
                        print(f"  📚 By Topic:")
                        for t, m in result['topics'].items():
                            print(f"    • {t}: {m:.1%}")
                        print()
                else:
                    print(f"❌ {result['message']}")

            # === LEARNING CURVE ===
            elif cmd.startswith("curve "):
                topic = cmd.split(" ", 1)[1]
                result = assistant.get_learning_curve(topic)
                if result["success"]:
                    print(f"\n📈 Learning Curve for '{topic}':")
                    for timestamp, mastery in result['curve']:
                        print(f"  {timestamp}: {mastery:.1%}")
                    print()
                else:
                    print(f"❌ {result['message']}")

            # === RECOMMENDATION ===
            elif cmd == "next":
                result = assistant.next_recommendation()
                if result["success"]:
                    s = result["suggestion"]
                    print(f"\n🎯 Next Recommendation:")
                    print(f"  📚 Topic: {s['next_topic_id']}")
                    print(f"  🎲 Difficulty: {s['difficulty']}")
                    print(f"  🎬 Action: {s['action_type']}\n")
                else:
                    print(f"❌ {result['message']}")

            # === QUIT ===
            elif cmd == "quit":
                print("\n👋 Goodbye!\n")
                break

            else:
                print("❌ Unknown command. Type a command or 'quit' to exit.")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!\n")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()