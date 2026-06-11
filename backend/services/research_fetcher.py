import time
import requests
import xml.etree.ElementTree as ET
from typing import List, Optional
from backend.models.pydantic_models import Paper
from backend.config import settings

def fetch_arxiv_papers(domain: str, max_results: int = 15) -> List[Paper]:
    """
    Fetch papers from the arXiv API using ElementTree XML parsing.
    """
    print(f"[Research Fetcher] Fetching papers from arXiv for query: '{domain}'...")
    url = "http://export.arxiv.org/api/query"
    # Search for domain in title, abstract, or body
    params = {
        "search_query": f'all:"{domain}"',
        "start": 0,
        "max_results": max_results
    }
    
    papers = []
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code != 200:
            print(f"[Research Fetcher] arXiv returned status code {response.status_code}")
            return papers
            
        xml_content = response.content
        namespaces = {'atom': 'http://www.w3.org/2005/Atom'}
        root = ET.fromstring(xml_content)
        entries = root.findall('atom:entry', namespaces)
        
        for entry in entries:
            title_el = entry.find('atom:title', namespaces)
            title = title_el.text.strip().replace("\n", " ") if title_el is not None else ""
            
            summary_el = entry.find('atom:summary', namespaces)
            abstract = summary_el.text.strip().replace("\n", " ") if summary_el is not None else ""
            
            # Extract author names
            authors = []
            author_els = entry.findall('atom:author', namespaces)
            for author_el in author_els:
                name_el = author_el.find('atom:name', namespaces)
                if name_el is not None and name_el.text:
                    authors.append(name_el.text.strip())
                    
            # Extract published year
            published_el = entry.find('atom:published', namespaces)
            year = None
            if published_el is not None and published_el.text:
                try:
                    # e.g., '2021-08-25T13:45:00Z'
                    year = int(published_el.text.split("-")[0])
                except ValueError:
                    pass
            
            # Extract URL
            url_el = entry.find("atom:id", namespaces)
            paper_url = url_el.text.strip() if url_el is not None else None
            
            if title and abstract:
                papers.append(Paper(
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    year=year,
                    source="arXiv",
                    url=paper_url
                ))
    except Exception as e:
        print(f"[Research Fetcher] Error fetching from arXiv: {e}")
        
    print(f"[Research Fetcher] arXiv returned {len(papers)} papers.")
    return papers

def fetch_semantic_scholar_papers(domain: str, limit: int = 15) -> List[Paper]:
    """
    Fetch papers from Semantic Scholar with exponential backoff for rate limiting.
    """
    print(f"[Research Fetcher] Fetching papers from Semantic Scholar for query: '{domain}'...")
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": domain,
        "limit": limit,
        "fields": "title,abstract,authors,year,url"
    }
    
    headers = {}
    if settings.SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = settings.SEMANTIC_SCHOLAR_API_KEY
        
    papers = []
    retries = 3
    delay = 2 # initial backoff delay in seconds
    
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15)
            if response.status_code == 429:
                # Rate limit hit
                print(f"[Research Fetcher] Semantic Scholar 429 Rate Limit (Attempt {attempt+1}/{retries}). Sleeping {delay}s...")
                time.sleep(delay)
                delay *= 2
                continue
            elif response.status_code != 200:
                print(f"[Research Fetcher] Semantic Scholar returned status code {response.status_code}")
                break
                
            data = response.json()
            data_list = data.get("data", [])
            for item in data_list:
                title = item.get("title", "")
                abstract = item.get("abstract") or ""
                year = item.get("year")
                paper_url = item.get("url")
                
                authors = []
                for author_obj in item.get("authors", []):
                    name = author_obj.get("name")
                    if name:
                        authors.append(name)
                        
                if title and abstract:
                    papers.append(Paper(
                        title=title,
                        abstract=abstract,
                        authors=authors,
                        year=year,
                        source="Semantic Scholar",
                        url=paper_url
                    ))
            break # success
        except Exception as e:
            print(f"[Research Fetcher] Error fetching from Semantic Scholar: {e}")
            break
            
    print(f"[Research Fetcher] Semantic Scholar returned {len(papers)} papers.")
    return papers

