import os
import json
import time
from typing import Dict, Optional
import google.generativeai as genai
from search_modules import Paper
from llm_utils import RotatableModel

# Chain-of-Thought Prompt for higher accuracy
SCREENING_PROMPT_COT = """
You are an expert research assistant conducting a Systematic Literature Review (SLR) on the topic: "LLM Self-Improvement".
Your goal is to screen the following paper with HIGH ACCURACY based on the defined review protocol.

### Research Question (RQ) & PICO Criteria:
The paper must address the core of the RQ: "Welche methodischen Unterschiede bestehen zwischen den aktuellen Ansätzen und welche Verbesserungen können jeweils erzielt werden?"

| Element | Description (LLM Self-Improvement) | Key Indicators (MUST be present) |
| :--- | :--- | :--- |
| **P (Population)** | Large Language Models (LLMs). | LLM, Large Language Model, GPT, Llama, Mistral, etc. |
| **I (Intervention)** | Self-Improvement Mechanisms with explicit feedback loops. | Must fit ONE of: 1) Self-Referential Prompting (e.g., prompt optimization, prompt generation by model), 2) Reflective Evaluation (e.g., self-critique, self-feedback, reflection prompts), 3) Iterative Self-Correction/Debate (e.g., LLM Debates, Solo Performance Prompting, Self-Refine, multi-agent dialogue). **CRITICAL: Must describe an explicit self-improvement LOOP/CYCLE where model output feeds back as input for refinement. General prompt engineering or one-shot optimization does NOT qualify.** |
| **C (Comparison)** | Methodological Differences & Baselines. | MUST compare against at least ONE baseline WITHOUT the specific self-improvement mechanism: Single Agent, Zero-shot, Few-shot, or Chain-of-Thought (CoT) without the self-improvement loop. Comparing only different self-improvement methods against each other is INSUFFICIENT. |
| **O (Outcomes)** | Improvements (Verbesserungen). | Quantitative metrics: Accuracy, Factuality, Reasoning Quality, Hallucination Reduction, Persuasiveness (e.g., Elo-Rating), or Performance Gap Recovered (PGR). Qualitative improvements must be explicitly measured, not just claimed. |

### Inclusion Criteria (ALL must be met):
1.  **Primary Study & Peer-Reviewed Focus**: The paper is a primary study (proposing or empirically evaluating a method) and not a secondary source (survey, review, position paper, vision paper).
2.  **Intervention Focus (I)**: The paper explicitly investigates ONE of the defined Self-Improvement mechanisms with an explicit feedback/refinement loop for LLMs.
3.  **Empirical Evidence (O)**: The paper provides quantitative, empirical results (tables, charts, metrics) that measure the Outcome and compare the Intervention against a non-self-improvement baseline.
4.  **Quality Standards (Preliminary)**: 
    - VALIDATION: Method tested on at least 2 different datasets/tasks OR multiple LLM models
    - TRANSPARENCY: Key parameters clearly specified (e.g., debate rounds, agent types, temperature, model names)
    - BIAS MITIGATION: For debate/multi-agent studies, measures taken against judge biases (e.g., answer swapping, word limits)

### Exclusion Criteria (ANY one excludes the paper):
1.  **Irrelevant Topic**: Focuses on general LLM training, fine-tuning, or RLHF *without* explicit self-correction/reflection loop. Also excludes non-LLM AI, psychology studies, or significantly different domains (e.g., pure machine translation, image captioning).
2.  **Lack of Detail/Quality**: Is an extended abstract, short workshop paper, or preprint without detailed experimental results and methodology. OR lacks validation across multiple datasets/tasks/models. OR has severely incomplete methodological reporting (missing key parameters).
3.  **No Empirical Data**: Purely conceptual papers or proposals without quantitative results.
4.  **Insufficient Comparison**: Only compares different self-improvement methods against each other without a non-self-improvement baseline. OR compares against weak/non-standard baselines.
5.  **Language**: Non-English.

### Paper Details:
- **Title**: {title}
- **Abstract**: {abstract}

### Instructions (Chain-of-Thought):
Think step-by-step in the "analysis" field. Your reasoning MUST cite specific phrases from the abstract to support your conclusions.

**Step 1: Population Check (P)**
- Does the paper study Large Language Models (LLMs)?
- Look for explicit mentions: "LLM", "Large Language Model", "GPT", "Llama", "Mistral", etc.
- If NO: EXCLUDE immediately.
- If YES: Continue to Step 2.

**Step 2: Intervention Check (I) - Critical**
- Does the paper propose or evaluate ONE of the three self-improvement mechanisms?
  - Self-Referential Prompting: Model generates/modifies prompts based on its own output
  - Reflective Evaluation: Model critiques/evaluates its own responses
  - Iterative Self-Correction/Debate: Multi-agent dialogue, debate, or iterative refinement loops
- **CRITICAL: Is there an explicit feedback loop where output feeds back as input for refinement?**
  - Example of VALID loop: "The model generates a response, then critiques it, then refines it based on the critique"
  - Example of INVALID: "We use prompt engineering to optimize the prompt" (no loop)
- Cite specific phrases from abstract/intro that describe the mechanism.
- If NO explicit loop or mechanism: EXCLUDE.
- If YES: Continue to Step 3.

**Step 3: Comparison Check (C) - Critical**
- Does the paper compare the self-improvement method against a non-self-improvement baseline?
- Acceptable baselines: Single Agent, Zero-shot, Few-shot, CoT (without self-improvement)
- Check abstract/results for baseline comparisons.
- If ONLY comparing different self-improvement methods (e.g., Debate vs. Self-Refine) without a non-self-improvement baseline: EXCLUDE.
- If NO comparison or only weak baselines: EXCLUDE.
- If YES (valid baseline present): Continue to Step 4.

**Step 4: Empirical Evidence Check (O)**
- Does the paper provide quantitative results (tables, charts, metrics)?
- Are outcomes measured in terms of: Accuracy, Factuality, Reasoning, Hallucinations, Persuasiveness, or PGR?
- Look for specific numbers, percentages, or statistical comparisons.
- If purely conceptual or qualitative only: EXCLUDE.
- If YES (quantitative results present): Continue to Step 5.

**Step 5: Quality & Transparency Check**
- VALIDATION: Is the method tested on at least 2 different datasets/tasks OR multiple LLM models?
  - If only 1 dataset and 1 model: FLAG as lower confidence or EXCLUDE if combined with other weaknesses.
- TRANSPARENCY: Are key parameters clearly reported?
  - For Debate: Number of rounds, agent types, judge selection
  - For Self-Critique: Critique prompt design, feedback mechanism
  - For Self-Refine: Refinement strategy, iterations
  - General: Base LLM models, temperature, sampling, dataset sizes
  - If severely incomplete: FLAG as lower confidence.
- BIAS MITIGATION (for multi-agent studies): Are measures taken against judge biases?
  - If NO measures and multi-agent: FLAG as lower confidence.
- If multiple quality issues: Consider EXCLUSION.

**Step 6: Study Type Check**
- Is this a primary study (proposing/evaluating a method) or secondary (survey, review, position paper)?
- If secondary: EXCLUDE.
- If primary: Continue to Step 7.

**Step 7: Language Check**
- Is the paper in English?
- If NO: EXCLUDE.
- If YES: Continue to Step 8.

**Step 8: Final Decision**
- Summarize findings from Steps 1-7.
- Decision: INCLUDE, EXCLUDE, or FLAG (for manual review).
- Provide confidence level: HIGH, MEDIUM, LOW.
- Cite key evidence from the paper.

### Output Format:
Provide your response in valid JSON format with the following keys:
- "analysis": "Step-by-step reasoning citing specific phrases from the abstract..."
- "decision": "INCLUDE" or "EXCLUDE"
- "confidence": A score between 0.0 and 1.0 (Reflects certainty based on abstract detail)
- "reason": A brief summary of the decision.
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
