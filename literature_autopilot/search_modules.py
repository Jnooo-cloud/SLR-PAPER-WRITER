import requests
import time
import arxiv
from typing import List, Dict, Optional

class Paper:
    def __init__(self, title: str, authors: List[str], year: int, abstract: str, url: str, doi: str = None, source: str = "Unknown"):
        self.title = title
        self.authors = authors
        self.year = year
        self.abstract = abstract
        self.url = url
        self.doi = doi
        self.source = source
        self.citations = 0
        self.references = []
        self.pdf_path = None

    def to_dict(self):
        return {
            "Title": self.title,
            "Authors": ", ".join(self.authors),
            "Year": self.year,
            "Abstract": self.abstract,
            "URL": self.url,
            "DOI": self.doi,
            "Source": self.source,
            "Citations": self.citations
        }

    def __repr__(self):
        return f"<Paper: {self.title} ({self.year})>"

class SemanticScholarSearch:
    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.headers = {"x-api-key": api_key} if api_key else {}

    def search_keyword(self, query: str, limit: int = 10) -> List[Paper]:
        """Search for papers by keyword."""
        url = f"{self.BASE_URL}/paper/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,authors,year,abstract,url,externalIds,citationCount"
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 429:
                print("Rate limit hit for Semantic Scholar. Waiting 5 seconds...")
                time.sleep(5)
                return self.search_keyword(query, limit)
            
            response.raise_for_status()
            data = response.json()
            
            papers = []
            if "data" in data:
                for item in data["data"]:
                    papers.append(self._parse_paper(item))
            return papers
        except Exception as e:
            print(f"Error searching Semantic Scholar: {e}")
            return []

    def get_paper_details(self, paper_id: str) -> Optional[Paper]:
        """Get details for a specific paper by ID (DOI, S2ID, arXiv ID)."""
        url = f"{self.BASE_URL}/paper/{paper_id}"
        params = {
            "fields": "title,authors,year,abstract,url,externalIds,citationCount,references,citations"
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 404:
                print(f"Paper not found: {paper_id}")
                return None
            
            response.raise_for_status()
            return self._parse_paper(response.json())
        except Exception as e:
            print(f"Error fetching paper details {paper_id}: {e}")
            return None

    def _parse_paper(self, item: Dict) -> Paper:
        authors = [a["name"] for a in item.get("authors", [])] if item.get("authors") else []
        external_ids = item.get("externalIds", {})
        doi = external_ids.get("DOI")
        url = item.get("url") or (f"https://doi.org/{doi}" if doi else None)
        
        paper = Paper(
            title=item.get("title", "Unknown Title"),
            authors=authors,
            year=item.get("year"),
            abstract=item.get("abstract", ""),
            url=url,
            doi=doi,
            source="Semantic Scholar"
        )
        paper.citations = item.get("citationCount", 0)
        return paper

class ArxivSearch:
    def __init__(self):
        self.client = arxiv.Client()

    def search_keyword(self, query: str, limit: int = 10) -> List[Paper]:
        """Search arXiv for papers."""
        search = arxiv.Search(
            query=query,
            max_results=limit,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        papers = []
        try:
            for result in self.client.results(search):
                papers.append(self._parse_result(result))
        except Exception as e:
            print(f"Error searching arXiv: {e}")
        
        return papers

    def _parse_result(self, result) -> Paper:
        return Paper(
            title=result.title,
            authors=[a.name for a in result.authors],
            year=result.published.year,
            abstract=result.summary,
            url=result.entry_id,
            doi=result.doi,
            source="arXiv"
        )
