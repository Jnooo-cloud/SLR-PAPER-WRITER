import json
import os
import sys
# Add current directory to path to find local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from paper_writer import PaperWriter

def patch_sections():
    print("Patching Sections 3.2 and 3.3...")
    
    # Load Data (Relative to literature_autopilot/)
    with open("../data/slr_extracted_data.json", "r") as f:
        data = json.load(f)
    
    # Filter Data
    reflective_data = [d for d in data if d.get("data", {}).get("mechanism", {}).get("type") == "Reflective"]
    debate_data = [d for d in data if d.get("data", {}).get("mechanism", {}).get("type") == "Debate"]
    
    print(f"Found {len(reflective_data)} Reflective papers and {len(debate_data)} Debate papers.")
    
    writer = PaperWriter(model_name="gemini-2.5-flash")
    
    # --- Section 3.2: Reflective Evaluation ---
    instr_3_2 = """
    Write a detailed analysis of the 'Reflective Evaluation' mechanism based ONLY on the provided papers.
    
    **CRITICAL INSTRUCTIONS**:
    1.  **DO NOT** mention "surveys", "respondents", "Likert scales", "Hierarchical Linear Modeling", or "N=320". This is a LITERATURE REVIEW of the provided papers, not a new statistical study.
    2.  Synthesize the findings from the papers (e.g., Meta-Rewarding, ReGenesis, AnyTool).
    3.  Discuss how they implement the 'Internal Critic' or 'Meta-Judge'.
    4.  Report specific performance gains from these papers (e.g., "ReGenesis improved GSM8K by 19.6 points").
    5.  Compare their approaches (e.g., hierarchical vs. recursive).
    6.  Structure:
        *   Mechanism Overview (The concept of the internal judge)
        *   Hierarchical Approaches (Meta-Rewarding)
        *   Recursive/Abstract Approaches (ReGenesis, RMP)
        *   Application to Tool Use (AnyTool)
        *   Synthesis of Effectiveness
    """
    
    section_3_2 = writer.write_section(
        section_title="3.2 Analysis: Reflective Evaluation",
        section_instructions=instr_3_2,
        relevant_data=reflective_data,
        previous_sections_summary="Section 3.1 discussed Self-Referential Prompting."
    )
    
    # --- Section 3.3: Debate ---
    instr_3_3 = """
    Write a detailed analysis of the 'Iterative Self-Correction and Debate' mechanism based ONLY on the provided papers.
    
    **CRITICAL INSTRUCTIONS**:
    1.  **DO NOT** mention "surveys", "MSE reduction", "convergence rates" (unless explicitly in a paper), "NVIDIA A100 GPUs", or "controlled computational environment".
    2.  Synthesize the findings from the papers (e.g., SWE-Debate, DOWN, Multi-Agent Debate).
    3.  Discuss the role of 'Social Computation' and 'Conflict Resolution'.
    4.  Report specific gains (e.g., "Debate improved Knight-Knave-Spy accuracy by 52%").
    5.  Discuss the cost/efficiency trade-off (DOWN paper).
    6.  Structure:
        *   Mechanism Overview (Multi-agent consensus)
        *   Robustness in Logic & Code (SWE-Debate, Logic Puzzles)
        *   Efficiency & Adaptive Control (DOWN framework)
        *   Synthesis of Effectiveness
    """
    
    section_3_3 = writer.write_section(
        section_title="3.3 Analysis: Iterative Self-Correction and Debate",
        section_instructions=instr_3_3,
        relevant_data=debate_data,
        previous_sections_summary="Section 3.2 discussed Reflective Evaluation."
    )
    
    # Save Patches
    with open("section_3_2_patch.md", "w") as f:
        f.write(section_3_2)
    with open("section_3_3_patch.md", "w") as f:
        f.write(section_3_3)
        
    print("Patches generated. Now merging into final paper...")
    
    # Read original paper
    with open("../output/final_paper_v2.md", "r") as f:
        content = f.read()
        
    # Replace Section 3.2
    # We need to find the start of 3.2 and 3.3 and replace the content between them.
    # This is tricky with string replacement if we don't have exact markers.
    # Let's assume standard headers.
    
    # Simple split/replace strategy
    # Note: The original file has "## 3.1 Analysis...", "## 3.2 Analysis...", "## 3.3 Analysis...", "## 4. Discussion"
    
    parts = content.split("## 3.2 Analysis: Reflective Evaluation")
    if len(parts) < 2:
        print("Error: Could not find Section 3.2 header.")
        return
    
    pre_3_2 = parts[0]
    remainder = parts[1]
    
    parts2 = remainder.split("## 3.3 Analysis: Iterative Self-Correction and Debate")
    if len(parts2) < 2:
        # Maybe the header is slightly different?
        # Let's try to find the next section "## 4. Discussion"
        print("Error: Could not find Section 3.3 header.")
        return

    # Actually, let's just use the generated sections to replace the bad ones.
    # But wait, the original file had "## 3.2 Analysis: Reflective Evaluation" as the header.
    # The `write_section` might add the header.
    
    # Let's construct the new file:
    # Pre-3.2 + New 3.2 + New 3.3 + Post-3.3
    
    # Find start of 3.2
    start_3_2 = content.find("## 3.2 Analysis: Reflective Evaluation")
    
    # Find start of 3.3
    start_3_3 = content.find("## 3.3 Analysis: Iterative Self-Correction and Debate")
    
    # Find start of 4.
    start_4 = content.find("## 4. Discussion")
    
    if start_3_2 == -1 or start_3_3 == -1 or start_4 == -1:
        print("Error: Could not locate section boundaries.")
        return

    new_content = (
        content[:start_3_2] + 
        section_3_2 + "\n\n" + 
        section_3_3 + "\n\n" + 
        content[start_4:]
    )
    
    with open("../output/final_paper_v3.md", "w") as f:
        f.write(new_content)
        
    print("Successfully created ../output/final_paper_v3.md")

if __name__ == "__main__":
    patch_sections()
