import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from memory.storage import Storage
    from agents.tutor_agent import TutorAgent
    from agents.quiz_agent import QuizAgent
    from parsers.lecture_parser import LectureParser
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Ensure you have a 'core.py' file if 'memory/storage.py' imports from it.")
    sys.exit(1)

def main():
    print("🚀 STARTING FINAL SYSTEM VERIFICATION...\n")

    # 1. Setup Storage
    try:
        storage = Storage()
        print("✅ Storage Initialized")
    except Exception as e:
        print(f"❌ Storage Failed: {e}")
        return

    # --- TEST 1: PARSER (.parse alias) ---
    print("\n" + "="*40)
    print("TEST 1: PARSER COMPATIBILITY")
    print("="*40)
    try:
        parser = LectureParser(storage)
        if not os.path.exists("data"):
            os.makedirs("data")
            
        files = [f for f in os.listdir("data") if f.endswith(".pdf")]
        if files:
            pdf_path = os.path.join("data", files[0])
            print(f"📄 Testing parser.parse('{pdf_path}')...")
            result = parser.parse(pdf_path)
            # Just print the title to avoid cluttering console
            print(f"   Result Title: {result.get('title', 'Unknown')}")
            print("✅ Parser Test Passed")
        else:
            print("⚠️ No PDF found in data/ folder. Skipping actual parse.")
    except Exception as e:
        print(f"❌ Parser Test Failed: {e}")

    # --- TEST 2: TUTOR (.explain_concept / .answer_question) ---
    print("\n" + "="*40)
    print("TEST 2: TUTOR COMPATIBILITY")
    print("="*40)
    try:
        tutor = TutorAgent(storage)
        print("Testing 'explain_concept' (Diff=5)...")
        
        res = tutor.explain_concept("Open Set Recognition", difficulty=5)
        
        # --- CHANGE IS HERE: Print the actual text ---
        print("\n👇 MODEL OUTPUT 👇")
        print(res) 
        print("--------------------------------------------------")

        if len(res) > 50:
            print(f"✅ Length check passed ({len(res)} chars).")
        else:
            print("❌ Tutor response too short.")
            
    except Exception as e:
        print(f"❌ Tutor Test Failed: {e}")

    # --- TEST 3: QUIZ LOOP (The New Feature) ---
    print("\n" + "="*40)
    print("TEST 3: QUIZ GENERATION LOOP")
    print("="*40)
    try:
        quiz_bot = QuizAgent(storage)
        topic = "Open Set Recognition"
        DIFF = 5
        NUM_Q = 2 

        print(f"📝 Requesting {NUM_Q} Hard Questions (Diff {DIFF}/5)...")

        # 1. Call the function
        quiz_output = quiz_bot.generate_quiz(topic, difficulty=DIFF, num_questions=NUM_Q)

        questions = quiz_output.get("questions", [])
        
        # 2. Check Count
        if len(questions) == NUM_Q:
            print(f"✅ Count matches request ({NUM_Q}).")
        else:
            print(f"❌ Count Mismatch! Expected {NUM_Q}, got {len(questions)}.")

        # 3. Print EVERYTHING to Verify
        print("\n👇 VERIFY FULL CONTENT BELOW 👇")
        for i, q in enumerate(questions):
            print(f"\n--------------------------------------------------")
            print(f" [Question {i+1}]")
            print(f"--------------------------------------------------")
            print(f"Q: {q.get('question', 'Error - Key not found')}")
            print("\nOptions:")
            for opt in q.get('options', []):
                print(f"  {opt}")
            
            print(f"\nCorrect Answer: {q.get('correct_answer', 'Error')}")
            print(f"Explanation:    {q.get('explanation', 'Error')}")

    except Exception as e:
        print(f"❌ Quiz Test Failed: {e}")

if __name__ == "__main__":
    main()
