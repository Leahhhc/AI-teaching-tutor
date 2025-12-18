import torch
import re
import uuid
from typing import List, Dict, Any
from langchain_huggingface import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from memory.storage import Storage
from prompts.quiz_prompt import QUIZ_SYSTEM_PROMPT, QUIZ_USER_PROMPT_TEMPLATE

class QuizAgent:
    def __init__(self, storage: Storage):
        self.storage = storage
        print("⏳ Loading Quiz AI Model...")
        model_id = "microsoft/Phi-3-mini-4k-instruct"
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=bnb_config, device_map="auto")

        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=2048,  # INCREASED: Needed for generating multiple questions at once
            temperature=0.1,
            do_sample=True,
            return_full_text=False
        )
        self.llm = HuggingFacePipeline(pipeline=pipe)
        print("✅ Quiz Agent Ready!")

    def _parse_quiz_output(self, raw_text: str) -> List[Dict[str, Any]]:
        """Parses the LLM output containing MULTIPLE questions separated by ---"""
        questions = []
        
        # 1. Split by the separator defined in your prompt (---)
        blocks = raw_text.split('---')

        for block in blocks:
            block = block.strip()
            # Skip empty blocks or blocks that don't look like questions
            if not block or "Question" not in block or "Correct Answer" not in block:
                continue

            try:
                # 2. Extract Question Text (handles 'Question [1]:' or just 'Question:')
                question_match = re.search(r"Question\s*\[?\d*\]?:\s*(.*?)(?=\nA\))", block, re.DOTALL)
                question_text = question_match.group(1).strip() if question_match else "Could not parse question."

                # 3. Extract Options (A, B, C, D)
                options: Dict[str, str] = {}
                for char in ["A", "B", "C", "D"]:
                    opt_match = re.search(
                        rf"{char}\)\s*(.*?)(?=\n[A-D]\)|\nCorrect Answer:|\nExplanation:|$)",
                        block,
                        re.DOTALL
                    )
                    if opt_match:
                        options[char] = opt_match.group(1).strip()

                # Fallback if parsing fails
                if len(options) != 4:
                    options = {"A": "Error", "B": "Error", "C": "Error", "D": "Error"}
                
                # Fallback if parsing fails
                if not options:
                     options = ["A) Error", "B) Error", "C) Error", "D) Error"]

                # 4. Extract Correct Answer
                correct_match = re.search(r"Correct Answer:\s*([A-D])", block)
                correct_ans = correct_match.group(1).strip() if correct_match else "A"

                # 5. Extract Explanation
                explanation_match = re.search(r"Explanation:\s*(.*)", block, re.DOTALL)
                explanation = explanation_match.group(1).strip() if explanation_match else "See notes."

                questions.append({
                    "question_id": str(uuid.uuid4())[:8],
                    "question": question_text,
                    "options": options,
                    "correct_answer": correct_ans,
                    "explanation": explanation
                })
            except Exception as e:
                print(f"⚠️ Error parsing a question block: {e}")
                continue

        return questions

    def generate_quiz(self, topic: str, difficulty: int = 3, num_questions: int = 5, context: str = "") -> dict:
        print(f"🔍 Generating {num_questions} questions for: {topic} (Difficulty: {difficulty}/5)")

        # 1. Get Context
        if not context:
            results = self.storage.query(topic, k=3)
            context = "\n\n".join([doc.page_content for doc in results]) if results else "No specific notes found."

        # 2. Define Difficulty Rules (THIS IS THE NEW PART)
        # We translate the number into specific instructions for the AI
        difficulty_rules = ""
        if difficulty >= 4:
            difficulty_rules = (
                "DIFFICULTY INSTRUCTIONS (Advanced):\n"
                "- Questions must analyze complex scenarios or edge cases.\n"
                "- Avoid simple definitions.\n"
                "- Options must be plausible distractors (no obviously wrong answers).\n"
                "- Requires synthesizing multiple concepts to answer."
            )
        elif difficulty <= 2:
            difficulty_rules = (
                "DIFFICULTY INSTRUCTIONS (Beginner):\n"
                "- Focus on basic definitions and core concepts.\n"
                "- Questions should be direct and straightforward.\n"
                "- The correct answer should be clearly distinguishable from options."
            )
        else:
            difficulty_rules = (
                "DIFFICULTY INSTRUCTIONS (Intermediate):\n"
                "- combine conceptual understanding with simple application.\n"
                "- Test the standard use-cases of the topic."
            )

        # 3. Build Prompt
        system_prompt = QUIZ_SYSTEM_PROMPT.format(num_questions=num_questions)
        user_prompt = QUIZ_USER_PROMPT_TEMPLATE.format(
            context=context,
            num_questions=num_questions
        )

        full_prompt = f"""<|system|>
{system_prompt}
<|end|>
<|user|>
{user_prompt}

Constraint: Target Difficulty Level {difficulty}/5.
{difficulty_rules}
<|end|>
<|assistant|>"""

        # 4. Invoke LLM
        print("   ... Invoking LLM for bulk generation ...")
        response_text = self.llm.invoke(full_prompt)
        
        # 5. Parse
        questions_list = self._parse_quiz_output(response_text)

        if not questions_list:
            questions_list = [{
                "question_id": str(uuid.uuid4())[:8],
                "question": "Failed to generate questions. Please try again.",
                "options": {"A": "Retry", "B": "Retry", "C": "Retry", "D": "Retry"},
                "correct_answer": "A",
                "explanation": "The model output could not be parsed."
            }]

        return {
            "quiz_id": str(uuid.uuid4())[:8],
            "topic": topic,
            "difficulty": difficulty,
            "questions": questions_list
        }
