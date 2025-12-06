import pandas as pd
import datetime

def generate_apa_citation(row):
    # Authors
    authors = row.get('Authors', 'Unknown')
    if pd.isna(authors):
        authors = "Unknown"
    
    # Year
    year = row.get('Year', 'n.d.')
    if pd.isna(year):
        year = "n.d."
    
    # Title
    title = row.get('Title', 'Untitled')
    
    # Venue/Journal
    venue = row.get('Venue', '')
    if pd.isna(venue) or venue == '':
        venue = "arXiv preprint"
    
    # DOI/URL
    url = row.get('URL', '')
    doi = row.get('DOI', '')
    
    citation = f"{authors} ({year}). {title}. *{venue}*."
    if doi:
        citation += f" https://doi.org/{doi}"
    elif url:
        citation += f" {url}"
    
    return citation

def main():
    try:
        df = pd.read_csv("slr_results_final.csv")
    except FileNotFoundError:
        print("Error: slr_results_final.csv not found.")
        return

    print("\n# Bibliography\n")
    
    citations = []
    for _, row in df.iterrows():
        citations.append(generate_apa_citation(row))
    
    # Sort alphabetically
    citations.sort()
    
    for citation in citations:
        print(f"* {citation}")

if __name__ == "__main__":
    main()
