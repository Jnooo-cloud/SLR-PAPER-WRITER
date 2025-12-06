import unittest
import json
import os
import shutil
import yaml
import sys
# Add parent directory to path to allow importing literature_autopilot as a package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from literature_autopilot.pipeline import SLRPipeline

class TestPipelineIntegration(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = "test_pipeline_output"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
            
        # Create dummy config
        self.config_path = os.path.join(self.test_dir, "test_config.yaml")
        self.config_data = {
            "slr_topic": "Test Topic",
            "search": {"keywords": ["test"], "max_search_results": 1, "seed_titles": []},
            "snowballing": {"enabled": False},
            "screening": {"provider": "openai", "model": "gpt-4o"},
            "extraction": {"model": "gemini-1.5-pro-latest"},
            "writing": {"model": "gemini-1.5-pro-latest"},
            "review": {"enabled": True, "focus_areas": ["Test Area"]},
            "analysis": {
                "run_visualizer": True,
                "run_citation_validator": True,
                "run_grade_assessment": True,
                "run_gap_identifier": True
            },
            "prompts": {
                "screening": "literature_autopilot/prompts/screening_prompt.md",
                "prescreening": "literature_autopilot/prompts/prescreening_prompt.md",
                "extraction": "literature_autopilot/prompts/extraction_prompt.md"
            },
            "paper_structure": {
                "sections": ["Abstract", "Introduction", "Methodology", "Results", "Discussion", "Conclusion"]
            }
        }
        with open(self.config_path, "w") as f:
            yaml.dump(self.config_data, f)
            
        # Create dummy extracted data
        self.extracted_data = [
            {
                "paper_title": "Paper A",
                "screening_decision": "INCLUDE",
                "methodological_differences": {"mechanism_type": "SRP", "specific_name": "Self-Refine"},
                "improvements": {
                    "baseline_comparisons": [{"task": "Math", "metric": "Accuracy"}],
                    "synthesis": {"overall_pattern": "Improved accuracy"}
                },
                "quality_assessment": {"overall_score": "HIGH"},
                "authors": ["Smith"],
                "year": 2023
            }
        ]
        with open("slr_extracted_data.json", "w") as f:
            json.dump(self.extracted_data, f)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists("slr_extracted_data.json"):
            os.remove("slr_extracted_data.json")
        if os.path.exists("final_paper.md"):
            os.remove("final_paper.md")
        if os.path.exists("slr_pipeline.log"):
            # Clean up log file if created
            pass

    def test_pipeline_analysis_step(self):
        print("\nTesting Pipeline Analysis Step...")
        pipeline = SLRPipeline(config_path=self.config_path)
        # Mock visualizer output dir to test_dir
        if pipeline.visualizer:
            pipeline.visualizer.output_dir = self.test_dir
            
        pipeline.step_analyze()
        
        # Check if visuals generated
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "prisma_flow_diagram.png")))
        
        # Check if Gap Report generated
        self.assertIsNotNone(pipeline.gap_report)
        self.assertIn("Literature Gap Analysis", pipeline.gap_report)
        
        # Check if GRADE Summary generated
        self.assertIsNotNone(pipeline.grade_summary)
        self.assertIn("GRADE Certainty of Evidence", pipeline.grade_summary)

if __name__ == '__main__':
    unittest.main()
