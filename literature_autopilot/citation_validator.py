import re
from typing import List, Dict, Tuple, Any

class CitationValidator:
    """Validate citations against actual papers."""
    
    def __init__(self, extracted_data: List[Dict[str, Any]]):
        self.papers = extracted_data
        # Create a lookup for easier validation
        # We store authors (normalized) and year
        self.paper_lookup = []
        for p in extracted_data:
            authors = p.get("authors", [])
            if isinstance(authors, str):
                # Handle case where authors might be a string
                authors = [a.strip() for a in authors.split(",")]
            
            # Normalize authors: take last names, lowercase
            normalized_authors = []
            for a in authors:
                # Simple heuristic: assume last word is last name
                parts = a.strip().split()
                if parts:
                    normalized_authors.append(parts[-1].lower())
            
            self.paper_lookup.append({
                "authors": normalized_authors,
                "year": str(p.get("year", "")),
                "title": p.get("title", ""),
                "original_data": p
            })
    
    def validate_citations_in_text(self, text: str) -> Dict[str, List[Tuple[str, str]]]:
        """Check if citations in text match actual papers."""
        
        # Regex for APA style citations: (Author, Year) or (Author et al., Year)
        # Examples: (Smith, 2023), (Smith & Jones, 2024), (Smith et al., 2025)
        # This regex is a simplification but covers most standard cases
        citation_pattern = r"\(([^)]+?),\s*(\d{4})\)"
        citations = re.findall(citation_pattern, text)
        
        validation_results = {
            "valid": [],
            "invalid": [],
            "suspicious": []
        }
        
        for author_part, year in citations:
            # Extract the primary author's last name for matching
            # "Smith" -> "smith"
            # "Smith & Jones" -> "smith"
            # "Smith et al." -> "smith"
            primary_author = author_part.split("&")[0].split("et al")[0].strip().split()[-1].lower()
            
            found = False
            for paper in self.paper_lookup:
                # Check year match
                if paper["year"] == year:
                    # Check author match
                    # We check if the primary author from citation exists in the paper's author list
                    if primary_author in paper["authors"]:
                        found = True
                        break
            
            if found:
                validation_results["valid"].append((author_part, year))
            else:
                # If not found, it might be a hallucination or a formatting issue
                # We flag it as suspicious/invalid
                validation_results["invalid"].append((author_part, year))
        
        return validation_results

    def generate_validation_report(self, text: str) -> str:
        """Generate a human-readable report of citation validation."""
        results = self.validate_citations_in_text(text)
        
        report = "## Citation Validation Report\n\n"
        
        if results["invalid"]:
            report += "### ⚠️ Invalid/Unknown Citations (Potential Hallucinations)\n"
            for author, year in set(results["invalid"]):
                report += f"- ({author}, {year})\n"
            report += "\n"
        else:
            report += "✅ No invalid citations detected.\n\n"
            
        report += f"Total Citations Checked: {len(results['valid']) + len(results['invalid'])}\n"
        report += f"Valid Citations: {len(results['valid'])}\n"
        
        return report
