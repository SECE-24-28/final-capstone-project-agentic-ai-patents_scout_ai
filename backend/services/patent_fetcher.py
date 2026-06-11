import requests
from typing import List, Optional
from backend.models.pydantic_models import Patent
from backend.config import settings

def fetch_patents(domain: str, max_results: Optional[int] = None, limit: Optional[int] = None) -> List[Patent]:
    """
    Fetch patents from the PatentsView API.
    If the API fails, it falls back to generating query-based mock patents to ensure stability.
    """
    count = limit if limit is not None else (max_results if max_results is not None else 15)
    print(f"[Patent Fetcher] Querying PatentsView for domain: '{domain}'...")
    url = "https://api.patentsview.org/patents/query"
    
    # We query for domain terms in title or abstract
    payload = {
        "q": {
            "_or": [
                {"_text_any": {"patent_title": domain}},
                {"_text_any": {"patent_abstract": domain}}
            ]
        },
        "f": ["patent_title", "patent_abstract", "patent_number", "patent_date", "inventor_first_name", "inventor_last_name"],
        "o": {"per_page": count}
    }
    
    patents = []
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            raw_patents = data.get("patents", [])
            if raw_patents is None:
                raw_patents = []
                
            for p in raw_patents:
                title = p.get("patent_title", "")
                abstract = p.get("patent_abstract") or ""
                patent_id = p.get("patent_number", "")
                
                # Extract issue year from patent_date (YYYY-MM-DD)
                patent_date = p.get("patent_date", "")
                year = None
                if patent_date:
                    try:
                        year = int(patent_date.split("-")[0])
                    except ValueError:
                        pass
                
                # Extract inventors
                inventors = []
                raw_inventors = p.get("inventors", [])
                if raw_inventors:
                    for inv in raw_inventors:
                        first = inv.get("inventor_first_name") or ""
                        last = inv.get("inventor_last_name") or ""
                        name = f"{first} {last}".strip()
                        if name:
                            inventors.append(name)
                            
                if title and patent_id:
                    patents.append(Patent(
                        title=title,
                        abstract=abstract,
                        inventors=inventors,
                        year=year,
                        patent_id=patent_id,
                        source="PatentsView"
                    ))
        else:
            print(f"[Patent Fetcher] PatentsView API returned status code {response.status_code}. Using fallback generator...")
            patents = get_mock_patents(domain, count)
    except Exception as e:
        print(f"[Patent Fetcher] Error querying PatentsView API: {e}. Using fallback generator...")
        patents = get_mock_patents(domain, count)
        
    print(f"[Patent Fetcher] Returned {len(patents)} patents.")
    return patents

def get_mock_patents(domain: str, count: int) -> List[Patent]:
    """
    Generates realistic looking mock patents containing domain terms for demonstration and testing stability.
    """
    mock_data = [
        {
            "title": f"Autonomous System and Method for {domain}",
            "abstract": f"An automated method and system for controlling and optimizing {domain} environments using cloud sensor nodes, machine learning confidence scores, and low-latency feedback networks.",
            "inventors": ["John Doe", "Jane Smith"],
            "patent_id": "US10234857B2",
            "year": 2023
        },
        {
            "title": f"Energy-Efficient Controller for {domain} Operations",
            "abstract": f"A controller circuit designed to optimize resource allocation and power consumption during {domain} processes, featuring dynamic load adaptation and a secure wireless interface.",
            "inventors": ["Robert Johnson"],
            "patent_id": "US11874639B1",
            "year": 2024
        },
        {
            "title": f"Distributed Ledger Tracking Framework for {domain}",
            "abstract": f"A framework implementing a distributed ledger network to verify data integrity, trace transaction flows, and record compliance milestones in a system executing {domain}.",
            "inventors": ["Emily Davis", "Michael Brown"],
            "patent_id": "US9938472B2",
            "year": 2021
        }
    ]
    
    patents = []
    # Loop and select from mock templates to fill request count
    for i in range(count):
        tpl = mock_data[i % len(mock_data)]
        # Add slight modifications for unique IDs
        patents.append(Patent(
            title=tpl["title"],
            abstract=tpl["abstract"],
            inventors=tpl["inventors"],
            year=tpl["year"] - (i // len(mock_data)),
            patent_id=f"{tpl['patent_id'][:-2]}{i:02d}B2",
            source="PatentsView (Mock Fallback)"
        ))
    return patents
