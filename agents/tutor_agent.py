import torch
from typing import Optional
from langchain_huggingface import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from langchain_core.messages import SystemMessage, HumanMessage
from memory.storage import Storage
from prompts.teaching_prompt import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

class TutorAgent:
    def __init__(self, storage: Optional[Storage] = None):
        self.storage = storage if storage else Storage()

        print("⏳ Loading Tutor AI Model...")
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
            max_new_tokens=512,
            # --- CRITICAL FIXES BELOW ---
            temperature=0.1,        # Very low: Forces it to be factual, not creative
            do_sample=True,
            return_full_text=False,
            repetition_penalty=1.03 # LOWERED: 1.15 was breaking words. 1.03 is safe.
        )

        self.llm = HuggingFacePipeline(pipeline=pipe)
        print("✅ Tutor Agent Ready!")

    def respond(self, query: str) -> str:
        results = self.storage.query(query, k=3)
        if results:
            context = "\n\n".join([doc.page_content for doc in results])
        else:
            context = "No specific context found."

        full_prompt = f"<|system|>\n{SYSTEM_PROMPT.format(context=context)}\n<|end|>\n<|user|>\n{USER_PROMPT_TEMPLATE.format(question=query)}\n<|end|>\n<|assistant|>"
        return self.llm.invoke(full_prompt)

    def explain_concept(self, concept: str, difficulty: int = 3, context: str = "") -> str:
        query = f"Explain the concept: {concept}. (Target difficulty: Level {difficulty}/5)"
        return self.respond(query)

    def answer_question(self, question: str, course_context: str = "") -> str:
        return self.respond(question)
