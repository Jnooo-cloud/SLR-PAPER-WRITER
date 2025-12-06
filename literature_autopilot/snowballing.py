import requests
import time
from typing import List, Set
from search_modules import SemanticScholarSearch, Paper

class Snowballer:
    def __init__(self, api_key: str = None):
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.headers = {"x-api-key": api_key} if api_key else {}
        self.visited_papers: Set[str] = set() # For cycle detection

    def get_citations(self, paper_id: str, max_results: int = 50) -> List[Paper]:
        """Get papers citing the given paper ID."""
        # Cycle detection check
        if paper_id in self.visited_papers:
            print(f"    Skipping cycle: {paper_id} already visited.")
            return []
        self.visited_papers.add(paper_id)

        url = f"{self.base_url}/paper/{paper_id}/citations"
        params = {"fields": "title,authors,year,abstract,url,externalIds,citationCount,venue"}
        return self._fetch_connected_papers(url, params, max_results, connection_type="citingPaper")

    def get_references(self, paper_id: str, max_results: int = 50) -> List[Paper]:
        """Get papers referenced by the given paper ID."""
        # Cycle detection check
        if paper_id in self.visited_papers:
             # Note: We might want to allow visiting the same paper for references if we are doing multi-hop,
             # but for single-hop snowballing, tracking visited is fine.
             # If we do recursive snowballing, we need to be careful.
             # For now, let's just track what we've expanded.
             pass
        self.visited_papers.add(paper_id)

        url = f"{self.base_url}/paper/{paper_id}/references"
        params = {"fields": "title,authors,year,abstract,url,externalIds,citationCount,venue"}
        return self._fetch_connected_papers(url, params, max_results, connection_type="citedPaper")

    def _fetch_connected_papers(self, url: str, params: dict, max_results: int, connection_type: str) -> List[Paper]:
        papers = []
        offset = 0
        limit = 100 # Max limit for S2 API
        params["limit"] = limit
        
        while len(papers) < max_results:
            params["offset"] = offset
            try:
                print(f"    Fetching batch (offset={offset})...")
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                
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
                    # Some entries might be None if the paper is not indexed well
                    paper_data = item.get(connection_type)
                    if paper_data:
                        paper_obj = self._parse_paper_data(paper_data)
                        if paper_obj:
                             papers.append(paper_obj)
                
                # Check if we reached the end
                if len(batch_data) < limit:
                    break
                    
                offset += limit
                time.sleep(0.5) # Be nice to the API
                
            except Exception as e:
                print(f"Error in snowballing: {e}")
                break
                
        return self._deduplicate_papers(papers)

    def _deduplicate_papers(self, papers: List[Paper]) -> List[Paper]:
        """Deduplicate papers based on DOI or Title."""
        unique_papers = {}
        for p in papers:
            # Prefer DOI as key, fallback to Title
            key = p.doi if p.doi else p.title.lower().strip()
            if key not in unique_papers:
                unique_papers[key] = p
        return list(unique_papers.values())

    def _parse_paper_data(self, item: dict) -> Paper:
        # Helper to convert raw dict to Paper object
        if not item.get("title"):
            return None
            
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
