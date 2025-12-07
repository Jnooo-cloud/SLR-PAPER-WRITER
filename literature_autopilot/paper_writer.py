import logging
import os
import json
import google.generativeai as genai
import requests
from typing import List, Dict
from literature_autopilot.reviewer import MultiAgentReviewer
from literature_autopilot.llm_utils import RotatableModel

class PaperWriter:
    STYLE_GUIDELINES = """
    **ACADEMIC WRITING BEST PRACTICES (STRICT ENFORCEMENT):**
    
    1.  **Structure & Hierarchy**:
        *   Follow the **Inverted Pyramid**: Introduction (Broad) -> Methods (Specific) -> Results (Data) -> Discussion (Interpretation) -> Conclusion (Broad).
        *   **Max 3 levels of nesting** (e.g., 1.2.1 is max). Do NOT use 1.1.1.1.
        *   **Paragraph Structure (Rule of Three)**:
            *   Sentence 1: **Topic Sentence** (State main idea).
            *   Sentences 2-4: **Supporting Evidence** (Data, citations, details).
            *   Sentence 5: **Concluding Sentence** (Summarize/Transition).
    
    2.  **Language & Tone**:
        *   **Register**: Formal, objective, academic.
        *   **Prohibited**: Colloquialisms ("stuff", "basically"), vague intensifiers ("very", "really"), emotional language ("unfortunately").
        *   **Perspective**: Use Third Person ("The study found...") or "We" only for methodology ("We conducted..."). Avoid "I".
        *   **Tense**: Use **PAST TENSE** for results/methodology ("We analyzed...", "The study found..."). Use Present Tense for established facts ("LLMs are...").
    
    3.  **Formatting & Style**:
        *   **No Bullet Points** in Introduction, Discussion, or Conclusion. Use full paragraphs.
        *   **No Bold Text** for emphasis. Use *italics* sparingly.
        *   **Figures**: Captions must be below figures (e.g., "Figure 1: ...").
        *   **Placeholders**: **NEVER** use placeholders like "N studies" or "[Insert number]". You MUST use the actual data provided (e.g., "30 studies").
    
    4.  **Content Specifics**:
        *   **Exclusion Criteria**: Explicitly distinguish "autonomous" vs "human-in-the-loop" (e.g., RLHF is excluded because it requires human feedback).
        *   **Novelty**: Define novelty clearly (e.g., "new feedback signal", "new domain").
    """

    def __init__(self, model_name: str = "gemini-1.5-pro-latest"):
        self.model = RotatableModel(model_name)
        self.reviewer = MultiAgentReviewer(model_name)
        self.s2_api_key = None # Optional: Add S2 API key if available

    def _get_official_venue(self, title: str) -> str:
        """
        Attempts to find the official publication venue (e.g. 'NeurIPS 2024') 
        using Semantic Scholar, to replace 'ArXiv' citations.
        """
        try:
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {"query": title, "limit": 1, "fields": "venue,year,publicationVenue"}
            headers = {"x-api-key": self.s2_api_key} if self.s2_api_key else {}
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("data"):
                    paper = data["data"][0]
                    # Prefer full venue name
                    venue = paper.get("publicationVenue", {}).get("name")
                    if not venue:
                        venue = paper.get("venue")
                    
                    if venue and venue.lower() != "arxiv":
                        return f"{venue} {paper.get('year', '')}"
        except Exception:
            pass
        return "ArXiv" # Fallback

    def generate_structure(self, extracted_data: List[Dict]) -> str:
        """
        Generates a detailed outline for the 50-page paper based on extracted data.
        """
        logging.info("Generating paper structure...")
        
        # Summarize the extracted data to fit in context if needed, 
        # but Gemini 1.5 Pro has huge context so we might pass a lot.
        # Let's create a consolidated summary string.
        data_summary = json.dumps(extracted_data[:20], indent=2) # Limit to 20 to save tokens, but usually enough for structure
        
        prompt = f"""
        You are an elite scientific writer and senior editor (100+ published papers). 
        We are writing a comprehensive Systematic Literature Review (SLR) on "LLM Self-Improvement".
        
        Here is a sample of the data extracted from the included studies:
        {data_summary}
        
        Please design a detailed, academic structure (Outline) for this paper.
        The structure must be suitable for a high-impact publication (A+ level).
        
        {self.STYLE_GUIDELINES}

        Requirements:
        1.  **Length**: The content must be sufficient for ~50 pages.
        2.  **Structure (Strictly following Critique Guidelines)**:
            *   **Abstract** (Max 200 words, concise, no citations, NO placeholders)
            *   **1. Introduction**
                *   1.1 Context and Motivation
                *   1.2 Core Mechanisms of LLM Self-Improvement
                    *   1.2.1 Self-Referential Prompting
                    *   1.2.2 Reflective Evaluation
                    *   1.2.3 Iterative Self-Correction / Debate
                *   1.3 Analytical Gaps in the Literature
                *   1.4 Research Questions and Contributions (Use paragraph format, no bullet points)
                *   1.5 Paper Outline
            *   **2. Methodology**
                *   Protocol Description (Search, Screening, Quality Assessment)
                *   **Explicitly state N={len(extracted_data)} studies** (Do not use "N").
            *   **3. Analysis of Core Mechanisms** (Structured Comparison)
                *   3.1 Self-Referential Prompting (Methodological details & Improvements)
                *   3.2 Reflective Evaluation (Methodological details & Improvements)
                *   3.3 Iterative Self-Correction / Debate (Methodological details & Improvements)
            *   **4. Discussion**
                *   Synthesis of Methodological Differences
                *   Synthesis of Achieved Improvements
                *   Implications for Autonomous Agents
            *   **5. Conclusion**
            *   **Bibliography** (APA)
        3.  **Detail**: For each section, provide a brief bullet point of what papers/data will be discussed.
        
        Output the structure in Markdown format.
        """
        
        response = self.model.generate_content(prompt)
        return response.text

    def write_section(self, section_title: str, section_instructions: str, relevant_data: List[Dict], previous_sections_summary: str = "", skip_review: bool = False) -> str:
        """
        Writes a single section of the paper.
        """
        logging.info(f"Writing section: {section_title}...")
        
        # Enrich data with official venue info for citations
        for paper_data in relevant_data:
            if paper_data.get("Source") == "arXiv" or "arxiv" in str(paper_data.get("Source", "")).lower():
                official_venue = self._get_official_venue(paper_data.get("Title", ""))
                if official_venue != "ArXiv":
                    paper_data["OfficialVenue"] = official_venue
                    logging.info(f"  [Citation Normalizer] Found official venue for '{paper_data.get('Title')[:20]}...': {official_venue}")

        context_str = json.dumps(relevant_data, indent=2)
        
        # --- STYLE GUIDELINES ---
        STYLE_GUIDELINES = """
        **CRITICAL STYLE RULES (ZERO TOLERANCE FOR ROBOTIC PROSE):**
        1.  **BANNED WORDS**: Do NOT use the following words/phrases. They are hallmarks of AI writing and will cause immediate rejection:
        1.  **Academic Tone**: Use formal, objective, and precise language. Avoid "AI-sounding" fluff (e.g., "delve", "tapestry", "paramount", "crucial").
        2.  **No Bullet Points**: Do NOT use bullet points in the body text (Introduction, Analysis, Discussion). Use full paragraphs.
        3.  **No Bold Emphasis**: Do NOT use **bold** for emphasis. Use *italics* if absolutely necessary, but sparingly.
        4.  **Figure Labels**: Always use "Figure X" (e.g., "Figure 1"), NEVER "Abb. X".
        5.  **Sentence Length**: Keep sentences concise (max 25 words). Break up long sentences.
        6.  **Citation Format**: Use APA style (Author, Year). For >2 authors, use "et al." (with a dot). NEVER use "etajl", "ets al", or "et al" without a dot.
        7.  **Consistency**: Ensure the number of analyzed studies stated in the text matches the provided data exactly.
        """

        if "Introduction" in section_title:
             prompt = f"""
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

            **Source Material**:
            {context_str}

            **Task**:
            Write the complete Introduction section in Markdown format.
            Include proper heading (# Introduction) at the start.
            """
        else:
            prompt = f"""
            You are writing the section: "**{section_title}**" for our SLR on LLM Self-Improvement.
            
            **Global Context (What has been written so far)**:
            {previous_sections_summary}
            
            **Goal**: 
            - Ensure a smooth logical transition from the previous sections.
            - Reference concepts established earlier in the Global Context to build a cohesive narrative.
            - For Conclusions/Discussion, synthesize findings from ALL previous sections.
            
            **Instructions for this section**: {section_instructions}
    
            **SPECIAL INSTRUCTION FOR ABSTRACT**:
            - **MAXIMUM LENGTH**: 200 words. STRICT LIMIT.
            - **CONTENT**: Context -> Gap -> Solution -> Results (Key Metrics only) -> Implication.
            - **BAN**: Do NOT include specific search strings, database names, or detailed method descriptions.
            
            **Source Material**:
            {context_str}
            
            **Task**:
            Write this section in full, academic, scientific prose. 
            
            {self.STYLE_GUIDELINES}
    
            **CRITICAL CONTEXT**:
            - This is a **Systematic Literature Review (SLR)**.
            - **Methodology Section**: MUST describe the Search Strategy, Screening Criteria, and Data Extraction. **DO NOT** describe a survey, participants, or experimental study.
            - **Analysis Section**: Analyze the *included papers*.
            
            **Additional Requirements**:
            - **Citation Style**: Strict APA format (Author, Year).
            - **Citation Normalization**: Use official venue names, not ArXiv.
            - **Evidence**: Every claim MUST be backed by a citation.
            - **Detail**: Be extremely detailed. Expand on every point. Use examples.
            - **Detail & Substance**: To achieve the required length without "fluff", you must:
              *   **Synthesize** findings from multiple papers (don't just list them).
              *   **Contrast** conflicting results or methodologies.
              *   **Deep Dive** into technical specifics (architectures, prompt templates, error modes).
              *   **Use Examples**: Describe specific experiments or case studies from the data in detail.
            - **Length Goal**: Aim for **comprehensive depth** (~800-1000 words). If you run out of things to say, **do not repeat yourself**. Instead, analyze the *implications* or *limitations* more deeply.
            - **Anti-Fluff**: Do not use vague generalizations. Every paragraph must contain specific information derived from the extracted data.
            - **Figures**: If writing the 'Methodology' section, you MUST include:
              `![Figure 1: Distribution of Included Studies by Year](images/figure_1_year_distribution.png)`
              Refer to it in the text (e.g., "As shown in Figure 1...").
            - **Figures**: If writing the 'Analysis' section (Section 3), you MUST include:
              `![Figure 2: Distribution of Self-Improvement Mechanisms](images/figure_2_mechanism_distribution.png)`
              Refer to it in the text.
            - Be critical, analytical, and rigorous.
            - **Connect back** to the previous section's findings to build a cumulative argument.
            - Do NOT write the whole paper, JUST this section.
            """
        
        response = self.model.generate_content(prompt)
        draft_text = response.text
        
        # --- Multi-Agent Review Loop ---
        if not skip_review:
            logging.info(f"  [Multi-Agent Reviewer] Critiquing and improving '{section_title}'...")
            final_text = self.reviewer.review_section(section_title, draft_text, source_data=relevant_data)
        else:
            logging.info(f"  [Multi-Agent Reviewer] Skipping review for '{section_title}' (Draft Only)...")
            final_text = draft_text
        
        # --- POST-PROCESSING ENFORCEMENT ---
        # Forcefully remove em-dashes if the LLM ignored the prompt
        if "—" in final_text or "--" in final_text:
            logging.info(f"  [Style Enforcer] Removing em-dashes from '{section_title}'...")
            final_text = final_text.replace("—", ", ").replace(" -- ", ", ").replace("--", ", ")
            # Fix any double commas created by replacement
            final_text = final_text.replace(", ,", ",").replace(" ,", ",")
            
        # Ensure Section Header Exists
        if not final_text.strip().startswith("#"):
            logging.info(f"  [Structure Enforcer] Prepending missing header for '{section_title}'...")
            if section_title.lower() in ["abstract", "introduction", "methodology", "discussion", "conclusion"]:
                final_text = f"# {section_title}\n\n{final_text}"
            else:
                final_text = f"## {section_title}\n\n{final_text}"
        
        # Validation
        length_status = self.validate_section_length(section_title, final_text)
        if "WARNING" in length_status:
            logging.warning(f"  [Length Check] {length_status}")
            # Optional: Trigger expansion loop if critically short
            
        return final_text

    DETAILED_STRUCTURE = {
        "Abstract": {
            "target_words": 200,
            "sections": ["Background", "Methods", "Results", "Conclusion"]
        },
        "1. Introduction": {
            "target_pages": 3,
            "subsections": [
                "1.1 Context and Motivation",
                "1.2 Core Mechanisms",
                "1.2.1 Self-Referential Prompting",
                "1.2.2 Reflective Evaluation",
                "1.2.3 Iterative Self-Correction/Debate",
                "1.3 Research Gaps",
                "1.4 Research Questions",
                "1.5 Paper Outline"
            ]
        },
        "2. Methodology": {
            "target_pages": 5,
            "subsections": [
                "2.1 Protocol Registration",
                "2.2 Search Strategy",
                "2.3 Inclusion/Exclusion Criteria",
                "2.4 Study Selection Process",
                "2.5 Data Extraction",
                "2.6 Quality Assessment (AMSTAR 2)",
                "2.7 Synthesis Methods"
            ]
        },
        "3. Analysis": {
            "target_pages": 25,
            "subsections": [
                "3.1 Self-Referential Prompting",
                "3.1.1 Methodological Overview",
                "3.1.2 Comparative Analysis",
                "3.1.3 Quantitative Results",
                "3.1.4 Quality Assessment",
                "3.2 Reflective Evaluation",
                "3.3 Iterative Self-Correction/Debate"
            ]
        },
        "4. Discussion": {
            "target_pages": 10,
            "subsections": [
                "4.1 Synthesis of Findings",
                "4.2 Methodological Differences",
                "4.3 Improvement Patterns",
                "4.4 Implications",
                "4.5 Limitations",
                "4.6 Future Research Directions"
            ]
        },
        "5. Conclusion": {
            "target_pages": 2,
            "subsections": ["Key Findings", "Recommendations"]
        }
    }
    
    def validate_section_length(self, section_title, text):
        """Checks if section meets target length."""
        # Find matching key in DETAILED_STRUCTURE (fuzzy match or exact)
        target = {}
        for key, val in self.DETAILED_STRUCTURE.items():
            if key in section_title or section_title in key:
                target = val
                break
        
        if not target:
            return "OK (No target defined)"

        target_words = target.get("target_words")
        target_pages = target.get("target_pages")
        
        word_count = len(text.split())
        page_estimate = word_count / 250  # ~250 words per page
        
        if target_pages and page_estimate < target_pages * 0.8:
            return f"WARNING: Section '{section_title}' too short ({page_estimate:.1f} vs {target_pages} pages)"
        
        if target_words and word_count < target_words * 0.8:
             return f"WARNING: Section '{section_title}' too short ({word_count} vs {target_words} words)"
             
        return "OK"
