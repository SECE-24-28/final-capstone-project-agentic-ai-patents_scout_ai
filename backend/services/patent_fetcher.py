import os
import sys
import logging
import requests
from typing import List, Optional
from langdetect import detect
from backend.models.pydantic_models import Patent

logger = logging.getLogger("PatentFetcher")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def is_english(title: str, abstract: str) -> bool:
    """
    Checks if a patent's title and abstract are in English.
    Rejects any text containing CJK characters or identified by langdetect as non-English.
    """
    def detect_lang(text: str) -> str:
        if not text or not text.strip():
            return 'en'
        # Detect CJK characters (Chinese, Japanese, Korean) and reject immediately
        for char in text:
            if '\u4e00' <= char <= '\u9fff' or '\u3040' <= char <= '\u30ff' or '\uac00' <= char <= '\ud7af':
                return 'non-en'
        try:
            return detect(text)
        except Exception:
            # Treat short or numerical snippets as English if no CJK character is present
            return 'en'

    title_lang = detect_lang(title)
    abstract_lang = detect_lang(abstract)
    return title_lang == 'en' and abstract_lang == 'en'

def fetch_patents(domain: str, limit: int = 60, max_results: Optional[int] = None) -> List[Patent]:
    """
    Fetch patents related to a technology domain using Google Patents XHR query.
    Filters out non-English patents and returns a list of normalized Patent objects.

    Args:
        domain (str): The search query or technology domain.
        limit (int): Maximum number of patents to retrieve. Defaults to 60.
        max_results (Optional[int]): Deprecated parameter for backward compatibility.

    Returns:
        List[Patent]: List of normalized, English-only Patent objects.
    """
    actual_limit = limit if max_results is None else max_results
    
    print(f"[Patent Fetcher] Searching Google Patents for: {domain}")
    logger.info(f"Querying Google Patents for domain: {domain}")

    # Request slightly more patents to compensate for non-English filtering
    num_to_request = min(100, actual_limit * 2)
    query_param = f"q={requests.utils.quote(domain)}&num={num_to_request}"
    xhr_url = f"https://patents.google.com/xhr/query?url={requests.utils.quote(query_param)}&exp="

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://patents.google.com/",
    }

    try:
        response = requests.get(xhr_url, headers=headers, timeout=15)
        if response.status_code != 200:
            logger.error(f"Google Patents returned HTTP status: {response.status_code}")
            print(f"[Patent Fetcher] Google Patents query failed with status: {response.status_code}")
            return []

        data = response.json()
    except Exception as err:
        logger.error(f"Failed to retrieve/parse Google Patents: {err}")
        print(f"[Patent Fetcher] Error retrieving patents: {err}")
        return []

    # Extract patents list from XHR response JSON structure
    clusters = data.get("results", {}).get("cluster", [])
    raw_list = []
    if clusters and isinstance(clusters, list):
        raw_list = clusters[0].get("result", [])

    print(f"[Patent Fetcher] Retrieved {len(raw_list)} raw patents")

    english_patents: List[Patent] = []
    non_english_count = 0

    for item in raw_list:
        patent_info = item.get("patent", {})
        title = patent_info.get("title", "").strip()
        abstract = patent_info.get("snippet", "").strip()

        # Reject non-English patents
        if not is_english(title, abstract):
            non_english_count += 1
            continue

        patent_number = patent_info.get("publication_number", "Unknown Patent ID").strip()
        assignee = patent_info.get("assignee", "Unknown Assignee").strip()

        # Extract Year
        pub_date = patent_info.get("publication_date", "")
        year = None
        if pub_date and isinstance(pub_date, str):
            try:
                year = int(pub_date.split("-")[0])
            except ValueError:
                pass

        # Construct and dynamic attributes for testing/compatibility requirements
        p = Patent(
            title=title,
            abstract=abstract,
            inventors=[assignee],
            year=year,
            patent_id=patent_number,
            source="google_patents"
        )
        object.__setattr__(p, 'assignee', assignee)
        object.__setattr__(p, 'patent_number', patent_number)
        
        english_patents.append(p)

    print(f"[Patent Fetcher] Filtered {non_english_count} non-English patents")
    
    # Truncate to the requested limit
    final_patents = english_patents[:actual_limit]
    print(f"[Patent Fetcher] Returning {len(final_patents)} English patents")

    return final_patents
