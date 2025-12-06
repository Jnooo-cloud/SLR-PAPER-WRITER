# Umfassendes Feedback: SLR Paper Writer Agent
## Erweiterte Analyse mit Prompt-Verbesserungen und MCP-Integration

---

## TEIL 1: BEWERTUNG DEINER BESTEHENDEN SLR-METHODIK

### 1.1 Stärken deiner Methodik

Deine in `slr_requirements.md` und `ACADEMIC WRITING BEST PRACTICES GUIDE.md` dokumentierte Methodik ist **solide und gut durchdacht**. Sie zeigt ein tiefes Verständnis für wissenschaftliches Schreiben:

| Aspekt | Bewertung | Begründung |
| :--- | :--- | :--- |
| **Forschungsfrage** | ✅ Ausgezeichnet | Klar definiert: "Welche methodischen Unterschiede bestehen zwischen den aktuellen Ansätzen und welche Verbesserungen können jeweils erzielt werden?" |
| **Kernmechanismen** | ✅ Ausgezeichnet | Drei gut differenzierte Kategorien (SRP, RE, ISCD) mit klaren Definitionen |
| **PICO-Kriterien** | ✅ Sehr gut | Population, Intervention, Comparison und Outcomes sind explizit definiert |
| **Inclusion/Exclusion** | ✅ Sehr gut | Detaillierte Kriterien mit Fokus auf empirische Evidenz und Baseline-Vergleiche |
| **Akademischer Schreibstil** | ✅ Ausgezeichnet | Umfassender Guide mit konkreten Beispielen (Inverted Pyramid, Rule of Three, Hedging Language) |
| **Struktur für 50-Seiten-Paper** | ⚠️ Teilweise | Definiert ist: Abstract, Intro, Methodology, Analysis (3 Subsections), Discussion, Conclusion. Aber: Zu wenig Detail für 50 Seiten |

### 1.2 Lücken zwischen Methodik und Implementierung

Die Hauptprobleme entstehen nicht aus einer schwachen Methodik, sondern aus **unzureichender Umsetzung** dieser Methodik im Code:

| Lücke | Methodik sagt | Code tut | Auswirkung |
| :--- | :--- | :--- | :--- |
| **Suchstrategie** | Mehrere Datenbanken + systematische Keywords | Nur Semantic Scholar & arXiv | Unvollständige Literaturabdeckung |
| **Quality Assessment** | Explizite Kriterien (Validation, Transparency, Bias Mitigation) | Oberflächliche 3-Punkt-Bewertung | Schwache Qualitätskontrolle |
| **PRISMA-Konformität** | Implizit erwartet | Nicht implementiert | Fehlende Transparenz und Reproduzierbarkeit |
| **Datensynthese** | "Strukturierter Vergleich" mit Fokus auf Unterschiede | Nur Zusammenfassung der Daten | Keine tiefe kritische Analyse |
| **Figuren & Tabellen** | Erwähnt (Elo-ratings, Accuracy gaps) | Grundlegende Plots nur | Nicht aussagekräftig genug |
| **Diskussion & Limitationen** | Ausführlich dokumentiert | Minimal in Prompts | Oberflächliche Diskussionssektionen |

### 1.3 Fazit zur Methodik

**Deine Methodik ist nicht zu schwach – sie ist nur unzureichend in den Code integriert.** Die Prompts müssen deine dokumentierten Standards explizit referenzieren und durchsetzen.

---

## TEIL 2: KONKRETE VERBESSERTE PROMPT-VORSCHLÄGE

### 2.1 Verbesserter Prompt für `screener.py` (Paper Screening)

**Aktueller Status:** Der Screening-Prompt ist gut, aber zu allgemein.

**Verbesserter Prompt:**

```python
SCREENING_PROMPT_IMPROVED = """
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
```

### 2.2 Verbesserter Prompt für `extractor.py` (Data Extraction)

**Verbesserter Prompt:**

```python
EXTRACTION_PROMPT_IMPROVED = """
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
```

### 2.3 Verbesserter Prompt für `paper_writer.py` (Section Writing)

**Verbesserter Prompt für die Einleitung:**

