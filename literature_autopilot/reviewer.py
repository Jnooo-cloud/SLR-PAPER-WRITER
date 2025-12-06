import os
import json
import google.generativeai as genai
from typing import Dict, List
from llm_utils import RotatableModel

class MultiAgentReviewer:
    MAX_ROUNDS = 2 # Increased for quality
    
    STYLE_GUIDELINES = """
    **ACADEMIC WRITING BEST PRACTICES (STRICT ENFORCEMENT):**
    1.  **Structure**: Inverted Pyramid. Max 3 nesting levels. Paragraphs: Topic -> Evidence -> Conclusion.
    2.  **Language**: Formal, objective. No colloquialisms. No "I". Past tense for results.
    3.  **Formatting**: No Bullet Points in body. No Bold Text. Captions below figures.
    4.  **Content**: NO placeholders ("N studies"). Explicitly state numbers.
    """

    def __init__(self, model_name: str = "gemini-1.5-pro-latest"):
        self.model = RotatableModel(model_name)

    def _call_agent(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"    Agent Error: {e}")
            return "Error generating response."

    def review_section(self, section_name: str, draft_text: str, source_data: List[Dict] = None, max_rounds: int = 2) -> str:
        """
        Runs the Multi-Agent Debate Loop:
        Writer -> (Hawk + Architect) -> Moderator -> Editor -> Loop
        """
        current_draft = draft_text
        
        for i in range(max_rounds):
            print(f"  [Multi-Agent Debate] Round {i+1}/{max_rounds} for '{section_name}'...")
            
            # 1. Methodological Hawk
            prompt_hawk = f"""
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
            
            **Draft Text**: {current_draft}
            """
            critique_hawk = self._call_agent(prompt_hawk)
            
            # 2. Narrative Architect
            prompt_architect = f"""
            You are a senior editor at a high-impact journal.
            
            {self.STYLE_GUIDELINES}

            **Review Criteria (Focus):**
            1.  **Clarity & Flow**: Does the narrative flow logically?
            2.  **Impact & Insight**: Is the "so what?" clear?
            3.  **Academic Tone**: Is the language precise?
            4.  **Structure**: Does it follow the Inverted Pyramid?
            5.  **Paragraphs**: Does each paragraph have a Topic Sentence, Evidence, and Conclusion?

            **Section**: {section_name}
            **Draft Text**: {current_draft}

            **Task**: Provide a numbered list of constructive suggestions.
            """
            critique_architect = self._call_agent(prompt_architect)

            # 3. StyleCritic (New Agent)
            prompt_style = f"""
            You are a ruthless copyeditor.
            
            {self.STYLE_GUIDELINES}
            
            **BANNED WORDS**: Crucial, Paramount, Delve, Landscape, Burgeoning, Underscore, Potential, Comprehensive, Multifaceted, Elucidate, Leverage, Pave the way, Actionable insights, Testament to.
            
            **Review Criteria**:
            1.  **Robotic Prose**: Does it sound like AI?
            2.  **Sentence Length**: Flag sentences > 25 words.
            3.  **Formatting**: NO BOLD. NO BULLETS in body. Figure labels "Figure X".
            4.  **Passive Voice**: Flag excessive passive voice.
            5.  **Placeholders**: FLAG ANY "N studies".

            **Section**: {section_name}
            **Draft Text**: {current_draft}
            
            **Task**: Identify violations and suggest rewrites.
            """
            critique_style = self._call_agent(prompt_style)

            # 4. ConsistencyCritic (New Agent)
            prompt_consistency = f"""
            You are the "ConsistencyCritic".
            
            {self.STYLE_GUIDELINES}
            
            **Review Criteria**:
            1.  **Citation Typos**: "et al" (no dot). (Author, Year).
            2.  **Date Consistency**: Jan 2022 – May 2025.
            3.  **Study Counts**: Flag "N studies". Must be specific number.
            4.  **Bibliography**: Check for duplicates.
            
            **Section**: {section_name}
            **Draft Text**: {current_draft}
            
            **Task**: 
            - Identify specific violations.
            - If the text is consistent, output "NO CONSISTENCY ISSUES".
            """
            critique_consistency = self._call_agent(prompt_consistency)

            # 5. FactChecker (The Hallucination Guard)
            critique_fact = "NO FACTUAL ISSUES (No source data provided)"
            if source_data:
                # Convert source data to a compact string for the prompt
                source_context = json.dumps(source_data, indent=2)
                prompt_fact = f"""
                You are the "FactChecker". Your ONLY job is to verify that the claims in the text are supported by the provided source data.
                You are the final line of defense against hallucinations.

                **Source Data (The Truth)**:
                {source_context}

                **Draft Text**:
                {current_draft}

                **Task**:
                1.  **Claim Verification**: For every specific claim (e.g., "Paper X achieved 95% accuracy"), find the corresponding entry in the Source Data.
                    - If the numbers/claims match: Good.
                    - If they DO NOT match: **FLAG AS CRITICAL ERROR**. (e.g., "Text says 95%, Data says 82%").
                    - If the claim is not in the data: Flag as "Potential Hallucination".
                2.  **Citation Verification**: Ensure that every paper cited in the text exists in the Source Data.
                
                **Output**:
                - If all claims are verified: "NO FACTUAL ISSUES".
                - If errors found: Provide a bulleted list of SPECIFIC discrepancies. Quote the text and the data.
                """
                critique_fact = self._call_agent(prompt_fact)
            
            # 6. Moderator
            prompt_moderator = f"""
            You are the Lead Editor acting as a moderator between expert reviewers. Your goal is to synthesize their feedback into a single, prioritized action plan for the author.

            **Critique from Methodological Hawk**: {critique_hawk}
            
            **Critique from Narrative Architect**: {critique_architect}
            
            **Critique from StyleCritic**: {critique_style}
            
            **Critique from ConsistencyCritic**: {critique_consistency}

            **Critique from FactChecker (CRITICAL)**: {critique_fact}

            **Task**:
            1.  **Synthesize**: Combine the critiques into a single, non-redundant, numbered list of required changes.
            2.  **Prioritize**: 
                - **PRIORITY 0 (FATAL)**: Any issues flagged by **FactChecker** (Hallucinations/Lies) MUST be fixed first.
                - **PRIORITY 1**: Methodological flaws (Hawk).
                - **PRIORITY 2**: Style and Consistency issues (StyleCritic/ConsistencyCritic).
                - **PRIORITY 3**: Flow and Narrative (Architect).
            3.  **Check for Convergence**: Assess if the critiques are minor refinements or fundamental flaws. If the critiques are minor (e.g., wording suggestions, typos) AND FactChecker is happy, state "CONVERGENCE REACHED". Otherwise, state "REVISION REQUIRED".

            **Output Format (JSON ONLY):**
            {{
              "convergence_status": "REVISION REQUIRED" or "CONVERGENCE REACHED",
              "top_3_priorities": ["...", "...", "..."],
              "full_action_plan": ["...", "...", "...", "..."]
            }}
            """
            moderator_response = self._call_agent(prompt_moderator)
            
            try:
                # Clean JSON
                text = moderator_response.strip()
                if text.startswith("```json"):
                    text = text[7:-3]
                moderator_output = json.loads(text)
            except Exception as e:
                print(f"    Moderator JSON Error: {e}")
                # Fallback if JSON fails
                moderator_output = {"convergence_status": "REVISION REQUIRED", "full_action_plan": [moderator_response]}

            # Check Convergence
            if moderator_output.get("convergence_status") == "CONVERGENCE REACHED":
                print(f"    Convergence reached in round {i+1}. Finalizing section.")
                break
            
            # 4. Editor
            prompt_editor = f"""
            You are a world-class academic writer and editor. Your goal is to produce a flawless, A+ quality paper section.

            **Section**: {section_name}

            **Original Draft**: {current_draft}

            **Moderator's Action Plan**: {json.dumps(moderator_output.get('full_action_plan'))}
            **Top Priorities**: {json.dumps(moderator_output.get('top_3_priorities'))}

            **Instructions**:
            - Perform a complete rewrite of the section.
            - **Address every single point** from the action plan provided by the moderator.
            - Pay special attention to implementing the top priorities flawlessly.
            - Elevate the text to be more rigorous, clear, and insightful while maintaining the core information.

            Output ONLY the rewritten text. Do not add any commentary.
            """
            current_draft = self._call_agent(prompt_editor)
            
        return current_draft
