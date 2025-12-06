import requests
import time
from typing import List
from search_modules import SemanticScholarSearch, Paper

class Snowballing:
    def __init__(self, search_engine: SemanticScholarSearch):
        self.engine = search_engine

    def forward_snowballing(self, seed_papers: List[Paper]) -> List[Paper]:
        """Get papers that cite the seed papers."""
        print("Starting Forward Snowballing...")
        citations = []
        for paper in seed_papers:
            # We need a paper ID (DOI or S2ID) to get citations
            paper_id = paper.doi
            if not paper_id:
                # Try to find the paper first to get an ID
                results = self.engine.search_keyword(paper.title, limit=1)
                if results:
                    paper_id = results[0].doi # Or S2ID if we stored it
                    # If we still don't have an ID, skip
                    if not paper_id: 
                         # Fallback: search by title and take the first result's ID if available
                         # For now, let's assume we can get it via search
                         pass

            if paper_id:
                details = self.engine.get_paper_details(paper_id)
                if details and hasattr(details, 'citations_list'): 
                    # Note: get_paper_details in search_modules needs to return the list of citing papers
                    # The current implementation of get_paper_details returns a Paper object, 
                    # but we might need to adjust it to return raw data or include the list in Paper object.
                    # Let's adjust this logic to be robust.
                    pass
        
        # Since the current SearchModule returns a Paper object which doesn't hold the full list of citations objects,
        # We need to extend the SemanticScholarSearch to specifically fetch citations.
        return citations

    def backward_snowballing(self, seed_papers: List[Paper]) -> List[Paper]:
        """Get papers referenced by the seed papers."""
        print("Starting Backward Snowballing...")
        references = []
        # Similar logic to forward, need to fetch references.
        return references

# Redefining Snowballing to use a more direct approach with the API
class Snowballer:
    def __init__(self, api_key: str = None):
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.headers = {"x-api-key": api_key} if api_key else {}

    def get_citations(self, paper_id: str, max_results: int = 50) -> List[Paper]:
        """Get papers citing the given paper ID."""
        url = f"{self.base_url}/paper/{paper_id}/citations"
        params = {"fields": "title,authors,year,abstract,url,externalIds,citationCount"}
        return self._fetch_connected_papers(url, params, max_results)

    def get_references(self, paper_id: str, max_results: int = 50) -> List[Paper]:
        """Get papers referenced by the given paper ID."""
        url = f"{self.base_url}/paper/{paper_id}/references"
        params = {"fields": "title,authors,year,abstract,url,externalIds,citationCount"}
        return self._fetch_connected_papers(url, params, max_results)

    def _fetch_connected_papers(self, url: str, params: dict, max_results: int) -> List[Paper]:
        papers = []
        offset = 0
        limit = 100 # Max limit for S2 API
        params["limit"] = limit
        
        while len(papers) < max_results:
            params["offset"] = offset
            try:
                print(f"    Fetching batch (offset={offset})...")
                response = requests.get(url, headers=self.headers, params=params)
                
                if response.status_code == 429:
                    print("    Rate limit hit. Waiting 5 seconds...")
                    time.sleep(5)
                    continue
                    
                if response.status_code != 200:
                    print(f"    Error fetching data: {response.status_code}")
                    break
                    
                data = response.json()
                batch_data = data.get("data", [])
                
                if not batch_data:
                    break
                    
                for item in batch_data:
                    if len(papers) >= max_results:
                        break
                    # The citing/referenced paper is inside 'citingPaper' or 'citedPaper'
                    paper_data = item.get("citingPaper") or item.get("citedPaper")
                    if paper_data:
                        papers.append(self._parse_paper_data(paper_data))
                
                # Check if we reached the end
                if len(batch_data) < limit:
                    break
                    
                offset += limit
                time.sleep(0.5) # Be nice to the API
                
            except Exception as e:
                print(f"Error in snowballing: {e}")
                break
                
        return papers

    def _parse_paper_data(self, item: dict) -> Paper:
        # Helper to convert raw dict to Paper object
        # This duplicates logic from search_modules, ideally should be shared.
        # For now, quick implementation.
        authors = [a["name"] for a in item.get("authors", [])] if item.get("authors") else []
        external_ids = item.get("externalIds", {})
        doi = external_ids.get("DOI")
        url = item.get("url") or (f"https://doi.org/{doi}" if doi else None)
        
        return Paper(
            title=item.get("title", "Unknown Title"),
            authors=authors,
            year=item.get("year"),
            abstract=item.get("abstract", ""),
            url=url,
            doi=doi,
            source="Semantic Scholar (Snowball)"
        )

import requests