```python
WRITE_INTRODUCTION_IMPROVED = """
You are an elite scientific writer preparing the Introduction section for a 50-page 
Systematic Literature Review on "LLM Self-Improvement".

**CRITICAL RESEARCH QUESTION**:
"Welche methodischen Unterschiede bestehen zwischen den aktuellen Ansätzen und welche 
Verbesserungen können jeweils erzielt werden?"

Your Introduction MUST:
1. Establish the CONTEXT: Why is LLM self-improvement important?
2. Identify the GAP: What do we NOT know about methodological differences?
3. State the RESEARCH QUESTION clearly
4. Preview the THREE MECHANISMS: SRP, RE, ISCD
5. Outline the PAPER STRUCTURE

---

### STRUCTURE (Inverted Pyramid):

**1.1 Context and Motivation** (2-3 pages)
- Start BROAD: The evolution of LLMs and their limitations
- Narrow DOWN: The need for self-improvement mechanisms
- Key Points:
  * LLMs have fixed architectures and cannot learn from individual interactions
  * Current approaches rely on expensive fine-tuning or RLHF
  * Self-improvement offers a path to autonomous, adaptive systems
  * This is critical for developing autonomous AI agents

- MUST include citations to establish the context
- MUST use hedging language appropriately ("research suggests", "evidence indicates")

**1.2 Core Mechanisms of LLM Self-Improvement** (3-4 pages)
Introduce the THREE mechanisms that are the focus of this review:

**1.2.1 Self-Referential Prompting (SRP)**
- Definition: Models generate or modify prompts based on their own outputs
- Key Characteristic: Operates at the PROMPT level
- Examples: Prompt optimization, self-generated instructions
- Advantage: Low computational cost, operates within a single forward pass
- Limitation: Limited to prompt-level optimization

**1.2.2 Reflective Evaluation (RE)**
- Definition: Models critique and evaluate their own responses
- Key Characteristic: Involves SELF-CRITIQUE and FEEDBACK
- Examples: Self-critique prompts, reflection-based refinement
- Advantage: Captures reasoning quality and correctness
- Limitation: Requires multiple forward passes

**1.2.3 Iterative Self-Correction / Debate (ISCD)**
- Definition: Multi-agent dialogue and iterative refinement
- Key Characteristic: Involves MULTIPLE AGENTS and DIALOGUE
- Examples: LLM debates, multi-agent consensus, iterative refinement
- Advantage: Leverages diverse perspectives and reasoning
- Limitation: High computational cost, requires careful judge selection

For EACH mechanism:
- Provide 2-3 concrete examples from the literature
- Explain the feedback loop explicitly
- Compare to standard approaches (e.g., CoT)

**1.3 Analytical Gaps in the Literature** (2-3 pages)
- What is NOT well understood about these mechanisms?
- CRITICAL: Focus on METHODOLOGICAL DIFFERENCES
  * How do different implementations of SRP differ?
  * What design choices lead to better performance?
  * How do the three mechanisms compare methodologically?
- CRITICAL: Focus on IMPROVEMENTS
  * Which mechanisms achieve the largest improvements?
  * Under what conditions do improvements generalize?
  * What are the efficiency-accuracy tradeoffs?
- Identify specific research gaps

**1.4 Research Questions and Contributions** (1-2 pages)
State your RQ clearly:
"Welche methodischen Unterschiede bestehen zwischen den aktuellen Ansätzen und welche 
Verbesserungen können jeweils erzielt werden?"

Break this into sub-questions:
- RQ1: What are the key methodological differences between SRP, RE, and ISCD?
- RQ2: How do design choices within each mechanism affect performance?
- RQ3: What improvements does each mechanism achieve over baselines?
- RQ4: How do improvements generalize across tasks and models?

State your contributions:
- Contribution 1: Systematic comparison of three mechanisms
- Contribution 2: Identification of methodological differences
- Contribution 3: Quantification of improvements
- Contribution 4: Guidance for practitioners

**1.5 Paper Outline** (0.5 pages)
Briefly outline the structure:
- Section 2: Methodology
- Section 3: Analysis of mechanisms
- Section 4: Discussion
- Section 5: Conclusion

---

### CRITICAL STYLE REQUIREMENTS:

**Language & Tone**:
- Formal, objective, academic register
- Third person ("This review examines..." NOT "We examine...")
- Past tense for findings, present tense for established facts
- NO colloquialisms, NO emotional language, NO vague intensifiers

**Sentence Structure**:
- Target 15-20 words per sentence
- Use active voice (80%+)
- Break up long sentences
- Use parallel structure for lists

**Citations**:
- EVERY claim must be backed by a citation
- Use APA format: (Author, Year)
- For 3+ authors: (Author et al., Year)
- Use "et al." with a period

**Hedging Language**:
- Strong claims: "The evidence demonstrates...", "Studies show..."
- Moderate claims: "The evidence suggests...", "Research indicates..."
- Weak claims: "The evidence may indicate...", "Some studies propose..."

**Formatting**:
- NO bold text in body
- Use *italics* sparingly for emphasis
- NO bullet points in body text
- Use full paragraphs

---

### CRITICAL CONTENT REQUIREMENTS:

- MUST answer "Why is this important?" for each mechanism
- MUST explain the feedback loop for each mechanism
- MUST cite at least 15-20 papers to establish context
- MUST be 8-10 pages long (approximately 3500-4000 words)
- MUST flow logically from broad context to specific research questions

---

### OUTPUT:

Write the complete Introduction section in Markdown format.
Include proper heading (# Introduction) at the start.
"""
```

