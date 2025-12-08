from __future__ import annotations
import os
import shutil
from collections import defaultdict
from typing import DefaultDict, Dict, List, Optional

# --- NEW IMPORTS (Fixes Warnings) ---
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# --- Core Import ---
from core import MasterySample

class Storage:
    def __init__(self) -> None:
        # --- PART 1: Mastery Storage ---
        self._data: DefaultDict[str, DefaultDict[str, List[MasterySample]]] = (
            defaultdict(lambda: defaultdict(list))
        )

        # --- PART 2: Vector DB Storage ---
        self.embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.persist_dir = "./chroma_db"

        self.db = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embedding_function
        )

    # --- Mastery Operations ---
    def append_mastery_sample(self, sample: MasterySample) -> None:
        self._data[sample.user_id][sample.topic_id].append(sample)

    def get_samples(self, user_id: str, topic_id: str) -> List[MasterySample]:
        return list(self._data[user_id][topic_id])

    def get_topics(self, user_id: str) -> List[str]:
        return list(self._data[user_id].keys())

    # --- Vector DB Operations ---
    def add_documents(self, documents):
        if documents:
            self.db.add_documents(documents)
            print(f"Stored {len(documents)} chunks to vector database.")

    def query(self, question: str, k: int = 3):
        if not self.db: return []
        return self.db.similarity_search(question, k=k)
