import argparse
import os
import json
import yaml
import time
import pandas as pd
import logging
from typing import Dict, Any

# Import existing modules
from literature_autopilot.search_modules import SemanticScholarSearch, ArxivSearch
from literature_autopilot.snowballing import Snowballer
from literature_autopilot.utils import deduplicate_papers, filter_papers, export_to_csv, export_to_markdown, load_papers_from_csv
from literature_autopilot.screener import PaperScreener
from literature_autopilot.pdf_retriever import PDFRetriever
from literature_autopilot.extractor import SLRExtractor
from literature_autopilot.paper_writer import PaperWriter
from literature_autopilot.mcp_final_reviewer import MCPFinalReviewer
from literature_autopilot.citation_validator import CitationValidator
from literature_autopilot.visualizer import SLRVisualizer
from literature_autopilot.grade_assessment import GRADEAssessment
from literature_autopilot.gap_identifier import GapIdentifier
from literature_autopilot.context_manager import ContextManager

class SLRPipeline:
    def __init__(self, config_path: str = "literature_autopilot/config.yaml"):
        # Configure Logging
        logging.basicConfig(
            filename='slr_pipeline.log', 
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - %(message)s',
            filemode='a'
        )
        # Also log to console
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        
        self.config = self._load_config(config_path)
        self.visualizer = SLRVisualizer() if self.config["analysis"]["run_visualizer"] else None
        
        # Initialize modules
        self.s2_search = SemanticScholarSearch()
        self.arxiv_search = ArxivSearch()
        self.snowballer = Snowballer()
        
        # State
        self.all_papers = []
        self.unique_papers = []
        self.final_papers = []
        self.extracted_data = []
        self.paper_structure = ""
        self.draft_paper = ""
        self.final_paper = ""

    def _load_config(self, path: str) -> Dict[str, Any]:
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def run(self, args):
        """Orchestrate the full pipeline."""
        logging.info(f"Starting SLR Pipeline for topic: {self.config['slr_topic']}")
        
        steps = ["search", "screen", "download", "extract", "analyze", "write", "review"]
        start_index = 0
        if args.resume_from:
            if args.resume_from in steps:
                start_index = steps.index(args.resume_from)
                logging.info(f"Resuming pipeline from step: {args.resume_from}")
        
        # 1. Search & Snowballing
        if start_index <= 0 and not args.skip_search:
            self.step_search_and_snowball()
        
        # 2. Screening
        if start_index <= 1 and args.screen:
            self.step_screen()
            
        # 3. PDF Retrieval
        if start_index <= 2 and args.download_pdfs:
            self.step_download_pdfs()
            
        # 4. Extraction
        if start_index <= 3 and args.extract_data:
            self.step_extract_data()
            
        # 5. Analysis (Visuals, Gaps, GRADE)
        if start_index <= 4 and not args.skip_analysis:
            self.step_analyze()
            
        # 6. Writing
        if start_index <= 5 and args.write_paper:
            self.step_write_paper()
            
        # 7. Final Review
        if start_index <= 6 and args.final_review:
            self.step_final_review()

    def step_search_and_snowball(self):
        logging.info("\n--- Phase 1 & 2: Search & Snowballing ---")
        keywords = self.config["search"]["keywords"]
        for keyword in keywords:
            logging.info(f"Searching for: '{keyword}'")
            s2_results = self.s2_search.search_keyword(keyword, limit=self.config["search"]["max_search_results"])
            arxiv_results = self.arxiv_search.search_keyword(keyword, limit=self.config["search"]["max_search_results"])
            self.all_papers.extend(s2_results + arxiv_results)
            
        # Snowballing
        if self.config["snowballing"]["enabled"]:
            seed_titles = self.config["search"]["seed_titles"]
            logging.info(f"Snowballing with {len(seed_titles)} seeds...")
            # (Simplified logic from original bot)
            for title in seed_titles:
                results = self.s2_search.search_keyword(title, limit=1)
                if results and results[0].doi:
                    citations = self.snowballer.get_citations(results[0].doi, max_results=self.config["snowballing"]["max_results"])
                    self.all_papers.extend(citations)

        self.unique_papers = deduplicate_papers(self.all_papers)
        logging.info(f"Total unique papers found: {len(self.unique_papers)}")
        export_to_csv(self.unique_papers, "slr_results_enriched.csv")

    def step_screen(self):
        logging.info("\n--- Phase 3: Screening ---")
        prompt_path = self.config.get("prompts", {}).get("screening")
        screener = PaperScreener(
            provider=self.config["screening"]["provider"], 
            model=self.config["screening"]["model"],
            prompt_path=prompt_path
        )
        # Load existing if available
        if os.path.exists("slr_results_enriched.csv") and not self.unique_papers:
             self.unique_papers = load_papers_from_csv("slr_results_enriched.csv")
             
        # Filter recent papers first
        filtered_papers = filter_papers(self.unique_papers, min_year=2021)
        
        screened_results = screener.screen_papers(filtered_papers) # Using bulk method for simplicity, or loop
        # Save results
        pd.DataFrame(screened_results).to_csv("slr_screening_results.csv", index=False)
        
        # Filter included
        self.final_papers = [p for p in filtered_papers if any(r["title"] == p.title and r["Screening Decision"] == "INCLUDE" for r in screened_results)]
        logging.info(f"Included {len(self.final_papers)} papers.")

    def step_download_pdfs(self):
        logging.info("\n--- Phase 4: PDF Retrieval ---")
        retriever = PDFRetriever()
        # Load final papers if needed
        if not self.final_papers and os.path.exists("slr_screening_results.csv"):
             # Load logic...
             pass 
             
        for paper in self.final_papers:
            pdf_path = retriever.download_paper(paper)
            if pdf_path:
                paper.pdf_path = pdf_path

    def step_extract_data(self):
        logging.info("\n--- Phase 5: Extraction ---")
        prescreen_path = self.config.get("prompts", {}).get("prescreening")
        extract_path = self.config.get("prompts", {}).get("extraction")
        
        extractor = SLRExtractor(
            model_name=self.config["extraction"]["model"],
            prescreening_prompt_path=prescreen_path,
            extraction_prompt_path=extract_path
        )
        self.extracted_data = []
        for paper in self.final_papers:
            if hasattr(paper, 'pdf_path') and paper.pdf_path:
                data = extractor.process_paper(paper.pdf_path)
                if data:
                    data["paper_title"] = paper.title
                    self.extracted_data.append(data)
        
        with open("slr_extracted_data.json", "w") as f:
            json.dump(self.extracted_data, f, indent=2)

    def step_analyze(self):
        logging.info("\n--- Phase 6: Analysis ---")
        if not self.extracted_data and os.path.exists("slr_extracted_data.json"):
            with open("slr_extracted_data.json", "r") as f:
                self.extracted_data = json.load(f)

        # Visualizations
        if self.config["analysis"]["run_visualizer"] and self.visualizer:
            self.visualizer.create_prisma_flow_diagram(len(self.all_papers), len(self.unique_papers), len(self.final_papers), len(self.extracted_data))
            
            # Mechanism Comparison
            mechanisms = []
            for d in self.extracted_data:
                diffs = d.get("methodological_differences", {})
                if diffs:
                    mechanisms.append({
                        "Mechanism": diffs.get("mechanism_type", "Unknown"),
                        "Name": diffs.get("specific_name", "N/A"),
                        "Innovation": diffs.get("key_innovation", "N/A")[:100] + "..."
                    })
            self.visualizer.create_mechanism_comparison_table(mechanisms)
            self.visualizer.create_year_distribution_chart(self.extracted_data)

        # Gap Analysis
        if self.config["analysis"]["run_gap_identifier"]:
            gap_identifier = GapIdentifier(self.extracted_data)
            self.gap_report = gap_identifier.generate_gap_report()

        # GRADE (Data-Driven)
        if self.config["analysis"]["run_grade_assessment"]:
            all_outcomes = []
            for paper in self.extracted_data:
                comparisons = paper.get("improvements", {}).get("baseline_comparisons", [])
                quality = paper.get("quality_assessment", {}).get("overall_score", "LOW")
                for comp in comparisons:
                    all_outcomes.append({
                        "outcome": f"{comp.get('task')} - {comp.get('metric')}",
                        "quality": quality
                    })
            
            # Simplified aggregation: Group by outcome name and take average quality?
            # For now, just list them or take top 5
            grade_assessments = []
            for out in all_outcomes[:5]: # Limit to top 5 for summary
                assessment = GRADEAssessment.assess_certainty(study_quality=out["quality"])
                assessment["outcome"] = out["outcome"]
                grade_assessments.append(assessment)
                
            self.grade_summary = GRADEAssessment.generate_grade_summary(grade_assessments)

    def step_write_paper(self):
        logging.info("\n--- Phase 7: Writing ---")
        writer = PaperWriter(model_name=self.config["writing"]["model"])
        
        # Generate Structure
        self.paper_structure = writer.generate_structure(self.extracted_data)
        
        # Write Sections with Deep Integration
        sections = self.config.get("paper_structure", {}).get("sections", [
            "Abstract", "1. Introduction", "2. Methodology", 
            "3. Results", "4. Discussion", "5. Conclusion"
        ])
        
        full_paper = ""
        previous_summary = ""
        
        for section in sections:
            logging.info(f"  Writing {section}...")
            instructions = f"Follow the plan for '{section}' defined in the Structure below.\nStructure:\n{self.paper_structure}"
            
            # Inject Gap Report into Discussion
            if "Discussion" in section and hasattr(self, 'gap_report'):
                instructions += f"\n\nIncorporate this Literature Gap Analysis:\n{self.gap_report}"
                
            # Inject Visuals into Methodology
            if "Methodology" in section and os.path.exists("images/prisma_flow_diagram.png"):
                instructions += "\n\nIMPORTANT: You MUST include the PRISMA diagram using: ![PRISMA 2020 Flow Diagram](images/prisma_flow_diagram.png)"
            
            section_text = writer.write_section(section, instructions, self.extracted_data, previous_summary)
            full_paper += section_text + "\n\n"
            previous_summary += f"Summary of {section}: ...\n"
            
        self.draft_paper = full_paper
        with open("final_paper.md", "w") as f:
            f.write(self.draft_paper)

    def step_final_review(self):
        logging.info("\n--- Phase 8: Final Review ---")
        mcp_reviewer = MCPFinalReviewer(model_name=self.config["writing"]["model"])
        
        with open("final_paper.md", "r") as f:
            paper_text = f.read()
            
        # Citation Validation & Auto-Correction
        if self.config["analysis"]["run_citation_validator"]:
            validator = CitationValidator(self.extracted_data)
            report = validator.generate_validation_report(paper_text)
            if "Invalid/Unknown Citations" in report:
                logging.info("Triggering Auto-Correction for Citations...")
                correction_prompt = f"Fix these invalid citations:\n{report}"
                paper_text = mcp_reviewer.targeted_patch(paper_text, correction_prompt)
        
        # Iterative Review
        improved_paper, review = mcp_reviewer.iterative_improvement_loop(paper_text, initial_focus_areas=self.config["review"]["focus_areas"])
        
        with open("final_paper_A_plus.md", "w") as f:
            f.write(improved_paper)
