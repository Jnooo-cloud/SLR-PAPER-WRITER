import os
import time
import google.generativeai as genai
from google.api_core import exceptions

# Pool of available keys
# Try to load from .env file if it exists
def load_env_file(filepath=".env"):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

# Load .env from current directory or parent
load_env_file(".env")
load_env_file("../.env")

GEMINI_KEYS = [
    os.getenv("GEMINI_API_KEY"), # Primary key from env
]

# Support for multiple keys via env vars like GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc.
# or a comma-separated list in GEMINI_API_KEYS_LIST
if os.getenv("GEMINI_API_KEYS_LIST"):
    GEMINI_KEYS.extend([k.strip() for k in os.getenv("GEMINI_API_KEYS_LIST").split(",") if k.strip()])

# Also check for numbered keys
i = 1
while os.getenv(f"GEMINI_API_KEY_{i}"):
    GEMINI_KEYS.append(os.getenv(f"GEMINI_API_KEY_{i}"))
    i += 1

# Filter out None values and duplicates
GEMINI_KEYS = list(set([k for k in GEMINI_KEYS if k]))

class RotatableModel:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.key_index = 0
        self.configure_current_key()

    def configure_current_key(self):
        if not GEMINI_KEYS:
            print("Error: No Gemini API keys available.")
            return
        current_key = GEMINI_KEYS[self.key_index]
        # print(f"  [LLM] Using Gemini Key #{self.key_index + 1}")
        genai.configure(api_key=current_key)
        self.model = genai.GenerativeModel(self.model_name)

    def rotate_key(self):
        self.key_index = (self.key_index + 1) % len(GEMINI_KEYS)
        print(f"  [LLM] ⚠️ Quota exceeded. Rotating to Gemini Key #{self.key_index + 1}...")
        self.configure_current_key()

    def generate_content(self, prompt, **kwargs):
        """
        Wrapper for generate_content with auto-rotation on 429 errors.
        """
        max_retries = len(GEMINI_KEYS) * 2 # Try cycling through keys twice
        
        for attempt in range(max_retries):
            try:
                return self.model.generate_content(prompt, **kwargs)
            except exceptions.ResourceExhausted:
                self.rotate_key()
                time.sleep(2) # Brief pause after rotation
            except Exception as e:
                # If it's a 429 but not caught by ResourceExhausted (sometimes happens)
                if "429" in str(e) or "quota" in str(e).lower():
                    self.rotate_key()
                    time.sleep(2)
                else:
                    raise e # Re-raise other errors
        
        raise Exception("All API keys exhausted.")
