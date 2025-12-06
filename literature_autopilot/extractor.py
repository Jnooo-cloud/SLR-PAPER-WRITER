import os
import json
import time
import google.generativeai as genai
from typing import Dict, Optional
from literature_autopilot.llm_utils import RotatableModel

class SLRExtractor:
    def __init__(self, model_name: str = "gemini-1.5-pro-latest", 
                 prescreening_prompt_path: str = None, 
                 extraction_prompt_path: str = None):
        self.model = RotatableModel(model_name)
        self.prescreening_prompt = None
        self.extraction_prompt = None
        
        if prescreening_prompt_path and os.path.exists(prescreening_prompt_path):
            with open(prescreening_prompt_path, "r") as f:
                self.prescreening_prompt = f.read()
                
        if extraction_prompt_path and os.path.exists(extraction_prompt_path):
            with open(extraction_prompt_path, "r") as f:
                self.extraction_prompt = f.read()

    def process_paper(self, pdf_path: str) -> Dict:
        """
        Executes the Two-Stage SLR Protocol:
        1. Pre-Screening (Fast Include/Exclude)
        2. Detailed Extraction (Quality Assessment + Structured Data)
        """
        print(f"Processing PDF: {pdf_path}...")
        
        # Upload PDF to Gemini
        try:
            uploaded_file = genai.upload_file(pdf_path)
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(2)
                uploaded_file = genai.get_file(uploaded_file.name)
        except Exception as e:
            print(f"  Error uploading PDF: {e}")
            return {"error": str(e)}

        # --- Stage 1: Pre-Screening ---
        print("  [Stage 1] Pre-Screening...")
        
        # Use loaded prompt or fallback (though fallback is removed for brevity, assume config is correct)
        prompt_screening = self.prescreening_prompt if self.prescreening_prompt else """
        You are an expert SLR assistant. Analyze the attached paper based on our protocol.
        Decide if this paper should be INCLUDED or EXCLUDED. Provide a brief reason.
        Output Format (JSON ONLY): {"screening_decision": "INCLUDE" or "EXCLUDE", "reason": "..."}
        """
        
        try:
            response = self.model.generate_content([prompt_screening, uploaded_file])
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3]
            screening_result = json.loads(text)
            
            if screening_result.get("screening_decision") != "INCLUDE":
                print(f"  Excluded in Stage 1: {screening_result.get('reason')}")
                return screening_result
                
        except Exception as e:
            print(f"  Stage 1 failed: {e}")
            return {"error": f"Stage 1 Error: {str(e)}"}

        # --- Stage 2: Detailed Extraction ---
        print("  [Stage 2] Detailed Extraction & Quality Assessment...")
        
        prompt_extraction = self.extraction_prompt if self.extraction_prompt else """
        You are an expert SLR data extractor. Extract comprehensive, structured data.
        """

        
        try:
            response = self.model.generate_content([prompt_extraction, uploaded_file])
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3]
            extraction_result = json.loads(text)
            
            # Merge screening decision into final result
            extraction_result["screening_decision"] = "INCLUDE"
            return extraction_result
            
        except Exception as e:
            print(f"  Stage 2 failed: {e}")
            return {"error": f"Stage 2 Error: {str(e)}"}
