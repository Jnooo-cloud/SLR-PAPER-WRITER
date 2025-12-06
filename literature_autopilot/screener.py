import os
import json
import time
from typing import Dict, Optional
import google.generativeai as genai
from literature_autopilot.search_modules import Paper
from literature_autopilot.llm_utils import RotatableModel

# Chain-of-Thought Prompt for higher accuracy
SCREENING_EXAMPLES = """
### EXAMPLES OF INCLUSION vs. EXCLUSION:

**EXAMPLE 1: INCLUDE**
- Title: "Self-Refine: Iterative Refinement with Self-Feedback"
- Abstract mentions: "model generates feedback to refine its own responses iteratively"
- Decision: INCLUDE (Reflective Evaluation with explicit feedback loop)

**EXAMPLE 2: EXCLUDE**
- Title: "Prompt Engineering for Better LLM Performance"
- Abstract mentions: "optimized prompts for better performance"
- Decision: EXCLUDE (No feedback loop, one-shot optimization)

**EXAMPLE 3: INCLUDE**
- Title: "Multi-Agent Debate for Code Generation"
- Abstract mentions: "multiple agents debate and converge on a solution"
- Decision: INCLUDE (ISCD with multiple iterations)

**EXAMPLE 4: EXCLUDE**
- Title: "Fine-tuning LLMs with RLHF"
- Abstract mentions: "human feedback to improve model weights"
- Decision: EXCLUDE (RLHF requires human-in-the-loop, not autonomous self-improvement)
"""