### 2.4 Verbesserter Prompt für `reviewer.py` (Multi-Agent Review)

**Verbesserter Prompt für den Methodological Hawk:**

```python
REVIEW_METHODOLOGICAL_HAWK_IMPROVED = """
You are a notoriously pedantic academic reviewer for a top-tier venue (NeurIPS, ICLR, ACL).
Your role is to ensure METHODOLOGICAL RIGOR and PRISMA COMPLIANCE.

**SECTION BEING REVIEWED**: {section_name}
**PAPER TOPIC**: Systematic Literature Review on "LLM Self-Improvement"

---

### CRITICAL REVIEW CRITERIA:

**1. PRISMA 2020 Compliance**
- Does the section follow PRISMA 2020 guidelines?
- For Methodology section: Are all 27 items addressed?
- For Results section: Are findings presented objectively?
- For Discussion section: Are limitations discussed?
- FLAG any missing elements

**2. Research Question Alignment**
- Does this section address the RQ: "Welche methodischen Unterschiede... und welche Verbesserungen..."?
- Are BOTH dimensions (differences AND improvements) covered?
- FLAG if either dimension is missing or weak

**3. Methodological Soundness**
- Are inclusion/exclusion criteria clearly stated?
- Is the search strategy reproducible?
- Is quality assessment using validated tools?
- Are data extraction methods systematic?
- FLAG any methodological flaws

**4. Logical Consistency**
- Are there logical gaps or fallacies?
- Do conclusions follow from evidence?
- Are claims appropriately hedged?
- FLAG any logical inconsistencies

**5. Evidence Quality**
- Are claims backed by citations?
- Are citations to high-quality sources?
- Is the evidence sufficient to support claims?
- FLAG any unsupported claims

**6. Quantitative Rigor**
- Are numbers and metrics clearly reported?
- Are comparisons fair and appropriate?
- Are statistical claims well-founded?
- FLAG any quantitative errors or misleading statistics

**7. Plagiarism & Originality**
- Is the text original or copied from sources?
- Are ideas properly attributed?
- FLAG any potential plagiarism

**8. Reproducibility**
- Could another researcher reproduce the methodology?
- Are all relevant details provided?
- Are search strings, databases, tools specified?
- FLAG any missing details that prevent reproducibility

**9. Critical Analysis**
- Does the section go beyond summarization?
- Are methodological differences analyzed critically?
- Are improvements contextualized?
- FLAG if analysis is superficial

**10. Placeholder Check (FATAL ERROR)**
- FLAG ANY use of "N studies", "[Insert X]", "TBD", etc.
- These are FATAL errors that must be fixed immediately

---

### OUTPUT FORMAT:

Provide a numbered list of CRITICAL issues, organized by severity:

**FATAL ERRORS** (Must fix immediately):
1. [Issue and specific quote from text]
2. [Issue and specific quote from text]

**MAJOR ISSUES** (Significantly impact quality):
1. [Issue and specific quote from text]
2. [Issue and specific quote from text]

**MINOR ISSUES** (Polish and refinement):
1. [Issue and specific quote from text]
2. [Issue and specific quote from text]

For each issue, provide:
- The problem (specific quote if possible)
- Why it's a problem
- Suggested fix
"""
```

