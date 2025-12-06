import matplotlib.pyplot as plt
import pandas as pd
import os
from typing import List, Dict, Any

class SLRVisualizer:
    """Generate publication-quality visualizations for SLR papers."""
    
    def __init__(self, output_dir: str = "images"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def create_prisma_flow_diagram(self, search_results: int, after_screening: int, 
                                    after_fulltext: int, included: int) -> str:
        """Create PRISMA 2020 flow diagram."""
        
        filename = os.path.join(self.output_dir, "prisma_flow_diagram.png")
        
        fig, ax = plt.subplots(figsize=(8, 10))
        
        # Define boxes
        boxes = [
            {"y": 9, "text": f"Records identified\n(n={search_results})", "color": "#E8F4F8"},
            {"y": 7.5, "text": f"Records screened\n(n={after_screening})", "color": "#E8F4F8"},
            {"y": 6, "text": f"Full-text assessed\n(n={after_fulltext})", "color": "#E8F4F8"},
            {"y": 4.5, "text": f"Studies included\n(n={included})", "color": "#C8E6C9"}
        ]
        
        # Draw boxes and arrows
        for box in boxes:
            ax.add_patch(plt.Rectangle((1, box["y"]-0.4), 3, 0.8, 
                                       facecolor=box["color"], edgecolor="black", linewidth=2))
            ax.text(2.5, box["y"], box["text"], ha="center", va="center", fontsize=10, weight="bold")
        
        # Draw arrows
        for i in range(len(boxes)-1):
            ax.arrow(2.5, boxes[i]["y"]-0.5, 0, -0.4, head_width=0.2, head_length=0.1, fc="black", ec="black")
        
        ax.set_xlim(0, 5)
        ax.set_ylim(3, 10)
        ax.axis("off")
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close()
        
        print(f"Generated PRISMA diagram: {filename}")
        return filename
    
    def create_mechanism_comparison_table(self, mechanisms: List[Dict[str, Any]]) -> str:
        """Create comparison table for SRP, RE, ISCD."""
        
        filename = os.path.join(self.output_dir, "mechanism_comparison.png")
        
        # Create DataFrame
        # Expecting mechanisms to be a list of dicts with keys like 'Mechanism', 'Key Feature', 'Advantage', 'Limitation'
        df = pd.DataFrame(mechanisms)
        
        if df.empty:
            print("No data for mechanism comparison table.")
            return ""

        # Create table figure
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.axis("tight")
        ax.axis("off")
        
        table = ax.table(cellText=df.values, colLabels=df.columns, 
                        cellLoc="center", loc="center",
                        colWidths=[0.2] * len(df.columns))
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close()
        
        print(f"Generated mechanism comparison table: {filename}")
        return filename

    def create_year_distribution_chart(self, papers: List[Dict[str, Any]]) -> str:
        """Create a bar chart showing the distribution of papers by year."""
        filename = os.path.join(self.output_dir, "figure_1_year_distribution.png")
        
        years = [p.get("year") for p in papers if p.get("year")]
        if not years:
            return ""
            
        year_counts = pd.Series(years).value_counts().sort_index()
        
        plt.figure(figsize=(10, 6))
        year_counts.plot(kind='bar', color='skyblue', edgecolor='black')
        plt.title('Distribution of Included Studies by Year', fontsize=14)
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Number of Studies', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300)
        plt.close()
        
        print(f"Generated year distribution chart: {filename}")
        return filename