# Chain-of-Thought Prompt for higher accuracy
SCREENING_PROMPT_COT = """
You are an expert research assistant conducting a rigorous Systematic Literature Review (SLR) 
on "LLM Self-Improvement" following PRISMA 2020 standards.

**CRITICAL RESEARCH QUESTION**: 
"Welche methodischen Unterschiede bestehen zwischen den aktuellen Ansätzen und welche 
Verbesserungen können jeweils erzielt werden?"

This question has TWO components that BOTH must be addressed:
1. METHODISCHE UNTERSCHIEDE: Different approaches/mechanisms
2. VERBESSERUNGEN: Quantifiable improvements achieved

---

### PICO FRAMEWORK (ALL must be met for INCLUSION):

**P (Population)**: Large Language Models (LLMs)
- Keywords: LLM, Large Language Model, GPT, Llama, Mistral, Claude, PaLM, etc.
- Exclude: Small language models, non-neural approaches, non-LLM AI systems

**I (Intervention)**: Self-Improvement Mechanisms WITH explicit feedback loops
- Category 1: Self-Referential Prompting (SRP)
  * Model generates/modifies prompts based on own output
  * Examples: prompt optimization, self-generated instructions
  * MUST have: Explicit loop where output feeds back as input
  
- Category 2: Reflective Evaluation (RE)
  * Model critiques/evaluates its own responses
  * Examples: self-critique, reflection prompts, self-feedback
  * MUST have: Explicit evaluation mechanism with feedback
  
- Category 3: Iterative Self-Correction / Debate (ISCD)
  * Multi-agent dialogue, debate, or iterative refinement
  * Examples: LLM debate, multi-agent discussion, consensus-building
  * MUST have: Multiple iterations where outputs feed back as inputs

**CRITICAL**: Generic prompt engineering WITHOUT a feedback loop = EXCLUDE
**CRITICAL**: One-shot optimization = EXCLUDE
**CRITICAL**: RLHF or fine-tuning without explicit self-improvement loop = EXCLUDE

**C (Comparison)**: MUST compare against non-self-improvement baseline
- Acceptable baselines: Zero-shot, Few-shot, Chain-of-Thought (CoT without loop), Single Agent
- Unacceptable: Only comparing different self-improvement methods against each other
- Unacceptable: Weak or non-standard baselines (e.g., random baseline only)

**O (Outcomes)**: Quantifiable improvements
- Metrics: Accuracy, F1-score, BLEU, Factuality, Reasoning Quality, Hallucination Reduction
- Metrics: Elo-Rating, Performance Gap Recovered (PGR), Win Rate
- Qualitative improvements MUST be explicitly measured with metrics
- Exclude: Only qualitative claims without numbers

---

""" + SCREENING_EXAMPLES + """

---

### QUALITY THRESHOLDS (for preliminary assessment):

**Validation Rigor**:
- ✅ HIGH: Tested on 3+ different datasets/tasks AND 2+ different LLM models
- ⚠️ MEDIUM: Tested on 2 datasets/tasks OR 2 models
- ❌ LOW: Only 1 dataset/task AND 1 model → FLAG for potential EXCLUSION

**Protocol Transparency**:
- ✅ HIGH: All parameters explicitly reported (base LLM, temperature, debate rounds, prompt details)
- ⚠️ MEDIUM: Most parameters reported, some missing
- ❌ LOW: Severely incomplete reporting → FLAG for potential EXCLUSION

**Bias Mitigation** (for multi-agent studies):
- ✅ HIGH: Measures taken (answer swapping, word limits, position randomization, multiple judges)
- ⚠️ MEDIUM: Some measures mentioned
- ❌ LOW: No bias mitigation measures → FLAG for lower confidence

---

### CHAIN-OF-THOUGHT ANALYSIS (MANDATORY):

**Step 1: Population Check**
- Explicitly mention: Does the abstract contain LLM-related keywords?
- Quote specific phrases that confirm LLM focus.
- Decision: INCLUDE or EXCLUDE

**Step 2: Intervention Check (CRITICAL)**
- Identify which self-improvement mechanism is addressed: SRP / RE / ISCD
- Quote the specific mechanism description from the abstract
- CRITICAL: Is there an explicit feedback loop described?
  * Look for phrases like: "iterative", "feedback", "refine", "improve", "loop", "dialogue"
  * Absence of these = likely EXCLUDE
- Decision: INCLUDE or EXCLUDE

**Step 3: Comparison Check (CRITICAL)**
- Identify the baseline(s) used for comparison
- Is it a non-self-improvement baseline? (Zero-shot, CoT, Single Agent, etc.)
- Quote the comparison statement
- Decision: INCLUDE or EXCLUDE

**Step 4: Outcomes Check**
- Identify quantitative metrics reported
- Are improvements measured in numbers?
- Quote specific results (e.g., "accuracy improved from 75% to 82%")
- Decision: INCLUDE or EXCLUDE

**Step 5: Quality Assessment**
- Validation Rigor: How many datasets/tasks? How many models?
- Protocol Transparency: Are hyperparameters reported?
- Bias Mitigation: For multi-agent, are biases addressed?
- Assign: HIGH / MEDIUM / LOW confidence

**Step 6: Study Type Check**
- Is this a primary study (proposing/evaluating a method)?
- Or secondary (survey, review, position paper)?
- Decision: INCLUDE or EXCLUDE

**Step 7: Language & Completeness Check**
- Is the paper in English?
- Is it a full paper (not extended abstract)?
- Decision: INCLUDE or EXCLUDE

---

### OUTPUT FORMAT (JSON ONLY):

{
  "decision": "INCLUDE" or "EXCLUDE",
  "confidence": 0.95,  // 0.0 to 1.0
  "mechanism_type": "SRP" or "RE" or "ISCD" or "MULTIPLE",
  "analysis": {
    "population_check": "✅ PASS: Paper explicitly studies LLMs (quote: '...')",
    "intervention_check": "✅ PASS: Addresses SRP with feedback loop (quote: '...')",
    "comparison_check": "✅ PASS: Compares against CoT baseline (quote: '...')",
    "outcomes_check": "✅ PASS: Reports accuracy improvement from X% to Y%",
    "quality_assessment": {
      "validation_rigor": "HIGH / MEDIUM / LOW",
      "protocol_transparency": "HIGH / MEDIUM / LOW",
      "bias_mitigation": "HIGH / MEDIUM / LOW"
    },
    "study_type_check": "✅ PASS: Primary study",
    "language_check": "✅ PASS: English"
  },
  "reasoning": "Detailed explanation of decision with specific quotes",
  "flags": ["Optional: Any concerns or notes"]
}
"""