---

## TEIL 3: MCP-BASIERTES FINAL REVIEW SYSTEM MIT SELBSTVERBESSERUNG

### 3.1 Architektur des Systems

Das System sollte folgende Struktur haben:

```
┌─────────────────────────────────────────────────────────────┐
│                    PAPER WRITING PIPELINE                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Search & Screening → 2. Data Extraction → 3. Writing    │
│                                                               │
│                    ↓ (Final Draft Generated)                 │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │   MCP-BASED FINAL REVIEW LOOP (NEW)                  │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │                                                        │   │
│  │  Round N:                                             │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ 1. Send Paper to Manus via MCP                  │ │   │
│  │  │    - Full paper text                            │ │   │
│  │  │    - Evaluation criteria (PRISMA, A+ standards) │ │   │
│  │  │    - Specific focus areas                       │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  │                     ↓                                 │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ 2. Manus Returns Detailed Review                │ │   │
│  │  │    - Strengths & weaknesses                     │ │   │
│  │  │    - Specific improvement suggestions           │ │   │
│  │  │    - Quality score (0-100)                      │ │   │
│  │  │    - Convergence assessment                     │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  │                     ↓                                 │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ 3. Agent Analyzes Review & Decides              │ │   │
│  │  │    - Quality Score >= 90? → DONE (A+ achieved)  │ │   │
│  │  │    - Quality Score < 90? → Continue             │ │   │
│  │  │    - Extract key improvement areas              │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  │                     ↓                                 │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ 4. Agent Rewrites Paper                         │ │   │
│  │  │    - Addresses all feedback points              │ │   │
│  │  │    - Maintains structure & citations            │ │   │
│  │  │    - Improves identified weak areas             │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  │                     ↓                                 │   │
│  │  Round N+1 (repeat until quality >= 90)              │   │
│  │                                                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│                    ↓ (A+ Paper Achieved)                     │
│                                                               │
│                   FINAL OUTPUT: final_paper_A_plus.md        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Implementation Details

**Schritt 1: MCP-Client für Final Review**

```python
# literature_autopilot/mcp_final_reviewer.py

import json
from typing import Dict, Tuple
from llm_utils import RotatableModel

