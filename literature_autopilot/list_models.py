import google.generativeai as genai
from llm_utils import RotatableModel

def list_models():
    print("Listing available models...")
    try:
        # Initialize RotatableModel to configure the key
        model_wrapper = RotatableModel("gemini-1.5-flash") 
        
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Name: {m.name}")
                print(f"  Display Name: {m.display_name}")
                print(f"  Version: {m.version}")
                print("-" * 20)
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
