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
        You are an expert SLR data extractor. The attached paper has been pre-screened for inclusion.
        Your task is to extract comprehensive, structured data that answers the core research question:
        "Welche methodischen Unterschiede bestehen zwischen den aktuellen Ansätzen und welche 
        Verbesserungen können jeweils erzielt werden?"

        This extraction MUST focus on TWO dimensions:
        1. METHODISCHE UNTERSCHIEDE: How does this approach differ from others?
        2. VERBESSERUNGEN: What quantifiable improvements does it achieve?

        ---

        ### SECTION 1: QUALITY ASSESSMENT (Using AMSTAR 2 Lite for SLRs)

        Evaluate the study quality based on these criteria:

        **Q1 (Validation Rigor)**: How extensively was the method validated?
        - Score: HIGH = 3+ datasets/tasks AND 2+ LLM models
        - Score: MEDIUM = 2 datasets/tasks OR 2 models
        - Score: LOW = 1 dataset/task AND 1 model
        - Justification: Cite specific datasets/models used

        **Q2 (Protocol Transparency)**: Are key hyperparameters reported?
        - Check for: Base LLM name, temperature, max_tokens, debate rounds, prompt engineering details
        - Score: HIGH = All parameters explicitly reported
        - Score: MEDIUM = Most parameters reported
        - Score: LOW = Severely incomplete (missing >30% of expected parameters)
        - Justification: List which parameters are missing

        **Q3 (Bias Mitigation)**: For multi-agent studies, are biases addressed?
        - Check for: Answer swapping, word limits, position randomization, multiple judges, judge diversity
        - Score: HIGH = 2+ bias mitigation measures
        - Score: MEDIUM = 1 measure
        - Score: LOW = No measures
        - Justification: List which measures are present

        **Q4 (Baseline Appropriateness)**: Is the comparison baseline suitable?
        - Check: Is it a non-self-improvement baseline? (Zero-shot, CoT, Single Agent, etc.)
        - Score: HIGH = Appropriate non-self-improvement baseline
        - Score: MEDIUM = Baseline present but potentially weak
        - Score: LOW = No baseline or inappropriate baseline
        - Justification: Describe the baseline

        **Overall Quality Score**: HIGH / MEDIUM / LOW
        - HIGH: Scores of HIGH on Q1, Q2, Q3, Q4
        - MEDIUM: Mix of HIGH and MEDIUM scores
        - LOW: Multiple LOW scores

        ---

        ### SECTION 2: METHODOLOGICAL DIFFERENCES EXTRACTION

        This section directly addresses "Welche methodischen Unterschiede..."

        **2.1 Mechanism Type**
        - Type: "Self-Referential Prompting" / "Reflective Evaluation" / "Iterative Self-Correction/Debate"
        - Specific Name: (e.g., Self-Refine, SPP, Cognitive Synergy, etc.)

        **2.2 Core Methodology**
        - Description: How does the mechanism work? (2-3 sentences)
        - Key Innovation: What is novel compared to standard approaches?
        - Feedback Loop: Describe the explicit loop (input → process → output → feedback → input)

        **2.3 Methodological Differences from Baselines**
        CRITICAL: Explicitly state HOW this differs from the baseline approach.
        - Baseline Mechanism: What does the baseline do?
        - This Approach Mechanism: What does this approach do differently?
        - Key Differences: List 3-5 specific methodological differences
          * Example: "Unlike CoT, this approach includes a self-critique phase"
          * Example: "Differs from single-agent by using 3 debaters with positional randomization"

        **2.4 Protocol Parameters**
        - Base LLMs: [List all LLMs tested]
        - Agent Setup: (Single-agent, Multi-agent with N agents, etc.)
        - Iterations/Rounds: (e.g., 5 refinement rounds, 3 debate rounds)
        - Prompting Techniques: [List all techniques used]
        - Temperature & Sampling: (if reported)
        - Other Hyperparameters: [Any other relevant parameters]

        ---

        ### SECTION 3: IMPROVEMENTS EXTRACTION

        This section directly addresses "Welche Verbesserungen können jeweils erzielt werden?"

        **3.1 Evaluation Setup**
        - Tasks & Domains: [List all tasks/datasets]
        - Metrics: [List all metrics used]
        - Number of Runs: (if reported)
        - Statistical Significance: (if reported)

        **3.2 Baseline Comparison Results**
        For EACH task and EACH metric, extract:

        {
          "task": "Task name (e.g., GSM8K)",
          "metric": "Metric name (e.g., Accuracy)",
          "baseline_name": "Name of baseline (e.g., CoT)",
          "baseline_score": 75.2,
          "method_score": 81.5,
          "absolute_improvement": 6.3,
          "relative_improvement_percent": 8.4,
          "improvement_comment": "Achieved a 6.3 point absolute improvement (8.4% relative)"
        }

        **3.3 Synthesis of Improvements**
        - Overall Improvement Pattern: Does the method consistently improve over baseline?
        - Best Performance: On which task/metric does it perform best?
        - Worst Performance: On which task/metric is improvement smallest?
        - Consistency: Is improvement consistent across datasets/models?

        **3.4 Failure Cases or Limitations**
        - Does the paper report cases where the method underperforms?
        - Are there tasks where the method fails?
        - What limitations are acknowledged?

        ---

        ### SECTION 4: COMPARATIVE ANALYSIS

        **4.1 Comparison with Other Self-Improvement Methods**
        If the paper compares against other self-improvement methods (not just baselines):
        - Method A: Name and key characteristics
        - Method B: Name and key characteristics
        - Comparison: How do they differ? Which performs better?

        **4.2 Generalization Analysis**
        - Does the method generalize across different LLMs?
        - Does it generalize across different tasks/domains?
        - Are there domain-specific limitations?

        ---

        ### OUTPUT FORMAT (JSON ONLY):

        {
          "screening_decision": "INCLUDE",
          "quality_assessment": {
            "overall_score": "HIGH / MEDIUM / LOW",
            "validation_rigor": "HIGH / MEDIUM / LOW",
            "protocol_transparency": "HIGH / MEDIUM / LOW",
            "bias_mitigation": "HIGH / MEDIUM / LOW",
            "baseline_appropriateness": "HIGH / MEDIUM / LOW",
            "justification": "Detailed explanation of scores"
          },
          "methodological_differences": {
            "mechanism_type": "SRP / RE / ISCD",
            "specific_name": "e.g., Self-Refine",
            "core_methodology": "Description of how it works",
            "key_innovation": "What is novel",
            "feedback_loop": "Description of the loop",
            "differences_from_baseline": [
              "Difference 1",
              "Difference 2",
              "Difference 3"
            ],
            "protocol_parameters": {
              "base_llms": ["GPT-4", "Mixtral-8x-7B"],
              "agent_setup": "Multi-agent with 3 debaters",
              "iterations_or_rounds": "5 rounds",
              "prompting_techniques": ["best-of-N sampling", "critique-and-refinement"]
            }
          },
          "improvements": {
            "evaluation_setup": {
              "tasks_and_domains": ["GSM8K", "QuALITY"],
              "metrics": ["Accuracy", "F1-score"],
              "number_of_runs": 3,
              "statistical_significance": "Reported"
            },
            "baseline_comparisons": [
              {
                "task": "GSM8K",
                "metric": "Accuracy",
                "baseline_name": "CoT",
                "baseline_score": 75.2,
                "method_score": 81.5,
                "absolute_improvement": 6.3,
                "relative_improvement_percent": 8.4,
                "improvement_comment": "Achieved a 6.3 point absolute improvement"
              }
            ],
            "synthesis": {
              "overall_pattern": "Consistent improvement across all tasks",
              "best_performance": "GSM8K with 8.4% improvement",
              "worst_performance": "QuALITY with 2.1% improvement",
              "consistency": "High consistency across datasets"
            },
            "failure_cases": "None reported"
          },
          "comparative_analysis": {
            "comparison_with_other_methods": "If applicable",
            "generalization": "Analysis of generalization across LLMs and tasks"
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
