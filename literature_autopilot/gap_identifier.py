from typing import List, Dict, Any
from collections import Counter

class GapIdentifier:
    """Identify literature gaps and suggest future research directions."""
    
    def __init__(self, extracted_data: List[Dict[str, Any]]):
        self.data = extracted_data
        
    def identify_gaps(self) -> Dict[str, Any]:
        """Analyze data to find gaps."""
        
        # 1. Mechanism Distribution
        mechanisms = [d.get("methodological_differences", {}).get("mechanism_type", "Unknown") for d in self.data]
        mech_counts = Counter(mechanisms)
        
        # 2. Task/Domain Coverage
        tasks = []
        for d in self.data:
            tasks.extend(d.get("improvements", {}).get("evaluation_setup", {}).get("tasks_and_domains", []))
        task_counts = Counter(tasks)
        
        # 3. Identify Under-explored Areas
        gaps = []
        
        # Check for under-represented mechanisms
        total_papers = len(self.data)
        if total_papers > 0:
            for mech, count in mech_counts.items():
                if count / total_papers < 0.2: # Less than 20% representation
                    gaps.append(f"Mechanism '{mech}' is under-explored (only {count} papers).")
            
            # Check for missing common tasks (simple heuristic)
            common_benchmarks = ["GSM8K", "MATH", "HumanEval", "MMLU"]
            for bench in common_benchmarks:
                if not any(bench.lower() in t.lower() for t in tasks):
                    gaps.append(f"Benchmark '{bench}' is missing from the evaluated tasks.")
                    
        return {
            "mechanism_distribution": dict(mech_counts),
            "task_distribution": dict(task_counts),
            "identified_gaps": gaps
        }

    def generate_gap_report(self) -> str:
        """Generate a markdown report of identified gaps."""
        analysis = self.identify_gaps()
        
        report = "## Literature Gap Analysis\n\n"
        
        report += "### Mechanism Distribution\n"
        for mech, count in analysis["mechanism_distribution"].items():
            report += f"- {mech}: {count}\n"
            
        report += "\n### Identified Gaps\n"
        if analysis["identified_gaps"]:
            for gap in analysis["identified_gaps"]:
                report += f"- {gap}\n"
        else:
            report += "No significant gaps identified based on current heuristics.\n"
            
        return report
