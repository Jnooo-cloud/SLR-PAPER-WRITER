import argparse
import os
import json
import time
from search_modules import SemanticScholarSearch, ArxivSearch, Paper
from snowballing import Snowballer
from utils import deduplicate_papers, filter_papers, export_to_csv, export_to_markdown, load_papers_from_csv
import pandas as pd

from screener import PaperScreener
from pdf_retriever import PDFRetriever
from extractor import SLRExtractor
from paper_writer import PaperWriter

# Configuration based on user requirements
KEYWORDS = [
    "Self-Referential Prompting",
    "Reflective Evaluation",
    "Iterative Self-Correction",
    "LLM Debate",
    "Self-Improvement LLM"
]


SEED_PAPERS_URLS = [
    "https://evjang.com/2023/03/26/self-reflection.html", # Blog post, might not be in S2, but we can search by title
    "https://aclanthology.org/2024.naacl-long.15/",
    "https://composable-models.github.io/llm_debate/", # Project page, likely has a paper title
    "https://arxiv.org/abs/2402.06782"
]

# We need titles for snowballing if URLs don't work directly with S2
SEED_PAPER_TITLES = [
    "Self-Correction in Large Language Models", # Approximate title for the blog/concept
    "Self-Refine: Iterative Refinement with Self-Feedback", # Common paper in this area
    "Improving Factuality and Reasoning in Language Models through Multiagent Debate",
    "Self-Discover: Large Language Models Self-Compose Reasoning Structures"
]

