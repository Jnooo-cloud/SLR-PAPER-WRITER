import sys
import os
import argparse
# Add parent directory to path to allow importing literature_autopilot as a package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from literature_autopilot.pipeline import SLRPipeline

def main():
    print("Initializing SLR Bot (Pipeline Mode)...")
    
    # Parse Arguments
    parser = argparse.ArgumentParser(description="SLR Paper Writer Agent")
    
    # Core Flags
    parser.add_argument("--config", type=str, default="literature_autopilot/config.yaml", help="Path to config file")
    parser.add_argument("--screen", action="store_true", help="Enable LLM-based screening")
    parser.add_argument("--download-pdfs", action="store_true", help="Download PDFs for included papers")
    parser.add_argument("--extract-data", action="store_true", help="Run data extraction on PDFs")
    parser.add_argument("--write-paper", action="store_true", help="Write the full paper based on structure")
    parser.add_argument("--final-review", action="store_true", help="Run MCP-based final review and iterative improvement")
    
    # Skip Flags (for debugging/resuming)
    parser.add_argument("--skip-search", action="store_true", help="Skip search and snowballing phase")
    parser.add_argument("--skip-analysis", action="store_true", help="Skip analysis phase (Visuals, Gaps, GRADE)")
    
    args = parser.parse_args()
    
    # Initialize and Run Pipeline
    try:
        pipeline = SLRPipeline(config_path=args.config)
        pipeline.run(args)
    except Exception as e:
        print(f"Pipeline Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