class MCPFinalReviewer:
    """
    Uses Manus MCP to perform final review of the paper.
    Iteratively improves the paper until A+ quality is achieved.
    """
    
    def __init__(self, model_name: str = "gemini-1.5-pro-latest"):
        self.model = RotatableModel(model_name)
        self.max_iterations = 5
        self.quality_threshold = 90  # 0-100 scale
    
    def review_paper_via_mcp(self, paper_text: str, focus_areas: list = None) -> Dict:
        """
        Send paper to Manus via MCP for comprehensive review.
        
        Args:
            paper_text: Full paper content
            focus_areas: List of areas to focus on (e.g., ["PRISMA compliance", "depth of analysis"])
        
        Returns:
            Review result with quality score and feedback
        """
        
        focus_instruction = ""
        if focus_areas:
            focus_instruction = f"\n\nPLEASE FOCUS ON: {', '.join(focus_areas)}"
        
        prompt = f"""
        You are an expert academic reviewer and editor. You are reviewing a 50-page 
        Systematic Literature Review on "LLM Self-Improvement".
        
        **EVALUATION CRITERIA**:
        1. PRISMA 2020 Compliance (27-item checklist)
        2. A+ Publication Standards (top-tier venue)
        3. Depth of Analysis (not just summarization)
        4. Methodological Rigor
        5. Academic Writing Quality
        6. Structure and Flow
        7. Citation Quality and Completeness
        8. Clarity and Precision
        
        **PAPER TO REVIEW**:
        {paper_text}
        
        {focus_instruction}
        
        **YOUR TASK**:
        Provide a comprehensive review in the following JSON format:
        
        {{
          "overall_quality_score": 0-100,  // 0=Reject, 50=Acceptable, 75=Good, 90+=A+
          "strengths": [
            "Strength 1 with specific examples",
            "Strength 2 with specific examples"
          ],
          "weaknesses": [
            {{
              "area": "Area name (e.g., 'PRISMA Compliance')",
              "severity": "CRITICAL / MAJOR / MINOR",
              "issue": "Specific issue description",
              "impact": "How this affects quality",
              "suggestion": "Specific improvement suggestion"
            }}
          ],
          "detailed_feedback": {{
            "prisma_compliance": "Assessment of PRISMA 2020 compliance",
            "depth_of_analysis": "Assessment of analytical depth",
            "methodological_rigor": "Assessment of rigor",
            "writing_quality": "Assessment of writing",
            "structure_and_flow": "Assessment of structure",
            "citation_quality": "Assessment of citations"
          }},
          "convergence_assessment": {{
            "is_converged": true/false,
            "reason": "Why the paper has/hasn't converged to A+ quality",
            "next_steps": "What should be done next"
          }},
          "priority_improvements": [
            "Top improvement 1",
            "Top improvement 2",
            "Top improvement 3"
          ]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            review_text = response.text.strip()
            
            # Parse JSON from response
            if "```json" in review_text:
                review_text = review_text.split("```json")[1].split("```")[0]
            
            review_data = json.loads(review_text)
            return review_data
            
        except Exception as e:
            print(f"Error in MCP review: {e}")
            return {
                "overall_quality_score": 0,
                "error": str(e)
            }
    
    def iterative_improvement_loop(self, paper_text: str, initial_focus_areas: list = None) -> Tuple[str, Dict]:
        """
        Iteratively improves the paper until A+ quality is achieved.
        
        Returns:
            (improved_paper_text, final_review)
        """
        
        current_paper = paper_text
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n{'='*60}")
            print(f"ITERATION {iteration}/{self.max_iterations}")
            print(f"{'='*60}")
            
            # Get review from Manus
            print("Sending paper to Manus for review...")
            review = self.review_paper_via_mcp(
                current_paper,
                focus_areas=initial_focus_areas if iteration == 1 else None
            )
            
            quality_score = review.get("overall_quality_score", 0)
            print(f"Quality Score: {quality_score}/100")
            
            # Check convergence
            if quality_score >= self.quality_threshold:
                print(f"\n✅ A+ QUALITY ACHIEVED! (Score: {quality_score}/100)")
                return current_paper, review
            
            # Extract improvements needed
            weaknesses = review.get("weaknesses", [])
            priority_improvements = review.get("priority_improvements", [])
            
            print(f"\nWeaknesses identified: {len(weaknesses)}")
            print("Priority improvements:")
            for i, improvement in enumerate(priority_improvements[:3], 1):
                print(f"  {i}. {improvement}")
            
            # Prepare rewriting prompt
            print("\nRewriting paper to address feedback...")
            rewrite_prompt = f"""
            You are a world-class academic writer. You are revising a 50-page SLR paper.
            
            **ORIGINAL PAPER**:
            {current_paper}
            
            **REVIEW FEEDBACK**:
            Quality Score: {quality_score}/100
            
            Weaknesses:
            {json.dumps(weaknesses, indent=2)}
            
            Priority Improvements:
            {json.dumps(priority_improvements, indent=2)}
            
            **YOUR TASK**:
            Rewrite the paper to address ALL feedback points. Specifically:
            1. Address each weakness mentioned above
            2. Implement all priority improvements
            3. Maintain the overall structure and citations
            4. Improve clarity, depth, and rigor
            5. Ensure PRISMA 2020 compliance
            
            Output ONLY the revised paper in Markdown format.
            Do not include commentary or explanations.
            """
            
            try:
                response = self.model.generate_content(rewrite_prompt)
                current_paper = response.text.strip()
                print("Paper revised successfully.")
            except Exception as e:
                print(f"Error during rewriting: {e}")
                return current_paper, review
        
        # Max iterations reached
        print(f"\n⚠️ Max iterations ({self.max_iterations}) reached.")
        print(f"Final quality score: {quality_score}/100")
        final_review = self.review_paper_via_mcp(current_paper)
        
        return current_paper, final_review
```

**Schritt 2: Integration in `slr_bot.py`**

```python
# In slr_bot.py, add after paper writing:

if args.final_review:
    print(f"\n--- Phase 10: Final Review & A+ Optimization (MCP) ---")
    
    if not os.path.exists("final_paper.md"):
        print("Error: final_paper.md not found. Run --write-paper first.")
        return
    
    with open("final_paper.md", "r") as f:
        paper_text = f.read()
    
    # Initialize MCP reviewer
    from mcp_final_reviewer import MCPFinalReviewer
    mcp_reviewer = MCPFinalReviewer(model_name=args.model)
    
    # Define focus areas for initial review
    focus_areas = [
        "PRISMA 2020 Compliance",
        "Depth of Analysis (methodological differences)",
        "Quantification of Improvements",
        "Critical Discussion",
        "Academic Writing Quality"
    ]
    
    # Run iterative improvement loop
    improved_paper, final_review = mcp_reviewer.iterative_improvement_loop(
        paper_text,
        initial_focus_areas=focus_areas
    )
    
    # Save improved paper
    with open("final_paper_A_plus.md", "w") as f:
        f.write(improved_paper)
    
    # Save final review
    with open("final_review.json", "w") as f:
        json.dump(final_review, f, indent=2)
    
    print(f"\n✅ Final paper saved: final_paper_A_plus.md")
    print(f"✅ Review saved: final_review.json")
    print(f"\nFinal Quality Score: {final_review.get('overall_quality_score', 'N/A')}/100")
```

**Schritt 3: Command-Line Integration**

```python
# In slr_bot.py main() function, add argument:

parser.add_argument("--final-review", action="store_true", 
                   help="Run MCP-based final review and iterative improvement")
```

### 3.3 Evaluation Criteria für MCP-Review

Der MCP-Reviewer sollte folgende Kriterien verwenden:

| Kriterium | 0-50 (Schwach) | 50-75 (Gut) | 75-90 (Sehr Gut) | 90-100 (A+) |
| :--- | :--- | :--- | :--- | :--- |
| **PRISMA Compliance** | Viele Items fehlen | Meiste Items vorhanden | Fast alle Items | Alle 27 Items vollständig |
| **Methodological Rigor** | Oberflächlich | Angemessen | Rigoros | Sehr rigoros |
| **Depth of Analysis** | Nur Zusammenfassung | Einige Analyse | Gute Analyse | Tiefe kritische Analyse |
| **Writing Quality** | Viele Fehler | Akzeptabel | Gut | Ausgezeichnet |
| **Citation Quality** | Unvollständig | Meiste vorhanden | Fast alle | Alle vollständig |
| **Structure & Flow** | Verwirrend | Logisch | Gut organisiert | Exzellent |
| **Originality & Insight** | Keine | Minimal | Einige | Substanzielle |

---

## TEIL 4: UMSETZUNGS-ROADMAP

### Phase 1: Prompt-Verbesserungen (1-2 Wochen)
1. Implementiere verbesserte Prompts für `screener.py`
2. Implementiere verbesserte Prompts für `extractor.py`
3. Implementiere verbesserte Prompts für `paper_writer.py`
4. Teste auf Beispiel-Papern

### Phase 2: MCP-Integration (2-3 Wochen)
1. Entwickle `mcp_final_reviewer.py`
2. Integriere in `slr_bot.py`
3. Teste iterative Verbesserungsschleife
4. Optimiere Prompts basierend auf Testergebnissen

### Phase 3: Erweiterte Funktionen (3-4 Wochen)
1. Verbessere Figuren-Generierung (PRISMA Flow-Diagramme)
2. Integriere Zitationsmanagement (Zotero API)
3. Erweitere Suchstrategie auf mehrere Datenbanken
4. Implementiere GRADE-Framework für Evidenzsicherheit

---

## FAZIT

Deine SLR-Methodik ist **nicht zu schwach** – sie ist nur **nicht vollständig im Code implementiert**. Durch die Umsetzung dieser Verbesserungen wirst du einen Agent haben, der tatsächlich A+ 50-Seiten-Paper produzieren kann.

Die Schlüsselinsights sind:
1. **Deine Methodik ist gut** – nutze sie explizit in den Prompts
2. **Verbesserte Prompts sind der Schlüssel** – sie müssen deine Standards durchsetzen
3. **MCP-basiertes Final Review** – ermöglicht echte Qualitätskontrolle und iterative Verbesserung
4. **Automatische Selbstverbesserung** – der Agent kann sich selbst optimieren bis A+ erreicht ist
