import logging
import os
import json
import time
import random
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

    def _retry_with_backoff(self, func, retries=3, initial_delay=1, backoff_factor=2):
        """Helper to retry a function with exponential backoff."""
        delay = initial_delay
        last_exception = None
        
        for attempt in range(retries):
            try:
                return func()
            except Exception as e:
                last_exception = e
                logging.warning(f"    Attempt {attempt + 1}/{retries} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay + random.uniform(0, 0.5)) # Add jitter
                delay *= backoff_factor
                
        raise last_exception

    def process_paper(self, pdf_path: str) -> Dict:
        """
        Executes the Two-Stage SLR Protocol:
        1. Pre-Screening (Fast Include/Exclude)
        2. Detailed Extraction (Quality Assessment + Structured Data)
        """
        logging.info(f"Processing PDF: {pdf_path}...")
        
        # Upload PDF to Gemini
        try:
            def upload_op():
                f = genai.upload_file(pdf_path)
                # Wait for processing
                while f.state.name == "PROCESSING":
                    time.sleep(2)
                    f = genai.get_file(f.name)
                if f.state.name == "FAILED":
                    raise ValueError(f"File processing failed: {f.state.name}")
                return f

            uploaded_file = self._retry_with_backoff(upload_op, retries=3)
            
        except Exception as e:
            logging.error(f"  Error uploading PDF after retries: {e}")
            return {"error": str(e)}

        # --- Stage 1: Pre-Screening ---
        logging.info("  [Stage 1] Pre-Screening...")
        
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
                logging.info(f"  Excluded in Stage 1: {screening_result.get('reason')}")
                return screening_result
                
        except Exception as e:
            logging.error(f"  Stage 1 failed: {e}")
            return {"error": f"Stage 1 Error: {str(e)}"}

        # --- Stage 2: Detailed Extraction ---
        logging.info("  [Stage 2] Detailed Extraction & Quality Assessment...")
        
        prompt_extraction = self.extraction_prompt if self.extraction_prompt else """
        You are an expert SLR data extractor. Extract comprehensive, structured data.
        """

        
        try:
            response = self.model.generate_content([prompt_extraction, uploaded_file])
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3]
            extraction_result = json.loads(text)
            
            # --- Stage 3: AMSTAR 2 Assessment ---
            amstar_result = self._run_amstar_assessment(uploaded_file)
            extraction_result["amstar_2_assessment"] = amstar_result
            
            # --- Stage 4: Validation ---
            validation_errors = self.validate_extracted_data(extraction_result)
            extraction_result["validation_errors"] = validation_errors
            if validation_errors:
                logging.warning(f"  Validation Errors for {pdf_path}: {validation_errors}")

            # Merge screening decision into final result
            extraction_result["screening_decision"] = "INCLUDE"
            return extraction_result
            
        except Exception as e:
            logging.error(f"  Stage 2/3 failed: {e}")
            return {"error": f"Extraction Error: {str(e)}"}

    AMSTAR_2_ITEMS = [
        "PICO components in research question",
        "Study design selection criteria",
        "Comprehensive search strategy",
        "Study selection process",
        "Data extraction process",
        "List of excluded studies with reasons",
        "Study characteristics reported",
        "Risk of bias assessment",
        "Funding sources reported",
        "Conflicts of interest reported",
        "Heterogeneity assessment",
        "Appropriate synthesis method",
        "Risk of bias in results interpretation",
        "Heterogeneity discussion",
        "Publication bias assessment",
        "Conflict of interest in review"
    ]

    def _run_amstar_assessment(self, uploaded_file) -> Dict:
        logging.info("  [Quality] Running AMSTAR 2 Assessment...")
        prompt = f"""
        You are a Quality Assurance Auditor. Assess the attached paper using the AMSTAR 2 checklist.
        Note: If this is a PRIMARY STUDY (not a review), some items may be 'NOT APPLICABLE'.
        
        ITEMS TO ASSESS:
        {json.dumps(self.AMSTAR_2_ITEMS, indent=2)}
        
        For each item, determine if the paper satisfies it (YES / NO / PARTIAL / NA).
        Provide a brief justification.
        
        Output Format (JSON ONLY):
        {{
            "Q1": {{"status": "YES", "reason": "..."}},
            ...
            "overall_score": "HIGH / MODERATE / LOW / CRITICALLY LOW"
        }}
        """
        try:
            response = self.model.generate_content([prompt, uploaded_file])
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3]
            return json.loads(text)
        except Exception as e:
            logging.error(f"  AMSTAR Assessment failed: {e}")
            return {"error": str(e)}

    def validate_extracted_data(self, data: Dict) -> list[str]:
        """Validates the extracted data for consistency and plausibility."""
        errors = []
        
        # Plausibility checks
        for comp in data.get("improvements", {}).get("baseline_comparisons", []):
            baseline = comp.get("baseline_score")
            method = comp.get("method_score")
            
            # Try to convert to float if string
            try:
                if isinstance(baseline, str): baseline = float(baseline.replace("%", ""))
                if isinstance(method, str): method = float(method.replace("%", ""))
                
                if baseline and not (0 <= baseline <= 100):
                    errors.append(f"Invalid baseline_score: {baseline}")
                if method and not (0 <= method <= 100):
                    errors.append(f"Invalid method_score: {method}")
            except:
                pass # Ignore parsing errors for now
        
        # Check for required fields
        required_fields = ["paper_title", "Year", "Authors"]
        # Note: paper_title is added later in pipeline, so check others
        if not data.get("Year"): errors.append("Missing Year")
        
        return errors
