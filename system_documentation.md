# System Documentation: Automated SLR & Paper Factory

This document describes the exact process, prompts, and rules implemented in the `literature_autopilot` system. It is generated based on the actual code in the repository.

## 1. System Overview

The system is an autonomous pipeline designed to conduct a Systematic Literature Review (SLR) on "LLM Self-Improvement" and generate a high-quality scientific paper. It operates in 5 phases:

1.  **Search & Discovery**: Keyword search + Snowballing.
2.  **Screening**: LLM-based filtering using Chain-of-Thought (CoT).
3.  **Data Extraction**: Full-text analysis and structured data extraction.
4.  **Paper Generation**: Structure design and section-by-section writing.
5.  **Multi-Agent Review**: Iterative critique and improvement of every written section.

---

## 2. Phase 1: Search & Discovery

**Source**: `slr_bot.py`, `snowballing.py`

### Keywords
The system searches Semantic Scholar and ArXiv for the following terms:
*   "Self-Referential Prompting"
*   "Reflective Evaluation"
*   "Iterative Self-Correction"
*   "LLM Debate"
*   "Self-Improvement LLM"

### Snowballing Strategy
The system performs **Forward** (citations) and **Backward** (references) snowballing starting from these seed papers:
1.  "Self-Correction in Large Language Models"
2.  "Self-Refine: Iterative Refinement with Self-Feedback"
3.  "Improving Factuality and Reasoning in Language Models through Multiagent Debate"
4.  "Self-Discover: Large Language Models Self-Compose Reasoning Structures"

**Limit**: Max 50 results per snowballing step to prevent explosion.

---

## 3. Phase 2: Automated Screening

**Source**: `screener.py`

The system uses a **Chain-of-Thought (CoT)** prompt to screen papers based on Title and Abstract.

### The Exact Prompt (`SCREENING_PROMPT_COT`)

```text
You are an expert research assistant conducting a Systematic Literature Review (SLR) on the topic: "LLM Self-Improvement".
Your goal is to screen the following paper with HIGH ACCURACY based on the defined review protocol.

### Research Question (RQ) & PICO Criteria:
The paper must address the core of the RQ: "Welche methodischen Unterschiede bestehen zwischen den aktuellen Ansätzen und welche Verbesserungen können jeweils erzielt werden?"

| Element | Description (LLM Self-Improvement) | Key Indicators (MUST be present) |
| :--- | :--- | :--- |
| **P (Population)** | Large Language Models (LLMs). | LLM, Large Language Model, GPT, Llama, Mistral, etc. |
| **I (Intervention)** | Self-Improvement Mechanisms. | Must fit one of: 1) Self-Referential Prompting (Prompt optimization), 2) Reflective Evaluation (Self-critique/feedback), 3) Iterative Self-Correction/Debate (Dialog/Multi-agent). |
| **C (Comparison)** | Methodological Differences & Baselines. | Comparison between different self-improvement methods OR comparison against standard baselines (CoT, Zero-shot). Focus on *how* they differ methodologically. |
| **O (Outcomes)** | Improvements (Verbesserungen). | Quantitative gains (Accuracy, etc.) OR Qualitative improvements (Efficiency, Autonomy, Robustness). |

### Inclusion Criteria (ALL must be met):
1.  **Primary Study & Peer-Reviewed Focus**: The paper is a primary study (proposing or empirically evaluating a method) and not a secondary source (survey, review, position paper, vision paper).
2.  **Intervention Focus (I)**: The paper explicitly investigates one of the defined 'Self-Improvement' or 'Debate/Reflection' mechanisms for LLMs.
3.  **Empirical Evidence (O)**: The paper provides quantitative, empirical results (tables, charts, metrics) that measure the 'Outcome' and compare the 'Intervention' against a 'Comparison' baseline.

### Exclusion Criteria (ANY one excludes the paper):
1.  **Irrelevant Topic**: Focuses on general LLM training, fine-tuning, or RLHF *without* a clear self-correction/reflection loop. Also excludes non-LLM AI or psychology studies.
2.  **Lack of Detail/Quality**: Is an extended abstract, short workshop paper, or preprint *without* detailed experimental results and methodology (i.e., not a full, peer-review-ready paper).
3.  **No Empirical Data**: Purely conceptual papers or proposals without any quantitative results.
4.  **Language**: Non-English.

### Instructions (Chain-of-Thought):
Think step-by-step in the "analysis" field. Your reasoning MUST cite specific phrases from the abstract to support your conclusions.
[...Steps 1-5 detailing PICO Check, Empirical Comparison, Study Type, Final Evaluation...]
```

---

## 4. Phase 3: Data Extraction

**Source**: `extractor.py`

