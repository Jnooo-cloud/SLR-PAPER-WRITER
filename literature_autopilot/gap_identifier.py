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

    def identify_mechanism_gaps(self, extracted_data):
        """Detaillierte Lückenanalyse pro Mechanismus"""
        # Placeholder for more detailed analysis if needed
        return []

    def identify_task_coverage_gaps(self, extracted_data):
        """Welche Aufgaben sind unterrepräsentiert?"""
        common_benchmarks = {
            "GSM8K": "Math reasoning",
            "MATH": "Math competition",
            "HumanEval": "Code generation",
            "MMLU": "General knowledge",
            "TruthfulQA": "Factuality",
            "HellaSwag": "Common sense",
            "ARC": "Science reasoning"
        }
        
        covered_benchmarks = set()
        for paper in extracted_data:
            tasks = paper.get("improvements", {}).get("baseline_comparisons", [])
            for task in tasks:
                task_name = task.get("task", "")
                for bench in common_benchmarks:
                    if bench.lower() in task_name.lower():
                        covered_benchmarks.add(bench)
        
        gaps = {bench: info for bench, info in common_benchmarks.items() 
               if bench not in covered_benchmarks}
        
        return gaps
    
    def identify_model_coverage_gaps(self, extracted_data):
        """Welche Modelle sind unterrepräsentiert?"""
        common_models = ["GPT-3", "GPT-4", "Claude", "LLaMA", "Mistral", "PaLM"]
        covered_models = set()
        
        for paper in extracted_data:
            baseline = paper.get("improvements", {}).get("baseline_comparisons", [])
            for comp in baseline:
                model = comp.get("baseline_model", "")
                for cm in common_models:
                    if cm.lower() in model.lower():
                        covered_models.add(cm)
        
        gaps = [m for m in common_models if m not in covered_models]
        return gaps

    def generate_gap_report(self) -> str:
        """Generate a markdown report of identified gaps."""
        analysis = self.identify_gaps()
        task_gaps = self.identify_task_coverage_gaps(self.data)
        model_gaps = self.identify_model_coverage_gaps(self.data)
        
        report = "## Literature Gap Analysis\n\n"
        
        report += "### Mechanism Distribution\n"
        for mech, count in analysis["mechanism_distribution"].items():
            report += f"- {mech}: {count}\n"
            
        report += "\n### Identified Gaps\n"
        if analysis["identified_gaps"]:
            for gap in analysis["identified_gaps"]:
                report += f"- {gap}\n"
        
        report += "\n### Missing Benchmarks\n"
        for bench, desc in task_gaps.items():
            report += f"- {bench} ({desc})\n"
            
        report += "\n### Under-represented Models\n"
        for model in model_gaps:
            report += f"- {model}\n"
            
        return report
