"""
AI Learning Assistant - Main Application (Week 2)
Owner: A

Integrates with C's evaluation system.
B's components (parser, tutor, quiz) are MOCKS for Week 2.
"""

from datetime import datetime
from typing import Dict, List

# B's modules (MOCKS)
from parsers.lecture_parser import LectureParser
from agents.tutor_agent import TutorAgent
from agents.quiz_agent import QuizAgent

# C's evaluation modules (REAL implementations)
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
    Main system orchestrator for Week 2.
    Core requirement: integrate with C's evaluation interfaces.
    B's components are MOCKS.
    """

    def __init__(self, user_id="user1"):
        self.user_id = user_id

        # Storage (C's implementation)
        self.storage = Storage()

        # B's mock components
        self.parser = LectureParser()
        self.tutor = TutorAgent()
        self.quiz_gen = QuizAgent(self.storage)

        # C's evaluation components
        self.evaluator = Evaluator()
        self.tracker = ProgressTracker(storage=self.storage)
        self.adaptive = AdaptiveEngine(storage=self.storage, tracker=self.tracker)

        self.current_course = None

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
        Uses B's mock parser.
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
        Explain a concept using tutor agent (mock) with adaptive difficulty.
        
        Flow:
        1. Get adaptive difficulty using helper method
        2. Call B's tutor agent (mock) to generate explanation
        """
        try:
            # Get adaptive difficulty
            difficulty_int = self._get_adaptive_difficulty_int(concept)
            
            # Call B's mock tutor
            explanation = self.tutor.explain_concept(
                concept, 
                difficulty_int, 
                context="mock"
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
        Answer student question using tutor agent (mock).
        """
        try:
            answer = self.tutor.answer_question(question, course_context="mock")
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
        Generate a quiz using quiz agent (mock) with adaptive difficulty.
        
        Flow:
        1. Get adaptive difficulty using helper method
        2. Call B's quiz agent (mock) to generate quiz
        """
        try:
            # Get adaptive difficulty
            difficulty_int = self._get_adaptive_difficulty_int(topic)
            
            # Call B's mock quiz generator
            quiz = self.quiz_gen.generate_quiz(
                topic, 
                difficulty_int, 
                num_questions
            )

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

    def submit_quiz(self, quiz_id: str, answers: List[Dict]) -> dict:
        """
        Submit quiz answers and evaluate using C's evaluation system.
        
        This is the CORE integration point with C's code.
        
        Flow:
        1. Validate input
        2. Convert answers to raw_quiz format
        3. Adapt using C's adapter → QuizAdapterOutput
        4. Evaluate using C's evaluator → score
        5. Build MasterySample using C's evaluator
        6. Record using C's tracker
        
        Args:
            quiz_id: Quiz identifier
            answers: List of dicts with format:
                [
                    {
                        'question_id': str,
                        'answer': str,
                        'correct_answer': str,
                        'topic_id': str
                    },
                    ...
                ]
        """
        try:
            # Validate input
            if not answers:
                return {
                    "success": False,
                    "message": "No answers provided"
                }
            
            # Count correct answers
            correct_count = sum(
                1 for ans in answers 
                if ans.get("answer") == ans.get("correct_answer")
            )
            total = len(answers)
            
            # Get topic from first answer
            topic_id = answers[0].get("topic_id", "unknown")

            # Step 1: Build raw_quiz in the format C's adapter expects
            raw_quiz = {
                "user_id": self.user_id,
                "topic_id": topic_id,
                "timestamp": datetime.now().isoformat(),
                "difficulty": "medium",  # This should come from generate_quiz
                "questions": [
                    {"is_correct": ans["answer"] == ans["correct_answer"]}
                    for ans in answers
                ]
            }

            # Step 2: Adapt to QuizAdapterOutput (C's adapter)
            quiz_output = adapt_quiz_result(raw_quiz)

            # Step 3: Evaluate quiz (C's evaluator)
            quiz_score = self.evaluator.evaluate_quiz(quiz_output)

            # Step 4: Build MasterySample (C's evaluator)
            mastery_sample = self.evaluator.build_mastery_sample(quiz_output, qa=None)

            # Step 5: Record to storage (C's tracker)
            self.tracker.record_mastery_sample(mastery_sample)

            return {
                "success": True,
                "score": quiz_score,
                "correct": correct_count,
                "total": total,
                "topic_id": topic_id
            }
        except Exception as e:
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
    print("  upload <path>     - Upload course material")
    print("  explain <concept> - Explain a concept")
    print("  ask <question>    - Ask a question")
    print("  quiz <topic>      - Generate quiz")
    print("  submit            - Submit quiz with test answers")
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
                topic = cmd.split(" ", 1)[1]
                result = assistant.generate_quiz(topic)
                if result["success"]:
                    print(f"\n📝 Quiz generated:")
                    print(f"  Topic: {result['quiz']['topic']}")
                    print(f"  Difficulty: {result['difficulty']}/5")
                    print(f"  Questions: {len(result['quiz']['questions'])}\n")
                else:
                    print(f"❌ {result['message']}")

            elif cmd == "submit":
                # Test submission with fixed answers
                print("\n📤 Submitting test quiz answers...")
                answers = [
                    {
                        "question_id": "q1",
                        "answer": "correct",
                        "correct_answer": "correct",
                        "topic_id": "math"
                    },
                    {
                        "question_id": "q2",
                        "answer": "wrong",
                        "correct_answer": "right",
                        "topic_id": "math"
                    },
                    {
                        "question_id": "q3",
                        "answer": "correct",
                        "correct_answer": "correct",
                        "topic_id": "math"
                    },
                ]
                result = assistant.submit_quiz("test_quiz", answers)
                if result["success"]:
                    print(f"✅ Quiz submitted!")
                    print(f"  Score: {result['score']:.2%}")
                    print(f"  Correct: {result['correct']}/{result['total']}")
                    print(f"  Topic: {result['topic_id']}\n")
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