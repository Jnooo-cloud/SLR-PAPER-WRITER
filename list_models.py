import google.generativeai as genai
import os

def list_models():
    key = "AIzaSyBgka9RZlcBN_GHwHeuUdOlF1zifEwCrIA" # Key 1
    if not key:
        print("No API key found.")
        return
    genai.configure(api_key=key)
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)

if __name__ == "__main__":
    list_models()
