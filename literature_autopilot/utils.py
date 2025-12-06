import pandas as pd
from typing import List
from literature_autopilot.search_modules import Paper

def deduplicate_papers(papers: List[Paper]) -> List[Paper]:
    """Deduplicate papers based on DOI (if available) or Title (normalized)."""
    seen_dois = set()
    seen_titles = set()
    unique_papers = []

    for paper in papers:
        # Check DOI
        if paper.doi and paper.doi in seen_dois:
            continue
        
        # Check Title (normalize: lowercase, remove non-alphanumeric)
        norm_title = "".join(c.lower() for c in paper.title if c.isalnum())
        if norm_title in seen_titles:
            continue

        if paper.doi:
            seen_dois.add(paper.doi)
        seen_titles.add(norm_title)
        unique_papers.append(paper)

    return unique_papers

def filter_papers(papers: List[Paper], keywords: List[str] = None, min_year: int = None) -> List[Paper]:
    """Filter papers by keywords in abstract/title and minimum year."""
    filtered = []
    for paper in papers:
        if min_year and paper.year and paper.year < min_year:
            continue
        
        if keywords:
            text = (paper.title + " " + paper.abstract).lower()
            if not any(k.lower() in text for k in keywords):
                continue
        
        filtered.append(paper)
    return filtered

def export_to_csv(papers: List[Paper], filename: str):
    """Export papers to CSV."""
    df = pd.DataFrame([p.to_dict() for p in papers])
    df.to_csv(filename, index=False)
    print(f"Exported {len(papers)} papers to {filename}")

def export_to_markdown(papers: List[Paper], filename: str):
    """Export papers to Markdown."""
    with open(filename, "w") as f:
        f.write("# Literature Review Results\n\n")
        for i, paper in enumerate(papers, 1):
            f.write(f"## {i}. {paper.title}\n")
            f.write(f"**Authors:** {', '.join(paper.authors)}\n\n")
            f.write(f"**Year:** {paper.year} | **Source:** {paper.source} | **Citations:** {paper.citations}\n\n")
            if paper.url:
                f.write(f"**Link:** [{paper.url}]({paper.url})\n\n")
            f.write(f"**Abstract:**\n{paper.abstract}\n\n")
            f.write("---\n\n")
    print(f"Exported {len(papers)} papers to {filename}")

def load_papers_from_csv(filename: str) -> List[Paper]:
    """Load papers from a CSV file."""
    try:
        df = pd.read_csv(filename)
        papers = []
        for _, row in df.iterrows():
            # Handle potential NaN values
            authors = str(row.get("Authors", "")).split(", ")
            year = int(row.get("Year")) if pd.notna(row.get("Year")) else None
            
            paper = Paper(
                title=row.get("Title", "Unknown"),
                authors=authors,
                year=year,
                abstract=row.get("Abstract", ""),
                url=row.get("URL", ""),
                doi=row.get("DOI", "") if pd.notna(row.get("DOI")) else None,
                source=row.get("Source", "Unknown")
            )
            paper.citations = int(row.get("Citations", 0)) if pd.notna(row.get("Citations")) else 0
            
            # Load screening info if available
            if "Screening Decision" in row:
                paper.screening_decision = row["Screening Decision"]
                
            papers.append(paper)
        print(f"Loaded {len(papers)} papers from {filename}")
        return papers
    except Exception as e:
        print(f"Error loading papers from {filename}: {e}")
        return []
