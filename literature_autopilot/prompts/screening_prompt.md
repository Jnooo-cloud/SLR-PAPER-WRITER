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

---

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

**P (Population)**: Large Language Models (LLMs) (e.g., GPT-3, PaLM, LLaMA).
**I (Intervention)**: 
- **Self-Referential Prompting (SRP)**: The model prompts itself to improve.
- **Reflective Evaluation (RE)**: The model generates feedback on its own output.
- **Iterative Self-Correction / Debate (ISCD)**: A loop where the model (or multiple instances) critiques and refines the output.
- *CRITICAL*: Must involve a **LOOP** or **ITERATIVE** process. Single-pass prompting is EXCLUDED.
**C (Comparator)**: 
- Standard Prompting (Zero-shot/Few-shot).
- Chain-of-Thought (CoT) without reflection.
- Other baselines (e.g., supervised fine-tuning).
- *CRITICAL*: Must have a baseline comparison.
**O (Outcome)**: 
- **Accuracy/Performance**: Improvement on benchmarks (GSM8K, HumanEval, etc.).
- **Hallucination Reduction**: Factuality improvements.
- **Reasoning Quality**: Better logic or coherence.
- **Safety/Alignment**: Reduced toxicity or better adherence to rules.

---

### EXCLUSION CRITERIA (If ANY are true, EXCLUDE):
1. **No Feedback Loop**: Standard CoT, simple prompt engineering, or RAG without self-correction.
2. **Human-in-the-Loop**: RLHF or methods requiring human feedback during inference.
3. **Training Only**: Methods that only improve *weights* (fine-tuning) without inference-time self-improvement (unless it's self-play fine-tuning).
4. **No Empirical Data**: Opinion pieces, pure theory without experiments.
5. **Wrong Topic**: General LLM papers not focused on self-improvement/correction.

---

### TASK:
Analyze the provided paper (Title + Abstract) and decide: **INCLUDE** or **EXCLUDE**.

**Step-by-Step Analysis (Chain-of-Thought):**
1. **Analyze Intervention**: Does it use SRP, RE, or ISCD? Is there a loop?
2. **Analyze Comparator**: Is there a baseline?
3. **Analyze Outcome**: Are quantitative improvements reported?
4. **Check Exclusions**: Does it violate any exclusion criteria?

**Output Format (JSON ONLY):**
{
    "analysis": "Brief step-by-step analysis...",
    "decision": "INCLUDE" or "EXCLUDE",
    "confidence": 0.0 to 1.0,
    "reasoning": "Final justification for the decision."
}
