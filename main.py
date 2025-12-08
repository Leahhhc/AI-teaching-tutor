"""
AI Learning Assistant - Main Application (Week 4)
Owner: A

Integrates with B and C's parts.
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

# Storage
from memory.storage import Storage

# Core types
from core.types import MasterySample


class LearningAssistant:
    """
    Main system orchestrator for Week 4.
    """

    def __init__(self, user_id="user1"):
        self.user_id = user_id

        # Storage
        self.storage = Storage()

        # B's components
        self.parser = LectureParser()
        self.tutor = TutorAgent(self.storage)
        self.quiz_gen = QuizAgent(self.storage)

        # C's components
        self.evaluator = Evaluator()
        self.tracker = ProgressTracker(storage=self.storage)
        self.adaptive = AdaptiveEngine(storage=self.storage, tracker=self.tracker)

        self.current_course = None
        self.current_quiz = None

    # ======================================================
    #                   HELPER METHODS
    # ======================================================
    
    def _get_adaptive_difficulty_int(self, topic_id: str) -> int:
        """
        Convert mastery level to integer difficulty (1-5)
        
        This is a helper that bridges C's string-based difficulty
        ("easy"/"medium"/"hard") with B's integer-based difficulty (1-5).
        
        Args:
            topic_id: Topic to get difficulty for
            
        Returns:
            Difficulty level:
                2 = easy (mastery < 0.4)
                3 = medium (0.4 <= mastery < 0.7)
                4 = hard (mastery >= 0.7)
                3 = default (no data)
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

    # ======================================================
    #                   COURSE MANAGEMENT
    # ======================================================
    
    def upload_course(self, file_path: str) -> dict:
        """
        Upload and parse course material.
        """
        try:
            course = self.parser.parse(file_path)
            self.current_course = course
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
    #                   TEACHING / QA
    # ======================================================
    
    def explain_concept(self, concept: str) -> dict:
        """
        Explain a concept using tutor agent with adaptive difficulty.
        
        Flow:
            1. Get adaptive difficulty based on mastery
            2. TutorAgent queries vector DB for context
            3. Generate explanation at appropriate level
        """
        try:
            # Get adaptive difficulty
            difficulty_int = self._get_adaptive_difficulty_int(concept)
            
            print(f"🎓 Explaining '{concept}' at difficulty {difficulty_int}/5...")
            
            # Call B's tutor
            explanation = self.tutor.explain_concept(
                concept, 
                difficulty_int, 
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
        Answer student question using tutor agent.
        """
        try:
            answer = self.tutor.answer_question(question, course_context="")
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
    #                        QUIZ
    # ======================================================
    
    def generate_quiz(self, topic: str, num_questions: int = 5) -> dict:
        """
        Generate a quiz using quiz agent with adaptive difficulty.
        
        Flow:
        1. Get adaptive difficulty using helper method
        2. Call quiz agent to generate quiz
        """
        try:
            # Get adaptive difficulty
            difficulty_int = self._get_adaptive_difficulty_int(topic)
            
            # Call quiz generator
            quiz = self.quiz_gen.generate_quiz(
                topic, 
                difficulty_int, 
                num_questions
            )
            
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
            show_answers: 
                If True, show correct answers (for debugging)
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

    def submit_quiz(self, user_answers: List[Dict] = None) -> dict:
        """
        Submit quiz answers and evaluate.

        Args:
            user_answers: 
                List like ["A", "B", "C", "D", "A"]
                If None, auto-fill with correct answers
        """
        try:
            if not self.current_quiz:
                return {
                    "success": False,
                    "message": "No current quiz. Generate a quiz first."
                }
                
            questions = self.current_quiz['questions']
            
            # Construct answers
            if user_answers is None:
                # Auto-test mode
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
                # User-answer mode
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
            
            # Get topic from first answer
            topic_id = self.current_quiz['topic']

            # Build raw_quiz
            raw_quiz = {
                "quiz_id": self.current_quiz.get('quiz_id', 'test_quiz'),
                "topic": topic_id,
                "answers": answers
            }
            
            # === C's Evaluation Pipeline ===
            print("📊 Evaluating with the system...")
        
            adapted = adapt_quiz_result(raw_quiz)
            score = self.evaluator.evaluate_quiz(adapted.results, adapted.topic_id)
            sample = self.evaluator.build_mastery_sample(
                self.user_id,
                adapted.topic_id,
                score,
                datetime.now()
            )
            self.tracker.record_mastery_sample(sample)
        
            print(f"✅ Recorded: {score:.1%} mastery for '{topic_id}'")
        
            # detailed results
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
    #                     PROGRESS
    # ======================================================
    
    def get_progress(self, topic_id: str = None) -> dict:
        """
        Get learning progress for a topic or overall.
        Uses C's tracker.
        """
        try:
            if topic_id:
                # Get mastery for specific topic
                mastery = self.tracker.compute_topic_mastery(self.user_id, topic_id)
                return {
                    "success": True,
                    "topic_id": topic_id,
                    "mastery": mastery
                }
            else:
                # Get overall mastery
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
        Get learning curve data for visualization (for D).
        Uses C's tracker.
        
        Returns:
            {
                'success': bool,
                'topic_id': str,
                'curve': [(timestamp, mastery), ...]
            }
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

    def next_recommendation(self) -> dict:
        """
        Get next learning step recommendation.
        Uses C's adaptive engine.
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
#                COMMAND LINE TEST (Week 2)
# ============================================================

def main():
    """Command-line interface for testing"""
    assistant = LearningAssistant()

    print("\n🚀 Week 2 AI Learning Assistant (with C's evaluation system)\n")
    print("Commands:")
    print("  upload <path>     - Upload course PDF")
    print("  explain <concept> - Get adaptive explanation")
    print("  ask <question>    - Ask a question")
    print("  quiz <topic> [n]  - Generate quiz (default 5 questions)")
    print("  show              - Show quiz again (without answers)")
    print("  show answers      - Show quiz with correct answers")
    print("  submit <A B C>    - Submit your answers (e.g., 'submit A B C D A')")
    print("  submit            - Auto-test mode (uses correct answers)")
    print("  progress [topic]  - View progress")
    print("  curve <topic>     - View learning curve")
    print("  next              - Get next recommendation")
    print("  quit              - Exit\n")

    while True:
        try:
            cmd = input(">>> ").strip()

            if not cmd:
                continue

            if cmd.startswith("upload "):
                path = cmd.split(" ", 1)[1]
                result = assistant.upload_course(path)
                print(result)

            elif cmd.startswith("explain "):
                concept = cmd.split(" ", 1)[1]
                result = assistant.explain_concept(concept)
                if result["success"]:
                    print(f"\n📚 Concept: {result['concept']}")
                    print(f"Difficulty: {result['difficulty']}/5")
                    print(f"Explanation: {result['explanation']}\n")
                else:
                    print(f"❌ {result['message']}")

            elif cmd.startswith("ask "):
                question = cmd.split(" ", 1)[1]
                result = assistant.ask_question(question)
                if result["success"]:
                    print(f"\n💡 Answer: {result['answer']}\n")
                else:
                    print(f"❌ {result['message']}")

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
        
                    for i, q in enumerate(quiz['questions'], 1):
                        print(f"\nQuestion {i}: {q['question']}")
                        for opt in q['options']:
                            print(f"  {opt}")
        
                    print("\n" + "─" * 60)
                    print(f"💡 Type 'submit A B C D ...' to submit your answers")
                    print(f"💡 Type 'submit' to auto-test with correct answers")
                    print(f"💡 Type 'show answers' to see correct answers\n")
                else:
                    print(f"❌ {result['message']}")
                    
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

            elif cmd.startswith("submit"):
                parts = cmd.split()
    
                if len(parts) == 1:
                    # submit (no parameters) - auto-test
                    print("\n📤 Submitting quiz (auto-test mode)...")
                    result = assistant.submit_quiz()
                else:
                    # submit A B C D - user-answer
                    user_answers = parts[1:]
                    print(f"\n📤 Submitting your answers: {' '.join(user_answers)}")
                    result = assistant.submit_quiz(user_answers)
    
                if result["success"]:
                    print(f"\n✅ Quiz Evaluated!")
                    print(f"  📊 Score: {result['score']:.1%}")
                    print(f"  ✓ Correct: {result['correct']}/{result['total']}")
                    print(f"  📚 Topic: {result['topic_id']}")
        
                    # show detailed results
                    print(f"\n  📋 Details:")
                    for detail in result['details']:
                        status = "✅" if detail['is_correct'] else "❌"
                        print(f"    Q{detail['question_num']}: {status} "
                            f"You: {detail['user_answer']} | "
                            f"Correct: {detail['correct_answer']}")
                    print()
                else:
                    print(f"❌ {result['message']}")

            elif cmd.startswith("progress"):
                parts = cmd.split(maxsplit=1)
                topic = parts[1] if len(parts) > 1 else None
                result = assistant.get_progress(topic)
                if result["success"]:
                    if topic:
                        print(f"\n📊 Progress for '{topic}':")
                        print(f"  Mastery: {result['mastery']:.1%}\n")
                    else:
                        print(f"\n📊 Overall Progress:")
                        print(f"  Overall Mastery: {result['overall_mastery']:.1%}")
                        print(f"  Topics:")
                        for t, m in result['topics'].items():
                            print(f"    {t}: {m:.1%}")
                        print()
                else:
                    print(f"❌ {result['message']}")

            elif cmd.startswith("curve "):
                topic = cmd.split(" ", 1)[1]
                result = assistant.get_learning_curve(topic)
                if result["success"]:
                    print(f"\n📈 Learning curve for '{topic}':")
                    for timestamp, mastery in result['curve']:
                        print(f"  {timestamp}: {mastery:.1%}")
                    print()
                else:
                    print(f"❌ {result['message']}")

            elif cmd == "next":
                result = assistant.next_recommendation()
                if result["success"]:
                    s = result["suggestion"]
                    print(f"\n🎯 Next Recommendation:")
                    print(f"  Topic: {s['next_topic_id']}")
                    print(f"  Difficulty: {s['difficulty']}")
                    print(f"  Action: {s['action_type']}\n")
                else:
                    print(f"❌ {result['message']}")

            elif cmd == "quit":
                print("👋 Goodbye!")
                break

            else:
                print("❌ Unknown command")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()