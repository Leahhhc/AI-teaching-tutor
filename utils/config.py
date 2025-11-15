"""
Configuration Management Module
"""
import os
from pathlib import Path

# load dotenv locally
if os.getenv("HF_SPACE") is None:  
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass


class Config:
    """Global Configuration"""
    
    # Project paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    COURSES_DIR = DATA_DIR / "courses"
    USER_DATA_DIR = DATA_DIR / "user_progress"
    
    # --- Model Selection ---
    MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Meta-Llama-3.1-8B-Instruct")
    
    # --- Hugging Face API ---
    HF_API_TOKEN = os.getenv("HF_API_TOKEN", None)  # None if not provided
    HF_API_BASE = "https://router.huggingface.co/hf-inference"
    
    @classmethod
    def get_api_url(cls):
        """Compose full URL for HuggingFace inference"""
        return f"{cls.HF_API_BASE}/{cls.MODEL_NAME}"
    
    # --- Model Parameters ---
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    TOP_P = float(os.getenv("TOP_P", "0.9"))
    
    # --- Local model option ---
    USE_LOCAL_MODEL = os.getenv("USE_LOCAL_MODEL", "False").lower() == "true"
    LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", "")
    
    # --- Learning configuration ---
    DEFAULT_DIFFICULTY = 3
    MIN_MASTERY_THRESHOLD = 0.7
    QUIZ_QUESTIONS_COUNT = 5
    
    # --- Logging ---
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def ensure_directories(cls):
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.COURSES_DIR.mkdir(exist_ok=True)
        cls.USER_DATA_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def validate(cls):
        """Safe validation (does not crash in HF Space)"""
        
        cls.ensure_directories()
        
        if cls.USE_LOCAL_MODEL:
            if not cls.LOCAL_MODEL_PATH:
                print("[Config Warning] LOCAL_MODEL_PATH is empty while USE_LOCAL_MODEL=True")
        
        else:
            if not cls.HF_API_TOKEN:
                print("[Config Warning] Missing HF_API_TOKEN. API calls will fail.")
                print("Set it in HuggingFace Space → Settings → Variables.")
    
    @classmethod
    def get_api_headers(cls):
        """Return headers (works even if token missing)"""
        return {
            "Authorization": f"Bearer {cls.HF_API_TOKEN}",
            "Content-Type": "application/json"
        }


# Initialize
Config.validate()
print("Config loaded. Model:", Config.MODEL_NAME)
