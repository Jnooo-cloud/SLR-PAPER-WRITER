import re
from typing import List, Dict, Any

class ContextManager:
    """Manage context size and optimize token usage."""
    
    @staticmethod
    def chunk_paper_for_review(paper_text: str, chunk_size: int = 50000) -> List[str]:
        """
        Split paper into chunks for review.
        Note: Gemini 1.5 Pro has 1M+ context, so chunking is less critical than for other models,
        but still good practice for very large documents or smaller models.
        """
        
        # Split by sections (Markdown headers)
        sections = re.split(r"(^## .*$)", paper_text, flags=re.MULTILINE)
        
        chunks = []
        current_chunk = ""
        
        for section in sections:
            if len(current_chunk) + len(section) > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = section
            else:
                current_chunk += section
        
        if current_chunk:
            chunks.append(current_chunk)
        
        # Fallback if no headers found or chunks still too big
        if not chunks:
            return [paper_text[i:i+chunk_size] for i in range(0, len(paper_text), chunk_size)]
            
        return chunks
    
    @staticmethod
    def summarize_extracted_data(data: List[Dict[str, Any]], max_papers: int = 20) -> str:
        """Create a summary of extracted data to fit in context."""
        
        # Take top papers by quality (assuming quality_assessment exists)
        # If not, just take the first ones
        def get_score(item):
            qa = item.get("quality_assessment", {})
            score = qa.get("overall_score", "LOW")
            if score == "HIGH": return 3
            if score == "MEDIUM": return 2
            return 1
            
        sorted_data = sorted(data, key=get_score, reverse=True)
        
        summary = "## Summary of Extracted Papers\n\n"
        for paper in sorted_data[:max_papers]:
            title = paper.get("paper_title") or paper.get("title", "Unknown Title")
            mech = paper.get("methodological_differences", {}).get("mechanism_type", "Unknown Mechanism")
            
            qa = paper.get("quality_assessment", {})
            score = qa.get("overall_score", "N/A")
            
            summary += f"- **{title}**: {mech} (Quality: {score})\n"
            
            # Add key improvements if available
            improvements = paper.get("improvements", {}).get("synthesis", {}).get("overall_pattern", "")
            if improvements:
                summary += f"  - Improvement: {improvements[:100]}...\n"
        
        return summary