def reconstruct_abstract(inverted_index: Optional[dict]) -> str:
    """
    Reconstruct plaintext abstract from OpenAlex's abstract_inverted_index.
    """
    if not inverted_index:
        return ""
    try:
        max_pos = 0
        for positions in inverted_index.values():
            for pos in positions:
                if pos > max_pos:
                    max_pos = pos
        words = [None] * (max_pos + 1)
        for word, positions in inverted_index.items():
            for pos in positions:
                words[pos] = word
        return " ".join(w for w in words if w is not None)
    except Exception as e:
        print(f"[Research Fetcher] Error reconstructing abstract: {e}")
        return ""

def fetch_openalex_papers(domain: str, max_results: int = 25) -> List[Paper]:
    """
    Fetch papers from the OpenAlex API and convert to Paper models.
    """
    print(f"[Research Fetcher] Fetching papers from OpenAlex for query: '{domain}'...")
    url = "https://api.openalex.org/works"
    
    email = settings.OPENALEX_API_EMAIL or "patentscout-ai@example.com"
    params = {
        "search": domain,
        "per_page": max_results,
        "mailto": email
    }
    
    papers = []
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code != 200:
            print(f"[Research Fetcher] OpenAlex returned status code {response.status_code}")
            return papers
            
        data = response.json()
        results = data.get("results", [])
        
        for item in results:
            title = item.get("title") or ""
            # Reconstruct abstract from inverted index
            abstract_inverted = item.get("abstract_inverted_index")
            abstract = reconstruct_abstract(abstract_inverted)
            
            # Extract year
            year = item.get("publication_year")
            
            # Extract authors
            authors = []
            for authorship in item.get("authorships", []):
                author_name = authorship.get("author", {}).get("display_name")
                if author_name:
                    authors.append(author_name)
                    
            # Extract source
            source = None
            primary_location = item.get("primary_location")
            if primary_location:
                source_obj = primary_location.get("source")
                if source_obj:
                    source = source_obj.get("display_name")
            if not source:
                source = "OpenAlex"
                
            # Extract URL
            paper_url = item.get("doi") or (primary_location or {}).get("landing_page_url") or (primary_location or {}).get("pdf_url")
            
            # Only include papers with title and abstract
            if title and abstract:
                papers.append(Paper(
                    title=title.strip(),
                    abstract=abstract.strip(),
                    authors=authors,
                    year=year,
                    source=source,
                    url=paper_url
                ))
    except Exception as e:
        print(f"[Research Fetcher] Error fetching from OpenAlex: {e}")
        
    print(f"[Research Fetcher] OpenAlex returned {len(papers)} papers.")
    return papers

def fetch_all_papers(domain: str, max_results: int = 15) -> List[Paper]:
    """
    Query Semantic Scholar, arXiv, and OpenAlex, deduplicating papers by title similarity.
    """
    papers = []
    
    # 1. Fetch from Semantic Scholar
    ss_papers = []
    try:
        ss_papers = fetch_semantic_scholar_papers(domain, limit=max_results)
    except Exception as e:
        print(f"[Research Fetcher] Error in Semantic Scholar fetcher: {e}")
    papers.extend(ss_papers)
    
    # 2. Fetch from arXiv
    arxiv_papers = []
    try:
        arxiv_papers = fetch_arxiv_papers(domain, max_results=max_results)
    except Exception as e:
        print(f"[Research Fetcher] Error in arXiv fetcher: {e}")
        
    # 3. Fetch from OpenAlex
    openalex_papers = []
    try:
        openalex_papers = fetch_openalex_papers(domain, max_results=max_results)
    except Exception as e:
        print(f"[Research Fetcher] Error in OpenAlex fetcher: {e}")
        
    # Deduplicate by title (case-insensitive alphanumeric match)
    existing_titles = {p.title.lower().replace(" ", "") for p in papers}
    
    for ap in arxiv_papers:
        clean_title = ap.title.lower().replace(" ", "")
        if clean_title not in existing_titles:
            papers.append(ap)
            existing_titles.add(clean_title)
            
    for op in openalex_papers:
        clean_title = op.title.lower().replace(" ", "")
        if clean_title not in existing_titles:
            papers.append(op)
            existing_titles.add(clean_title)
            
    print(f"[Research Fetcher] Total unique papers after deduplication: {len(papers)}")
    return papers
