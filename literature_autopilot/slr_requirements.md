# SLR Requirements & Methodology

## Phase 1: Planning the Review

### 1.0 Context
Die Gestaltung von Prompts, das sogenannte Prompt-Engineering, beeinflusst maßgeblich sowohl die Effizienz von Large Language Models (LLMs) als auch die Qualität der erzeugten Antworten. Indem Prompts gezielt formuliert werden, lässt sich das Verhalten von LLMs steuern, was in gewisser Weise einer Form des Trainings gleichkommt.
Ein bemerkenswerter Aspekt dieser Technik ist die Möglichkeit, dass Sprachmodelle ihre eigenen Ausgaben als Eingaben für weitere Verarbeitungsschritte nutzen können (Chaining). Dadurch eröffnen sich neue Perspektiven auf selbstadaptierende Systeme. Insbesondere das Potenzial, LLMs zur eigenständigen Optimierung ihrer Prompts und der dahinterliegenden Strategien zu nutzen, weist den Weg zu selbstreferenziellen, sich kontinuierlich verbessernden KI-Systemen.
Diese Entwicklungen werden mit den Begriffen self-referential, self-improvement, reflection bezeichnet. Sie markieren einen vielversprechenden Schritt in Richtung autonomer, agentischer Sprachmodelle und stellen ein zentrales Forschungsthema im Bereich moderner KI-Architekturen dar.

### 1.1 Need & Protocol
- **Goal**: Ziel ist es, eine fundierte, systematische Wissensbasis zu den Mechanismen von self-improvement, self-referential und reflection in LLMs zu schaffen, die als Grundlage für die Entwicklung autonomer, lernfähiger und selbstadaptiver LLM-Agenten dient.
- **Protocol**: Defined here and implemented in `slr_bot.py` and `screener.py`.

### SLR Requirements & Protocol

## 1. Context & Goal
**Context**: Die Gestaltung von Prompts (Prompt-Engineering) beeinflusst Effizienz und Qualität von LLMs. Neue Entwicklungen (Self-referential, Self-improvement, Reflection) ermöglichen es Modellen, ihre eigenen Ausgaben als Eingaben zu nutzen (Chaining) und sich eigenständig zu optimieren. Dies ist ein Schritt in Richtung autonomer, agentischer Sprachmodelle.

**Goal**: Ziel ist es, eine fundierte, systematische Wissensbasis zu den Mechanismen von self-improvement, self-referential und reflection in LLMs zu schaffen, die als Grundlage für die Entwicklung autonomer, lernfähiger und selbstadaptiver LLM-Agenten dient.

## 2. Research Question (RQ)
**RQ**: "Welche methodischen Unterschiede bestehen zwischen den aktuellen Ansätzen und welche Verbesserungen können jeweils erzielt werden?"

## 3. Methodology (Vorgehen)
Zur Beantwortung dieser Frage wird ein strukturierter Vergleich bestehender Self-Improvement-Techniken durchgeführt, mit Fokus auf drei Kernmechanismen:

1.  **Self-Referential Prompting**: Modelle generieren eigenständig neue Prompts oder modifizieren bestehende Eingaben auf Basis eigener Ausgaben.
2.  **Reflective Evaluation**: Modelle bewerten und hinterfragen ihre eigenen Antworten, typischerweise durch explizite „Reflection Prompts“ oder externe Feedback-Schleifen.
3.  **Iterative Self-Correction / Debate Mechanismen**: Modelle nutzen dialogbasierte Strukturen (z. B. LLM Debates), um konkurrierende Antworten zu erzeugen, zu vergleichen und auf ein besseres Ergebnis zu konvergieren.

## 4. Material (Seed Papers)
*   https://evjang.com/2023/03/26/self-reflection.html
*   https://aclanthology.org/2024.naacl-long.15/
*   https://composable-models.github.io/llm_debate/
*   https://arxiv.org/abs/2402.06782

### 1.4 Search Strategy
- **Keywords**:
    - `LLM` OR `Large Language Model`
    - AND (`Self-Improvement` OR `Self-Correction` OR `Self-Refine` OR `Reflexion` OR `Reflection`)
    - AND (`Debate` OR `Multiagent` OR `Solo Performance Prompting` OR `Cognitive Synergy`)
- **Sources**: Semantic Scholar, arXiv (via API).
- **Snowballing**: Backward & Forward from Seed Papers.

### 1.5 Selection Criteria
- **Inclusion**:
    - Peer-reviewed primary studies.
    - Empirically investigate the impact of identified mechanisms (Self-Improvement, Debate, Reflection) on LLM performance.
- **Exclusion**:
    - Informal literature reviews without defined methodology.
    - Purely conceptual works without empirical evaluation.
    - Non-English papers.

## Phase 2: Conducting the Review

### 2.1 Identification & Selection
- Automated search and screening via `slr_bot.py`.
- LLM-based screening using `screener.py` with Chain-of-Thought.

### 2.2 Quality Assessment (To be done manually/semi-automated)
- Validation quality (multiple tasks/datasets?).
- Protocol transparency (model parameters, prompts?).
- Bias mitigation (positional bias, verbosity bias?).

### 2.3 Data Extraction (Target for future automation)
- Study details, Methodology, Protocol parameters, Base LLMs, Optimization details, Tasks, Outcomes.

## Phase 3: Reporting
- Structure: Context, Objectives, Methods, Results, Conclusions.
- Visualizations: Elo-ratings, Accuracy gaps.