The system downloads the full PDF and runs a **3-Step Protocol** using Gemini.

### The Exact Prompt

```text
You are an expert researcher conducting a rigorous Systematic Literature Review (SLR) on "LLM Self-Improvement".

**Research Question**: "Welche methodischen Unterschiede bestehen zwischen den aktuellen Ansätzen und welche Verbesserungen können jeweils erzielt werden?"

Your task is to analyze the attached full-text paper and perform the following 3 steps strictly.

---
### Step 1: Full-Text Screening (Study Selection)
Decide if this paper should be INCLUDED or EXCLUDED based on:
- **Include**: Paper discusses/evaluates Self-Referential Prompting, Reflective Evaluation, or Iterative Self-Correction/Debate.
- **Exclude**: Off-topic, no relevant mechanism.

---
### Step 2: Quality Assessment (Bias Check)
(Only if INCLUDED) Evaluate the study quality:
1. **Selection Bias**: Are comparison groups comparable?
2. **Performance Bias**: Was the intervention consistent?
3. **Transparency**: Are hyperparameters reported?
4. **Validation**: Tested on multiple tasks/datasets?

Assign a **Quality Score** (High/Medium/Low) and brief justification.

---
### Step 3: Data Extraction
(Only if INCLUDED) Extract data to answer the RQ:
- **Study Details**: Title, Authors, Year, Venue.
- **Mechanism Type**: (Self-Referential / Reflective / Debate).
- **Methodological Details**: How does the mechanism work? (The "Methodische Unterschiede").
- **Improvements**: What specific improvements were achieved? (The "Verbesserungen").
- **Tasks/Domains**: Where was it tested?

---
### Output Format (JSON ONLY)
[JSON Schema...]
```

---

## 5. Phase 4: Paper Generation

**Source**: `paper_writer.py`

### Step 1: Structure Generation
**Prompt**:
```text
You are an elite scientific writer. We are writing a comprehensive 50-page Systematic Literature Review (SLR) on "LLM Self-Improvement".

Here is the data extracted from {N} relevant papers:
{JSON Data}

Please design a detailed, academic structure (Outline) for this paper.
The structure must be suitable for a high-impact publication (A+ level).

Requirements:
1.  **Length**: The content must be sufficient for ~50 pages.
2.  **Structure (Strictly following SLR Reporting Protocol)**:
    *   Abstract
    *   1. Introduction (Context, Goal, RQ)
    *   2. Methodology (Protocol Description)
    *   3. Analysis of Core Mechanisms (Structured Comparison)
    *   4. Discussion (Synthesis of Differences & Improvements)
    *   5. Conclusion
    *   Bibliography
3.  **Detail**: For each section, provide a brief bullet point of what papers/data will be discussed.
```

### Step 2: Section Writing
**Prompt**:
```text
You are writing the section: "**{section_title}**" for our SLR on LLM Self-Improvement.

**Global Context**: {previous_summary}

**Instructions**: {section_instructions}

**Source Material**: {JSON Data}

**Task**:
Write this section in full, academic, scientific prose. 
- **Citation Style**: Strict APA format (Author, Year).
- **Citation Normalization**: Use official venue names, not ArXiv.
- **Evidence**: Every claim MUST be backed by a citation.
- Be critical, analytical, and rigorous.
- Target length: ~1000-2000 words.
```

---

## 6. Phase 5: Multi-Agent Review

**Source**: `reviewer.py`

Every section written by the `PaperWriter` is passed through this loop.

### Agent 1: The Critic
**Prompt**:
```text
You are a strict, senior academic reviewer for a top-tier Computer Science conference (e.g., NeurIPS, ICLR).
Your goal is to ensure the paper is "A+ quality" (Accept/Oral presentation level).

**Section**: {section_name}

**Review Criteria**:
1.  **Clarity & Flow**: Is the argument logical and easy to follow?
2.  **Rigor**: Are claims supported by evidence/citations?
3.  **Novelty/Insight**: Does it go beyond summarizing to provide synthesis?
4.  **Academic Tone**: Is the language precise, objective, and formal?

**Draft Text**: {draft}

**Task**:
Provide a constructive critique. Output ONLY the critique.
```

### Agent 2: The Editor
**Prompt**:
```text
You are a Senior Editor for a top academic journal.

**Goal**: Rewrite the following draft section to address the Reviewer's critique and elevate it to "A+ quality".

**Section**: {section_name}

**Original Draft**: {draft}

**Reviewer's Critique**: {critique}

**Instructions**:
- Rewrite the text to be more rigorous, clear, and insightful.
- Fix the specific issues raised by the reviewer.
- Maintain the original core information/citations but improve the presentation.
- Ensure the tone is highly professional and academic.

Output ONLY the rewritten text.
```
