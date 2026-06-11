import os
import logging
import requests
from typing import List, Optional
from backend.models.pydantic_models import Patent

logger = logging.getLogger("PatentFetcher")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def fetch_patents(domain: str, limit: int = 60, max_results: Optional[int] = None) -> List[Patent]:
    """
    Fetch patents related to a technology domain.
    Attempts USPTO Open Data Portal first, then falls back to Lens.org if USPTO fails.
    If both fail, raises an error.

    Args:
        domain (str): The search query or technology domain.
        limit (int): Maximum number of patents to retrieve. Defaults to 60.
        max_results (Optional[int]): Deprecated parameter for backward compatibility.

    Returns:
        List[Patent]: List of normalized Patent objects.
    """
    actual_limit = limit if max_results is None else max_results
    
    # 1. Attempt USPTO Open Data Portal
    print("[Patent Fetcher] Querying USPTO...")
    logger.info("Attempting USPTO Open Data Portal retrieval...")
    try:
        uspto_patents = _fetch_uspto(domain, actual_limit)
        print(f"[Patent Fetcher] USPTO returned {len(uspto_patents)} patents")
        logger.info(f"Successfully retrieved {len(uspto_patents)} patents from USPTO.")
        return uspto_patents
    except Exception as uspto_err:
        print("[Patent Fetcher] USPTO failed")
        logger.warning(f"USPTO retrieval failed: {uspto_err}")
        
    # 2. Attempt Lens.org
    print("[Patent Fetcher] Switching to Lens.org")
    logger.info("Attempting Lens.org retrieval...")
    try:
        lens_patents = _fetch_lens(domain, actual_limit)
        print(f"[Patent Fetcher] Lens.org returned {len(lens_patents)} patents")
        logger.info(f"Successfully retrieved {len(lens_patents)} patents from Lens.org.")
        return lens_patents
    except Exception as lens_err:
        logger.error(f"Lens.org retrieval failed: {lens_err}")
        
    # 3. Both failed
    print("[Patent Fetcher] No patent data available")
    logger.error("Both USPTO and Lens.org patent retrieval failed.")
    raise RuntimeError("Failed to retrieve patent data from both USPTO and Lens.org.")

def _fetch_uspto(domain: str, limit: int) -> List[Patent]:
    """Helper to fetch from USPTO Open Data Portal."""
    uspto_key = os.getenv("USPTO_API_KEY") or os.getenv("PATENTSVIEW_API_KEY")
    if not uspto_key:
        raise ValueError("USPTO API Key (USPTO_API_KEY or PATENTSVIEW_API_KEY) is not configured in .env.")
        
    url = "https://api.uspto.gov/api/v1/patent/applications/search"
    headers = {
        "x-api-key": uspto_key,
        "accept": "application/json"
    }
    params = {
        "q": domain,
        "limit": limit
    }
    
    response = requests.get(url, headers=headers, params=params, timeout=15)
    if response.status_code != 200:
        raise requests.HTTPError(f"USPTO API returned status code {response.status_code}: {response.text}")
        
    data = response.json()
    results = data.get("patentApplicationSearchResults") or data.get("results") or data.get("data") or []
    
    patents = []
    for item in results:
        meta = item.get("applicationMetaData", {})
        title = meta.get("inventionTitle", "Unknown Title")
        
        # Abstract extraction
        abstract = "No abstract available"
        raw_abstract = item.get("abstractText") or meta.get("abstractText")
        if isinstance(raw_abstract, list) and len(raw_abstract) > 0:
            abstract = str(raw_abstract[0])
        elif raw_abstract:
            abstract = str(raw_abstract)
            
        patent_number = meta.get("patentNumber") or item.get("applicationNumberText") or "Unknown Patent ID"
        
        # Year extraction
        year = None
        date_str = meta.get("filingDate") or meta.get("grantDate") or meta.get("publicationDate")
        if date_str and isinstance(date_str, str):
            try:
                year = int(date_str.split("-")[0])
            except ValueError:
                pass
                
        # Assignee extraction
        assignee = (
            meta.get("firstApplicantName") or
            meta.get("assigneeName") or
            meta.get("firstInventorName") or
            "Unknown Assignee"
        )
        
        # Construct and add dynamic fields for compatibility
        p = Patent(
            title=title,
            abstract=abstract,
            inventors=[assignee],
            year=year,
            patent_id=patent_number,
            source="USPTO"
        )
        object.__setattr__(p, 'assignee', assignee)
        object.__setattr__(p, 'patent_number', patent_number)
        patents.append(p)
        
    return patents

def _fetch_lens(domain: str, limit: int) -> List[Patent]:
    """Helper to fetch from Lens.org."""
    lens_key = os.getenv("LENS_API_KEY")
    if not lens_key:
        raise ValueError("Lens.org API Key (LENS_API_KEY) is not configured in .env.")
        
    url = "https://api.lens.org/patent/search"
    headers = {
        "Authorization": f"Bearer {lens_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": {
            "query_string": {
                "query": domain
            }
        },
        "size": limit,
        "include": [
            "lens_id",
            "doc_number",
            "date_published",
            "biblio.invention_title",
            "biblio.parties.applicants",
            "abstract"
        ]
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=15)
    if response.status_code != 200:
        raise requests.HTTPError(f"Lens.org API returned status code {response.status_code}: {response.text}")
        
    data = response.json()
    results = data.get("data") or data.get("results") or []
    
    patents = []
    for item in results:
        biblio = item.get("biblio", {})
        
        # Title extraction
        title = "Unknown Title"
        titles = biblio.get("invention_title", [])
        if isinstance(titles, list) and len(titles) > 0:
            if isinstance(titles[0], dict):
                title = titles[0].get("text", "Unknown Title")
            else:
                title = str(titles[0])
        elif isinstance(titles, str):
            title = titles
            
        # Abstract extraction
        abstract = "No abstract available"
        abstracts = item.get("abstract", [])
        if isinstance(abstracts, list) and len(abstracts) > 0:
            if isinstance(abstracts[0], dict):
                abstract = abstracts[0].get("text", "No abstract available")
            else:
                abstract = str(abstracts[0])
        elif isinstance(abstracts, str):
            abstract = abstracts
            
        patent_number = item.get("doc_number") or item.get("lens_id") or "Unknown Patent ID"
        
        # Year extraction
        year = None
        pub_year = biblio.get("publication_year")
        if pub_year:
            try:
                year = int(pub_year)
            except (ValueError, TypeError):
                pass
        if not year:
            date_pub = item.get("date_published")
            if date_pub and isinstance(date_pub, str):
                try:
                    year = int(date_pub.split("-")[0])
                except ValueError:
                    pass
                    
        # Assignee extraction
        applicants = biblio.get("parties", {}).get("applicants", [])
        assignee_names = []
        if applicants and isinstance(applicants, list):
            for app in applicants:
                name = None
                if isinstance(app, dict):
                    name = app.get("name") or app.get("extracted_name", {}).get("value")
                if name:
                    assignee_names.append(str(name))
        assignee = ", ".join(assignee_names) if assignee_names else "Unknown Assignee"
        
        # Construct and add dynamic fields for compatibility
        p = Patent(
            title=title,
            abstract=abstract,
            inventors=[assignee],
            year=year,
            patent_id=patent_number,
            source="Lens.org"
        )
        object.__setattr__(p, 'assignee', assignee)
        object.__setattr__(p, 'patent_number', patent_number)
        patents.append(p)
        
    return patents
