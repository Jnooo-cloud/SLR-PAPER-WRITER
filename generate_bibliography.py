import json
import pandas as pd

def generate_apa_citation(data):
    # Authors
    authors = data.get('Authors', [])
    if isinstance(authors, list):
        if len(authors) > 2:
            author_str = f"{authors[0]} et al."
        else:
            author_str = " & ".join(authors)
    else:
        author_str = str(authors)
    
    if not author_str or author_str == "nan":
        author_str = "Unknown"
    
    # Year
    year = data.get('Year', 'n.d.')
    if not year or str(year) == "nan":
        year = "n.d."
    
    # Title
    title = data.get('Title', 'Untitled')
    
    # Venue/Journal
    venue = data.get('Source', '')
    if not venue or venue == '':
        venue = "arXiv preprint"
    
    # DOI/URL
    url = data.get('URL', '')
    doi = data.get('DOI', '')
    
    citation = f"{author_str} ({year}). {title}. *{venue}*."
    if doi and str(doi) != "nan":
        citation += f" https://doi.org/{doi}"
    elif url and str(url) != "nan":
        citation += f" {url}"
    
    return citation

def generate_bibliography_string(json_path="slr_extracted_data.json"):
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return "Error: slr_extracted_data.json not found."

    bibliography = "\n# Bibliography\n\n"
    
    citations = []
    for entry in data:
        citations.append(generate_apa_citation(entry))
    
    # Sort alphabetically
    citations.sort()
    
    for citation in citations:
        bibliography += f"* {citation}\n"
        
    return bibliography

def main():
    print(generate_bibliography_string())

if __name__ == "__main__":
    main()
