import json
import os

import requests

def get_official_venue(title):
    """
    Attempts to find the official publication venue (e.g. 'NeurIPS 2024') 
    using Semantic Scholar, to replace 'ArXiv' citations.
    """
    try:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {"query": title, "limit": 1, "fields": "venue,year,publicationVenue"}
        
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                paper = data["data"][0]
                # Prefer full venue name
                venue = paper.get("publicationVenue", {}).get("name")
                if not venue:
                    venue = paper.get("venue")
                
                if venue and venue.lower() != "arxiv":
                    return f"{venue}"
    except Exception:
        pass
    return None

def generate_apa_citation(paper_data):
    """Generates an APA citation string from paper data."""
    details = paper_data.get("data", {}).get("study_details", {})
    
    authors = details.get("authors", [])
    year = details.get("year", "n.d.")
    title = details.get("title", "Unknown Title")
    venue = details.get("venue", "Unknown Venue")
    
    # Normalize Venue if it's ArXiv
    if venue and ("arxiv" in venue.lower() or "preprint" in venue.lower()):
        official_venue = get_official_venue(title)
        if official_venue:
            venue = official_venue
            print(f"  [Citation Normalizer] Upgraded venue for '{title[:20]}...': {venue}")
        else:
            venue = "arXiv Preprint" # Consistent naming
            
    # Fix Title Capitalization (Remove ALL CAPS)
    if title.isupper():
        title = title.title()
    
    # Format authors
    if not authors:
        author_str = "Unknown Author"
    elif len(authors) == 1:
        author_str = authors[0]
    elif len(authors) == 2:
        author_str = f"{authors[0]} & {authors[1]}"
    else:
        # APA 7th edition: list up to 20 authors. For simplicity here, we'll list up to 6 and use et al.
        if len(authors) > 6:
            author_str = ", ".join(authors[:6]) + ", et al."
        else:
            author_str = ", ".join(authors[:-1]) + ", & " + authors[-1]
            
    # Format citation
    # Remove asterisks from venue as per user request for DOCX cleanliness, 
    # or keep them if we fix the docx parser. User said "leave them out", 
    # likely referring to the visible * in docx. 
    # We will keep them here for Markdown correctness (Italics), 
    # but ensure md_to_docx strips them if it can't render.
    citation = f"{author_str} ({year}). {title}. *{venue}*."
    return citation

def main():
    json_path = "slr_extracted_data.json"
    md_path = "final_paper.md"
    
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found.")
        return

    print(f"Loading data from {json_path}...")
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    print(f"Generating bibliography for {len(data)} papers...")
    citations = []
    for paper in data:
        if paper.get("screening_decision") == "INCLUDE":
            citations.append(generate_apa_citation(paper))
            
    # Sort citations alphabetically
    citations.sort()
    
    bibliography_section = "\n\n# 6. Bibliography\n\n"
    for citation in citations:
        bibliography_section += f"*   {citation}\n"
        
    print(f"Appending bibliography to {md_path}...")
    with open(md_path, 'a') as f:
        f.write(bibliography_section)
        
    print("Done!")

if __name__ == "__main__":
    main()
