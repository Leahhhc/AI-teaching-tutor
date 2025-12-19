from __future__ import annotations
import os
import shutil
from collections import defaultdict
from typing import DefaultDict, Dict, List, Optional, Any
import re
import unicodedata

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
    
    def add_texts(self, texts: List[Any], metadatas: Optional[List[Dict]] = None):
        clean_texts: List[str] = []
        clean_metas: List[Dict] = []

        for i, t in enumerate(texts):
            if t is None:
                continue
            if not isinstance(t, str):
                t = str(t)

            t = self._sanitize_text(t)
            if not t:
                continue

            clean_texts.append(t)
            if metadatas:
                clean_metas.append(metadatas[i])

        if clean_texts:
            self.db.add_texts(
                texts=clean_texts,
                metadatas=clean_metas if metadatas else None
            )

    def _sanitize_text(self, s: str) -> str:
        # Normalize unicode (fixes odd PDF glyph variants)
        s = unicodedata.normalize("NFKC", s)

        # Remove null bytes and other nasty control chars (keep \n and \t)
        s = s.replace("\x00", " ")
        s = "".join(ch for ch in s if ch.isprintable() or ch in "\n\t")

        # Collapse excessive whitespace
        s = re.sub(r"[ \t]+", " ", s)
        s = re.sub(r"\n{3,}", "\n\n", s)

        return s.strip()

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
