import os
import time
import requests
import arxiv
from search_modules import Paper

class PDFRetriever:
    def __init__(self, download_dir: str = "pdfs"):
        self.download_dir = download_dir
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            
    def download_paper(self, paper: Paper) -> str:
        """
        Attempts to download the PDF for a given paper.
        Returns the local file path if successful, None otherwise.
        """
        safe_filename = "".join([c for c in paper.title if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_") + ".pdf"
        file_path = os.path.join(self.download_dir, safe_filename)
        
        # Skip if already exists
        if os.path.exists(file_path):
            return file_path
            
        print(f"Attempting to download PDF for: {paper.title}...")
        
        # Strategy 1: ArXiv (Check Source, URL, OR DOI)
        is_arxiv = (
            paper.source == "arXiv" or 
            "arxiv.org" in (paper.url or "") or
            (paper.doi and "arXiv" in paper.doi) or 
            (paper.doi and "10.48550" in paper.doi)
        )
        
        if is_arxiv:
            if self._download_from_arxiv(paper, file_path):
                return file_path
                
        # Strategy 2: Direct URL (if it ends in .pdf)
        if paper.url and paper.url.lower().endswith(".pdf"):
            if self._download_from_url(paper.url, file_path):
                return file_path

        # Strategy 3: Unpaywall (Legal Open Access from Universities/Repositories)
        if paper.doi:
            if self._download_from_unpaywall(paper.doi, file_path):
                return file_path
        
        # Strategy 4: Last Resort - Try searching ArXiv by title for ANY paper
        # (Many S2 papers are actually on ArXiv but missing the link/DOI in S2 metadata)
        print(f"  Fallback: Searching ArXiv by title...")
        if self._download_from_arxiv(paper, file_path):
            return file_path
            
        return None

    def _download_from_unpaywall(self, doi: str, save_path: str) -> bool:
        """
        Queries Unpaywall API to find a legal Open Access PDF.
        """
        email = "slr_bot_project@example.com" # Unpaywall requires an email
        url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                best_oa = data.get("best_oa_location", {})
                if best_oa and best_oa.get("url_for_pdf"):
                    pdf_url = best_oa.get("url_for_pdf")
                    print(f"  Found Unpaywall PDF: {pdf_url}")
                    return self._download_from_url(pdf_url, save_path)
        except Exception as e:
            print(f"  Unpaywall check failed: {e}")
        return False

    def _download_from_arxiv(self, paper: Paper, save_path: str) -> bool:
        time.sleep(3) # Respect ArXiv rate limit
        try:
            # Extract ID from URL or use external ID if we had it
            # URL format: http://arxiv.org/abs/2303.17651v1
            arxiv_id = None
            
            # 1. Try URL
            if paper.url and "arxiv.org/abs/" in paper.url:
                arxiv_id = paper.url.split("arxiv.org/abs/")[-1].split("v")[0]
            
            # 2. Try DOI (ArXiv DOIs look like 10.48550/arXiv.2303.17651)
            if not arxiv_id and paper.doi and "10.48550/arXiv." in paper.doi:
                arxiv_id = paper.doi.split("10.48550/arXiv.")[-1]
                
            # 3. Try Title Search (Fallback)
            if not arxiv_id:
                # Search by title to find ID
                # Use ti: prefix for title search to improve relevance
                query = f'ti:"{paper.title}"'
                search = arxiv.Search(query=query, max_results=3)
                results = list(search.results())
                
                if not results:
                    # Fallback to simple query if strict title search fails
                    search = arxiv.Search(query=paper.title, max_results=3)
                    results = list(search.results())

                if results:
                    # Normalize for comparison (remove non-alphanumeric, lowercase)
                    def normalize(s):
                        return "".join(c.lower() for c in s if c.isalnum())
                    
                    paper_title_norm = normalize(paper.title)
                    
                    for res in results:
                        res_title_norm = normalize(res.title)
                        # Check for exact match or substring match (if title is long enough)
                        if paper_title_norm == res_title_norm or \
                           (len(paper_title_norm) > 20 and paper_title_norm in res_title_norm):
                            arxiv_id = res.entry_id.split("/")[-1].split("v")[0]
                            print(f"  [ArXiv Search] Match found: {res.title} (ID: {arxiv_id})")
                            break
            
            if arxiv_id:
                print(f"  Found ArXiv ID: {arxiv_id}")
                paper_obj = next(arxiv.Client().results(arxiv.Search(id_list=[arxiv_id])))
                paper_obj.download_pdf(filename=os.path.basename(save_path), dirpath=os.path.dirname(save_path))
                print(f"  Success (ArXiv): {save_path}")
                return True
        except Exception as e:
            print(f"  ArXiv download failed: {e}")
        return False

    def _download_from_url(self, url: str, save_path: str) -> bool:
        try:
            response = requests.get(url, stream=True, timeout=15)
            if response.status_code == 200 and "application/pdf" in response.headers.get("Content-Type", ""):
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"  Success (Direct URL): {save_path}")
                return True
        except Exception as e:
            print(f"  Direct URL download failed: {e}")
        return False