class PaperScreener:
    def __init__(self, provider: str = "openai", model: str = "gpt-4o"):
        self.provider = provider
        self.model_name = model
        
        if self.provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = RotatableModel(self.model_name)
            
        elif self.provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                print("Warning: GEMINI_API_KEY not found in environment variables.")
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model_name or "gemini-pro-latest")
            self.model = RotatableModel(self.model_name)
            
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def screen_paper(self, paper: Paper) -> Dict:
        """Screens a single paper using the LLM with CoT and Retries."""
        prompt = SCREENING_PROMPT_COT.format(title=paper.title, abstract=paper.abstract)
        
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                if self.provider == "openai":
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are a rigorous research assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.0
                    )
                    content = response.choices[0].message.content
                    return json.loads(content)
    
                elif self.provider == "gemini":
                    response = self.client.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                    return json.loads(response.text)
                    
            except Exception as e:
                print(f"  Error screening paper '{paper.title[:30]}...' (Attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1)) # Exponential-ish backoff
                else:
                    return {"decision": "ERROR", "confidence": 0.0, "reason": str(e), "analysis": "Error occurred after retries"}
        
        return {"decision": "ERROR", "confidence": 0.0, "reason": "Max retries exceeded", "analysis": "Error"}

    def screen_papers(self, papers: list[Paper]) -> list[Dict]:
        """Screens a list of papers."""
        results = []
        print(f"Screening {len(papers)} papers with {self.provider} ({self.model}) using Chain-of-Thought...")
        
        for i, paper in enumerate(papers):
            print(f"[{i+1}/{len(papers)}] Screening: {paper.title[:50]}...")
            result = self.screen_paper(paper)
            
            # Merge result with paper info
            paper_data = paper.to_dict()
            paper_data.update({
                "Screening Decision": result.get("decision", "ERROR"),
                "Screening Confidence": result.get("confidence", 0.0),
                "Screening Reason": result.get("reason", "Error occurred"),
                "Screening Analysis": result.get("analysis", "")
            })
            results.append(paper_data)
            
            # Rate limiting (simple sleep)
            time.sleep(4) 
            
        return results
    def screen_paper_consensus(self, paper: Paper) -> Dict:
        """
        Screens a paper using a 'Double-Blind' consensus approach.
        Runs two independent screening passes. If they disagree, a third 'Senior Editor' pass resolves it.
        """
        # Pass 1: Reviewer A
        result_a = self.screen_paper(paper)
        decision_a = result_a.get("decision", "EXCLUDE")
        reasoning_a = result_a.get("reasoning", "No reasoning provided.")

        # Pass 2: Reviewer B
        # (We rely on the non-deterministic nature of the LLM for independence, 
        # or we could slightly vary the system prompt if needed. For now, same prompt is fine.)
        result_b = self.screen_paper(paper)
        decision_b = result_b.get("decision", "EXCLUDE")
        reasoning_b = result_b.get("reasoning", "No reasoning provided.")

        # Consensus Check
        if decision_a == decision_b:
            # Agreement reached
            return result_a
        else:
            # Conflict! Trigger Senior Editor
            print(f"    [Conflict] Reviewer A: {decision_a} vs Reviewer B: {decision_b}. Resolving...")
            return self._resolve_conflict(paper, result_a, result_b)

    def _resolve_conflict(self, paper: Paper, result_a: Dict, result_b: Dict) -> Dict:
        """
        Resolves a screening conflict using a 'Senior Editor' persona.
        """
        prompt = f"""
        You are the "Senior Editor" for a Systematic Literature Review.
        Two junior reviewers have disagreed on whether to include this paper.
        Your job is to make the FINAL, BINDING decision.

        **Paper**: "{paper.title}"
        **Abstract**: "{paper.abstract}"

        **Reviewer A's Opinion**:
        Decision: {result_a.get('decision')}
        Reasoning: {result_a.get('reasoning')}

        **Reviewer B's Opinion**:
        Decision: {result_b.get('decision')}
        Reasoning: {result_b.get('reasoning')}

        **Task**:
        1.  Analyze the paper against the strict inclusion criteria (Self-Improvement Loop + Empirical Data).
        2.  Evaluate the reviewers' arguments. Who is correct?
        3.  Decide "INCLUDE" or "EXCLUDE".

        **Output Format (JSON ONLY)**:
        {{
          "decision": "INCLUDE" or "EXCLUDE",
          "reasoning": "Final binding decision rationale..."
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            # Clean markdown
            if text.startswith("```json"):
                text = text[7:-3]
            
            return json.loads(text)
        except Exception as e:
            print(f"    [Senior Editor Error] {e}")
            # Default to EXCLUDE on error to be safe
            return {"decision": "EXCLUDE", "reasoning": "Senior Editor failed to resolve conflict."}
