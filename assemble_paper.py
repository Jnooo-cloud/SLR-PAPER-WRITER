import os

def assemble_paper():
    print("Assembling Final Paper...")
    
    # Read Files
    with open("final_paper.md", "r") as f:
        main_text = f.read()
        
    if os.path.exists("section_1_patch.md"):
        patch_path = "section_1_patch.md"
    elif os.path.exists("literature_autopilot/section_1_patch.md"):
        patch_path = "literature_autopilot/section_1_patch.md"
    else:
        print("Error: section_1_patch.md not found")
        return

    with open(patch_path, "r") as f:
        intro_text = f.read()
        
    with open("bibliography.md", "r") as f:
        bib_text = f.read()
        
    # 1. Replace Intro
    # Find "## 1. Introduction" and the error message
    start_marker = "## 1. Introduction"
    end_marker = "## 2. Methodology"
    
    start_idx = main_text.find(start_marker)
    end_idx = main_text.find(end_marker)
    
    if start_idx != -1 and end_idx != -1:
        # Replace the block
        # We want to keep "## 2. Methodology" so we replace up to end_idx
        # But intro_text includes "## 1. Introduction" header?
        # Let's check intro_text content.
        # It starts with "# 1. Introduction".
        # We should replace the existing header too.
        
        # Adjust intro_text header level if needed. Main text uses ## for sections?
        # Abstract is # Abstract.
        # Intro is ## 1. Introduction.
        # Methodology is ## 2. Methodology.
        # So H2 is correct for numbered sections.
        # The patch has "# 1. Introduction". I should change it to "## 1. Introduction".
        intro_text = intro_text.replace("# 1. Introduction", "## 1. Introduction")
        
        # Also check subsections. Patch has "## 1.1". Should be "### 1.1".
        intro_text = intro_text.replace("## 1.1", "### 1.1")
        intro_text = intro_text.replace("## 1.2", "### 1.2")
        intro_text = intro_text.replace("## 1.3", "### 1.3")
        intro_text = intro_text.replace("## 1.4", "### 1.4")
        intro_text = intro_text.replace("## 1.5", "### 1.5")
        intro_text = intro_text.replace("### 1.2.1", "#### 1.2.1")
        intro_text = intro_text.replace("### 1.2.2", "#### 1.2.2")
        intro_text = intro_text.replace("### 1.2.3", "#### 1.2.3")
        intro_text = intro_text.replace("### 1.3.1", "#### 1.3.1")
        intro_text = intro_text.replace("### 1.3.2", "#### 1.3.2")
        intro_text = intro_text.replace("### 1.3.3", "#### 1.3.3")

        new_text = main_text[:start_idx] + intro_text + "\n\n" + main_text[end_idx:]
        main_text = new_text
    else:
        print("Warning: Could not find Intro block to replace.")

    # 2. Add Keywords
    # Find end of Abstract
    # Abstract starts at # Abstract.
    # Ends before ## 1. Introduction.
    # But we just replaced Intro. So find "## 1. Introduction".
    intro_idx = main_text.find("## 1. Introduction")
    if intro_idx != -1:
        keywords = "\n\n**Keywords**: Large Language Models, Self-Improvement, Systematic Literature Review, Autonomous Agents, Taxonomy\n\n"
        # Insert before Intro
        main_text = main_text[:intro_idx] + keywords + main_text[intro_idx:]
        
    # 3. Insert Figures
    # Figure 1: Year Distribution. Insert in Methodology 2.1.1
    # Find "### 2.1.1 Information Sources and Search Strategy"
    fig1_marker = "### 2.1.1 Information Sources and Search Strategy"
    fig1_idx = main_text.find(fig1_marker)
    if fig1_idx != -1:
        # Insert after the first paragraph of this section?
        # Or just after the header.
        # Let's insert after the header.
        insert_pos = fig1_idx + len(fig1_marker)
        figure_md = "\n\n![Figure 1: Distribution of Included Studies by Year](images/figure_1_year_distribution.png)\n*Figure 1. Distribution of included studies by year of publication.*\n\n"
        main_text = main_text[:insert_pos] + figure_md + main_text[insert_pos:]
        
    # Figure 2: Mechanism Distribution. Insert in Section 3.1
    # Find "## 3.1 Analysis: Self-Referential Prompting"
    fig2_marker = "## 3.1 Analysis: Self-Referential Prompting"
    fig2_idx = main_text.find(fig2_marker)
    if fig2_idx != -1:
        insert_pos = fig2_idx + len(fig2_marker)
        figure_md = "\n\n![Figure 2: Distribution of Self-Improvement Mechanisms](images/figure_2_mechanism_distribution.png)\n*Figure 2. Distribution of identified self-improvement mechanisms across the three archetypes.*\n\n"
        main_text = main_text[:insert_pos] + figure_md + main_text[insert_pos:]

    # 4. Append Bibliography
    # Check if Bibliography header exists in bib_text
    if "# Bibliography" not in bib_text:
        bib_text = "\n\n# Bibliography\n\n" + bib_text
    
    main_text += "\n\n" + bib_text
    
    # Save
    with open("final_paper_v2.md", "w") as f:
        f.write(main_text)
        
    print("Successfully assembled final_paper_v2.md")

if __name__ == "__main__":
    assemble_paper()
