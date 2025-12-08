import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from memory.storage import Storage  # Assuming you have this

class LectureParser:
    """
    Owner: B
    Purpose: Parse course material files
    """

    def __init__(self, storage=None):
        # Internal logic is allowed (like setting up storage)
        self.storage = storage if storage else Storage()
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    # --- MUST MATCH INTERFACE BELOW ---
    def parse(self, file_path: str) -> dict:
        """
        Parse course material
        Returns: { 'title': str, 'chapters': [ ... ] }
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.endswith(".pdf"):
            raise ValueError("File format not supported")

        # Your Logic
        reader = PdfReader(file_path)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text: full_text += text + "\n"

        # Your Side Effect (Storing to DB) - This is fine to keep!
        chunks = self.text_splitter.create_documents([full_text])
        self.storage.add_documents(chunks)

        # REQUIRED RETURN FORMAT
        return {
            'title': os.path.basename(file_path),
            'chapters': [
                {
                    'id': 'chap_1',
                    'name': 'Extracted Content',
                    'content': full_text,
                    'key_concepts': []
                }
            ]
        }
