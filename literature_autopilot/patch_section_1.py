import json
import os
import sys

# Add current directory to path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from paper_writer import PaperWriter

def patch_intro():
    print("Patching Section 1: Introduction...")
    
    # Load Data (from parent dir)
    with open("../slr_extracted_data.json", "r") as f:
        extracted_data = json.load(f)
    relevant_data = [d for d in extracted_data if d.get("screening_decision") == "INCLUDE"]
    
    # Load Structure (from parent dir)
    with open("../paper_structure.md", "r") as f:
        structure_content = f.read()
        
    # Initialize Writer (Use Flash for speed, skip review for safety)
    writer = PaperWriter(model_name="gemini-flash-latest")
    
    section_title = "1. Introduction"
    instructions = f"""
    Follow the plan for '{section_title}' defined in the Structure below.
    
    **Structure**:
    {structure_content}
    """
    
    # Write Section
    text = writer.write_section(
        section_title=section_title,
        section_instructions=instructions,
        relevant_data=relevant_data,
        skip_review=True
    )
    
    print("\n--- Generated Introduction ---\n")
    print(text)
    
    # Save to a separate file for manual merging
    with open("../section_1_patch.md", "w") as f:
        f.write(text)

if __name__ == "__main__":
    patch_intro()
