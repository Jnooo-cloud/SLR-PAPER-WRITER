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
- Check for: Conformity bias (agents agreeing blindly), Order bias (first speaker advantage)
- Score: HIGH = Explicit mitigation strategies used (e.g., blind voting, role swapping)
- Score: MEDIUM = Mentioned but not fully addressed
- Score: LOW = Not mentioned
- Score: N/A = Single-agent study

**Q4 (Novelty & Generalization)**:
- Novelty: Is this a new architecture or just a prompt tweak? (High/Medium/Low)
- Generalization: Tested on OOD (Out-of-Distribution) tasks? (Yes/No)
- Reproducibility: Code available? (Yes/No/Link)

**OVERALL QUALITY SCORE**: Calculate based on Q1-Q3.
- HIGH: All High or 2 High + 1 Medium
- MEDIUM: Mixed
- LOW: 1+ Low

---

### SECTION 2: STRUCTURED DATA EXTRACTION (JSON)

Extract the following fields precisely.

1.  **Metadata**:
    *   `title`: Full title.
    *   `authors`: List of authors.
    *   `year`: Publication year.
    *   `venue`: Conference/Journal (if available).
    *   `citations`: Citation count (if mentioned).

2.  **Methodological Differences (The "How")**:
    *   `mechanism_type`: Choose ONE: "Self-Referential Prompting", "Reflective Evaluation", "Iterative Self-Correction/Debate".
    *   `specific_name`: Name of the method (e.g., "Reflexion", "Self-Refine", "MAD").
    *   `feedback_source`: "Self" (same model), "External" (other model/tool), "Human".
    *   `iteration_strategy`: "Fixed count" (e.g., 3 rounds) or "Dynamic" (until convergence).
    *   `key_innovation`: What makes this specific method unique? (1-2 sentences).
    *   `architecture_details`: Brief description of the flow (e.g., "Generator -> Critic -> Refiner").

3.  **Improvements (The "What")**:
    *   `baseline_comparisons`: List of comparisons. Each item:
        *   `task`: Task name (e.g., GSM8K).
        *   `baseline_model`: Model used as baseline (e.g., GPT-4 Zero-shot).
        *   `method_model`: Model used with this method.
        *   `metric`: Metric name (e.g., Accuracy).
        *   `baseline_score`: Score of baseline.
        *   `method_score`: Score of this method.
        *   `improvement_absolute`: (method_score - baseline_score).
        *   `improvement_relative_percent`: ((method_score - baseline_score) / baseline_score) * 100.
    *   `synthesis`:
        *   `overall_pattern`: Summary of where it works best (e.g., "Great for math, bad for creative writing").
        *   `limitations`: Reported failure modes (e.g., "High cost", "Latency").

---

### Output Format (JSON ONLY)
{
    "quality_assessment": {
        "q1_validation": {"score": "...", "justification": "..."},
        "q2_transparency": {"score": "...", "justification": "..."},
        "q3_bias": {"score": "...", "justification": "..."},
        "q4_novelty": {"novelty": "...", "generalization": "...", "reproducibility": "..."},
        "overall_score": "..."
    },
    "metadata": { ... },
    "methodological_differences": { ... },
    "improvements": {
        "baseline_comparisons": [ ... ],
        "synthesis": { ... }
    }
}