def main():
    print("Initializing SLR Bot...")
    
    # Initialize modules
    s2_search = SemanticScholarSearch()
    arxiv_search = ArxivSearch()
    snowballer = Snowballer()
    
    # Parse Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--screen", action="store_true", help="Enable LLM-based screening")
    parser.add_argument("--provider", type=str, default="openai", choices=["openai", "gemini"], help="LLM provider")
    parser.add_argument("--model", type=str, help="Model name")
    parser.add_argument("--openai-key", type=str, help="OpenAI API Key")
    # Paper Factory Args
    parser.add_argument("--download-pdfs", action="store_true", help="Download PDFs for included papers")
    parser.add_argument("--extract-data", action="store_true", help="Run data extraction on PDFs")
    parser.add_argument("--generate-structure", action="store_true", help="Generate paper structure from extracted data")
    parser.add_argument("--write-paper", action="store_true", help="Write the full paper based on structure")
    parser.add_argument("--final-review", action="store_true", help="Run MCP-based final review and iterative improvement")
    parser.add_argument("--input-file", type=str, default="slr_screening_results.csv", help="Input CSV file")
    args = parser.parse_args()
    
    # Set OpenAI Key if provided
    if args.openai_key:
        os.environ["OPENAI_API_KEY"] = args.openai_key
    
    all_papers = []

    if args.input_file:
        print(f"\n--- Resuming from file: {args.input_file} ---")
        all_papers = load_papers_from_csv(args.input_file)
        # If loading from file, we assume these are the 'final' papers or at least the ones we want to process
        # We skip phases 1, 2, 3
        unique_papers = all_papers
        filtered_papers = all_papers
        final_papers = all_papers
        
        # If we are resuming, we might want to filter by "INCLUDE" if it was a screening result file
        # But let's leave that to the user or assume the input file is what they want to process.
        # If the file has "Screening Decision", we could filter.
        if any(hasattr(p, 'screening_decision') and p.screening_decision == "INCLUDE" for p in all_papers):
             print("Filtering for INCLUDED papers from loaded file...")
             final_papers = [p for p in all_papers if getattr(p, 'screening_decision', '') == "INCLUDE"]
             print(f"Selected {len(final_papers)} INCLUDED papers.")
        
    else:
        # 1. Keyword Search
        print(f"\n--- Phase 1: Keyword Search ({len(KEYWORDS)} keywords) ---")
        for keyword in KEYWORDS:
            print(f"Searching for: '{keyword}'")
            s2_results = s2_search.search_keyword(keyword, limit=20)
            arxiv_results = arxiv_search.search_keyword(keyword, limit=20)
            print(f"  Found {len(s2_results)} (S2) + {len(arxiv_results)} (arXiv) papers")
            all_papers.extend(s2_results)
            all_papers.extend(arxiv_results)

        # 2. Snowballing
        print(f"\n--- Phase 2: Snowballing ({len(SEED_PAPER_TITLES)} seed papers) ---")
        seed_papers_objs = []
        
        # First, find the seed papers in S2 to get their IDs
        for title in SEED_PAPER_TITLES:
            print(f"Resolving seed paper: {title}")
            results = s2_search.search_keyword(title, limit=1)
            if results:
                seed_papers_objs.append(results[0])
                print(f"  Found: {results[0].title} (ID: {results[0].doi or 'S2ID'})")
            else:
                print(f"  Could not find seed paper: {title}")

        # Run Snowballing
        for seed in seed_papers_objs:
            if seed.doi or seed.url: 
                # Note: My Snowballer implementation currently takes ID strings for get_citations/references
                # Let's get the ID. S2 search returns Paper objects.
                # We need the S2 Paper ID which might not be in my Paper class yet (I only added DOI).
                # Let's rely on the search_modules to handle this or just search by title again in snowballer?
                # Actually, let's use the DOI if available, or skip for now to keep it simple.
                # Ideally we should store S2ID.
                pass
                
                # For this prototype, let's just do a quick search for citations using the title if we can't get ID easily
                # But wait, the snowballer.get_citations takes an ID.
                # Let's try to get the paper ID from the S2 search result.
                # The current Paper class doesn't store S2ID. I should probably add it or just use DOI.
                # Let's assume DOI works for now.
                
                if seed.doi:
                    print(f"  Snowballing (Forward) for: {seed.title}")
                    citations = snowballer.get_citations(seed.doi, max_results=50)
                    print(f"    Found {len(citations)} citations")
                    all_papers.extend(citations)
                    
                    print(f"  Snowballing (Backward) for: {seed.title}")
                    references = snowballer.get_references(seed.doi, max_results=50)
                    print(f"    Found {len(references)} references")
                    all_papers.extend(references)

        # 3. Processing
        print(f"\n--- Phase 3: Processing ({len(all_papers)} raw papers) ---")
        unique_papers = deduplicate_papers(all_papers)
        print(f"After deduplication: {len(unique_papers)} papers")
        
        # Filter (Optional: keep only recent papers or specific keywords)
        print(f"Filtering papers (Year >= 2021)...")
        filtered_papers = filter_papers(unique_papers, min_year=2021)
        print(f"After filtering: {len(filtered_papers)} papers (removed {len(unique_papers) - len(filtered_papers)} old papers)")
        
        # 3.5 Citation Enrichment (Skipped)
        print(f"\n--- Phase 3.5: Citation Enrichment (SKIPPED) ---")
                
        # print(f"Enriched {enriched_count} papers with citation counts and metadata.")
        
        # Save intermediate results
        print(f"Saving intermediate results to slr_results_enriched.csv...")
        export_to_csv(filtered_papers, "slr_results_enriched.csv")
        
        final_papers = filtered_papers
    
    if args.screen:
        print(f"\n--- Phase 4: Automated Screening ---")
        try:
            screener = PaperScreener(provider=args.provider, model=args.model)
            # screen_papers now returns a list, but we want to save incrementally.
            # We will modify the loop here instead of using the bulk method if possible, 
            # or better, let's just iterate here.
            
            # Load existing results if resuming
            screened_results = []
            screened_titles = set()
            if os.path.exists("slr_screening_results.csv"):
                try:
                    existing_df = pd.read_csv("slr_screening_results.csv")
                    screened_results = existing_df.to_dict('records')
                    screened_titles = set(existing_df["Title"].tolist())
                    print(f"  Resuming screening: Found {len(screened_results)} already screened papers.")
                except Exception as e:
                    print(f"  Could not load existing screening results: {e}")

            print(f"Screening {len(filtered_papers)} papers...")
            for i, paper in enumerate(filtered_papers):
                if paper.title in screened_titles:
                    print(f"[{i+1}/{len(filtered_papers)}] Skipping (Already Screened): {paper.title[:50]}...")
                    continue

                print(f"[{i+1}/{len(filtered_papers)}] Screening (Consensus Mode): {paper.title[:50]}...")
                result = screener.screen_paper_consensus(paper)
                
                paper_data = paper.to_dict()
                paper_data.update({
                    "Screening Decision": result.get("decision", "ERROR"),
                    "Screening Confidence": result.get("confidence", 0.0),
                    "Screening Reason": result.get("reasoning", "Error occurred"),
                    "Screening Analysis": result.get("analysis", "")
                })
                screened_results.append(paper_data)
                
                # Save every 5 papers
                if (i + 1) % 5 == 0:
                    pd.DataFrame(screened_results).to_csv("slr_screening_results.csv", index=False)
                    print(f"  (Saved progress to slr_screening_results.csv)")
            
            # Final save
            df = pd.DataFrame(screened_results)
            df.to_csv("slr_screening_results.csv", index=False)
            
            # Filter included papers for the next phases
            included_titles = set(df[df["Screening Decision"] == "INCLUDE"]["title"].tolist())
            final_papers = [p for p in filtered_papers if p.title in included_titles]
            
            print(f"Screening complete. Included {len(final_papers)}/{len(filtered_papers)} papers.")
            print("Saved detailed screening results to slr_screening_results.csv")
            
        except Exception as e:
            print(f"Screening failed: {e}")
            # If screening failed, we might want to stop or proceed with what we have
            # For now, let's try to load what we have
            if os.path.exists("slr_screening_results.csv"):
                 df = pd.read_csv("slr_screening_results.csv")
                 included_titles = set(df[df["Screening Decision"] == "INCLUDE"]["Title"].tolist())
                 final_papers = [p for p in filtered_papers if p.title in included_titles]
                 print(f"  Resuming with {len(final_papers)} included papers from partial run.")
            else:
                 print("Proceeding with unscreened papers (WARNING)...")

    # 5. Export
    print("\n--- Phase 5: Exporting ---")
    export_to_csv(final_papers, "slr_results_final.csv")
    export_to_markdown(final_papers, "slr_results_final.md")
    
    # 6. Paper Factory (New)
    if args.download_pdfs:
        print("\n--- Phase 6: PDF Retrieval ---")
        retriever = PDFRetriever()
        for paper in final_papers:
            pdf_path = retriever.download_paper(paper)
            if pdf_path:
                paper.pdf_path = pdf_path
                print(f"  PDF saved: {pdf_path}")
        
        # Report Missing PDFs
        missing_pdfs = [p for p in final_papers if not hasattr(p, 'pdf_path') or not p.pdf_path]
        if missing_pdfs:
            print(f"\n⚠️  WARNING: {len(missing_pdfs)} relevant papers are missing PDFs.")
            print(f"    Generating 'missing_pdfs.md' for manual retrieval...")
            with open("missing_pdfs.md", "w") as f:
                f.write("# Missing PDFs for Manual Retrieval\n\n")
                f.write("Please manually download these papers and place them in the `pdfs/` folder.\n")
                f.write("Then re-run the bot with `--extract-data`.\n\n")
                for p in missing_pdfs:
                    f.write(f"- **{p.title}**\n")
                    f.write(f"  - URL: {p.url}\n")
                    f.write(f"  - DOI: {p.doi}\n")
                    f.write(f"  - Source: {p.source}\n\n")
            print("    -> Saved list to missing_pdfs.md")

    if args.extract_data:
        print(f"\n--- Phase 6: Data Extraction (Full SLR Protocol) ---")
        extractor = SLRExtractor(model_name=args.model)
        extracted_data = []
        
        # Re-associate PDFs if missing (e.g. when resuming)
        pdf_dir = "pdfs"
        for paper in final_papers:
            if not hasattr(paper, 'pdf_path') or not paper.pdf_path:
                # Reconstruct filename logic from PDFRetriever
                safe_filename = "".join([c for c in paper.title if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_") + ".pdf"
                potential_path = os.path.join(pdf_dir, safe_filename)
                if os.path.exists(potential_path):
                    paper.pdf_path = potential_path
                    print(f"  Found PDF for '{paper.title[:30]}...': {potential_path}")
        
        for paper in final_papers:
            if hasattr(paper, 'pdf_path') and paper.pdf_path and os.path.exists(paper.pdf_path):
                print(f"Extracting data from: {paper.title[:50]}...")
                result = extractor.process_paper(paper.pdf_path)
                if result:
                    # Add metadata
                    result["paper_title"] = paper.title
                    result["paper_source"] = paper.source
                    extracted_data.append(result)
                    
                    # Incremental Save
                    with open("slr_extracted_data.json", "w") as f:
                        json.dump(extracted_data, f, indent=2)
                    print(f"  (Saved {len(extracted_data)} extracted papers)")
            else:
                print(f"Skipping extraction for {paper.title[:30]} (No PDF found)")

        print("Extraction complete.")

    if args.generate_structure:
        print("\n--- Phase 8: Paper Generation (Structure) ---")
        if os.path.exists("slr_extracted_data.json"):
            with open("slr_extracted_data.json", "r") as f:
                extracted_data = json.load(f)
            
            # FIX: Filter out papers that were excluded during Full-Text Screening (Stage 1)
            relevant_data = [
                d for d in extracted_data 
                if d.get("screening_decision") == "INCLUDE"
            ]
            print(f"  Filtered {len(extracted_data)} -> {len(relevant_data)} papers for structure generation.")
            
            writer = PaperWriter(model_name=args.model)
            structure = writer.generate_structure(relevant_data)
            
            # --- Structure Validation (Self-Improvement) ---
            print("  Validating Paper Structure...")
            validation_prompt = f"""
            You are a Research Supervisor. Review the following Paper Structure for an SLR on "LLM Self-Improvement".
            
            **Structure**:
            {structure}
            
            **Criteria**:
            1. Does it explicitly answer the RQ: "Methodische Unterschiede" AND "Verbesserungen"?
            2. Is the "Analysis of Core Mechanisms" section structured by Mechanism (not by paper)?
            3. Is the flow logical?
            
            If Good: Output "APPROVED".
            If Bad: Output a critique to improve it.
            """
            
            # Simple validation loop (1 round)
            # We use the writer's model for this
            try:
                val_response = writer.model.generate_content(validation_prompt).text
                if "APPROVED" not in val_response:
                    print("  Structure Critique received. Refining...")
                    refinement_prompt = f"""
                    Improve the following structure based on this critique:
                    
                    **Critique**: {val_response}
                    
                    **Original Structure**:
                    {structure}
                    
                    Output ONLY the improved structure in Markdown.
                    """
                    structure = writer.model.generate_content(refinement_prompt).text
                    print("  Structure Refined.")
                else:
                    print("  Structure Approved.")
            except Exception as e:
                print(f"  Validation failed: {e}. Proceeding with original structure.")

            with open("paper_structure.md", "w") as f:
                f.write(structure)
            print("  Generated paper structure: paper_structure.md")
            print("  Please review this file before proceeding to full writing.")
        else:
            print("  No extracted data found. Run --extract-data first.")

    if args.write_paper:
        print("\n--- Phase 9: Full Paper Writing ---")
        if not os.path.exists("slr_extracted_data.json"):
            print("Error: slr_extracted_data.json not found. Run --extract-data first.")
            return
        if not os.path.exists("paper_structure.md"):
            print("Error: paper_structure.md not found. Run --generate-structure first.")
            return

        with open("slr_extracted_data.json", "r") as f:
            extracted_data = json.load(f)
        
        # Filter for relevant data (INCLUDE only)
        relevant_data = [d for d in extracted_data if d.get("screening_decision") == "INCLUDE"]
        
        with open("paper_structure.md", "r") as f:
            structure_content = f.read()

        writer = PaperWriter(model_name=args.model)
        full_paper = ""
        previous_summary = ""

        # Define sections to write
        sections = [
            "Abstract",
            "1. Introduction",
            "2. Methodology",
            "3.1 Analysis: Self-Referential Prompting",
            "3.2 Analysis: Reflective Evaluation",
            "3.3 Analysis: Iterative Self-Correction / Debate",
            "4. Discussion",
            "5. Conclusion"
        ]

        for section in sections:
            print(f"\nProcessing Section: {section}...")
            
            # Contextual instructions
            instructions = f"""
            Follow the plan for '{section}' defined in the Structure below.
            
            **Structure**:
            {structure_content}
            """
            
            section_text = writer.write_section(
                section_title=section,
                section_instructions=instructions,
                relevant_data=relevant_data,
                previous_sections_summary=previous_summary
            )
            
            # Update summary for next section (keep it brief to save context)
            # We can just append the last few lines or a quick summary. 
            # For now, let's pass the last 500 chars as a simple "previous context" signal
            # Save progress incrementally
            with open("final_paper_draft.md", "a") as f:
                f.write(section_text + "\n\n")
            
            full_paper += section_text + "\n\n"
            previous_summary += f"Summary of {section}: ...\n" # Simplified summary update

        # Save Final Paper
        with open("final_paper.md", "w") as f:
            f.write(full_paper)
        
        print("\n✅ Final Paper Generated: final_paper.md")

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

    print("Done!")

if __name__ == "__main__":
    main()
