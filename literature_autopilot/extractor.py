import os
import json
import time
import google.generativeai as genai
from typing import Dict, Optional
from llm_utils import RotatableModel

class SLRExtractor:
    def __init__(self, model_name: str = "gemini-1.5-pro-latest"):
        self.model = RotatableModel(model_name)

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
        prompt_screening = """
        You are an expert SLR assistant. Analyze the attached paper based on our protocol.

        ### Inclusion Criteria:
        1.  **Primary Study**: Proposes or empirically evaluates a method.
        2.  **Intervention Focus**: Explicitly investigates Self-Referential Prompting, Reflective Evaluation, or Iterative Self-Correction/Debate with a clear feedback LOOP.
        3.  **Empirical Evidence**: Provides quantitative results (tables, charts).
        4.  **Comparison**: MUST compare against a non-self-improvement baseline (e.g., CoT, Zero-shot).

        ### Exclusion Criteria:
        - Off-topic (general RLHF/fine-tuning without a loop).
        - No empirical data or no valid baseline comparison.

        Decide if this paper should be INCLUDED or EXCLUDED. Provide a brief reason.

        ### Output Format (JSON ONLY)
        {
            "screening_decision": "INCLUDE" or "EXCLUDE",
            "reason": "..."
        }
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
        prompt_extraction = """
        You are an expert SLR data extractor. The attached paper has been pre-screened for inclusion. Your task is to perform a detailed Quality Assessment and Data Extraction based on our rigorous protocol.

        **Research Question**: "Welche methodischen Unterschiede bestehen zwischen den aktuellen Ansätzen und welche Verbesserungen können jeweils erzielt werden?"

        --- 
        ### 1. Quality Assessment
        Evaluate the study's quality based on our specific criteria. Assign a score (High/Medium/Low) and provide a justification.

        - **Q1 (Validation Rigor)**: How extensively was the method validated? (e.g., number of datasets, tasks, models). High = multiple datasets AND models.
        - **Q2 (Protocol Transparency)**: Are key hyperparameters reported? (e.g., base LLM, temperature, number of debate rounds N, prompt engineering details).
        - **Q3 (Bias Mitigation)**: For debate/multi-agent studies, were measures taken to mitigate judge biases (e.g., positional bias, verbosity bias, answer swapping)?

        --- 
        ### 2. Data Extraction
        Extract the following data points into a structured JSON format. Be precise and extract quantitative values where available.

        - **Study Details**: Title, Authors, Year, Venue.
        - **Mechanism**: The specific self-improvement mechanism used.
        - **Methodology**: The core components of the mechanism.
        - **Protocol Parameters**: Key parameters that define the experimental setup.
        - **Tasks & Datasets**: The specific tasks and datasets used for evaluation.
        - **Baselines**: The comparison baselines used in the study.
        - **Outcomes**: The quantitative results achieved.

        --- 
        ### 3. Output Format (JSON ONLY)
        {
          "quality_assessment": {
            "overall_score": "High/Medium/Low",
            "justification": "...",
            "validation_rigor": "...",
            "protocol_transparency": "...",
            "bias_mitigation": "..."
          },
          "data": {
            "study_details": {
              "title": "...",
              "authors": ["..."],
              "year": 2024,
              "venue": "..."
            },
            "mechanism": {
              "type": "Self-Referential | Reflective | Debate",
              "specific_name": "e.g., Self-Refine, SPP, Cognitive Synergy"
            },
            "methodology": {
              "description": "A concise summary of how the mechanism works.",
              "feedback_loop": "Describe the explicit feedback/refinement loop."
            },
            "protocol_parameters": {
              "base_llms": ["e.g., GPT-4, Mixtral-8x-7B"],
              "agent_setup": "e.g., Single-agent, Multi-agent with 3 debaters",
              "iterations_or_rounds": "e.g., 5 rounds, 3 refinement steps",
              "prompting_techniques": ["e.g., best-of-N sampling, critique-and-refinement augmentation"]
            },
            "evaluation": {
              "tasks_and_domains": ["e.g., GSM8K (Arithmetic), QuALITY (Comprehension)"],
              "baselines_compared_against": ["e.g., CoT, Single Agent"]
            },
            "outcomes": [
              {
                "metric": "e.g., Accuracy, Elo Rating, PGR",
                "task": "e.g., GSM8K",
                "baseline_name": "e.g., CoT",
                "baseline_score": 75.2,
                "method_score": 81.5,
                "improvement_comment": "Achieved a 6.3 point absolute improvement."
              }
            ]
          }
        }
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
