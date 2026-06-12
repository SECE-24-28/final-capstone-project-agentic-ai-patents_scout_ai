import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger("PatentCleaner")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def clean_patents(patents: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Cleans raw patents by enforcing quality rules:
    - Required fields check (title, abstract, patent_number)
    - Length constraints (title >= 10, abstract >= 50 characters)
    - Removes duplicates based on patent_number and title (case-insensitive)

    Args:
        patents (List[Dict[str, Any]]): List of raw patent dicts.

    Returns:
        Tuple[List[Dict[str, Any]], Dict[str, int]]: Cleaned list of patents and cleaning statistics.
    """
    logger.info("Starting patent cleaning process...")
    
    total_raw = len(patents)
    duplicates_count = 0
    missing_titles = 0
    missing_abstracts = 0
    malformed_records = 0
    
    seen_identifiers = set()
    cleaned_patents: List[Dict[str, Any]] = []

    for i, patent in enumerate(patents):
        # 1. Check if record is dict and has fields
        if not isinstance(patent, dict):
            malformed_records += 1
            continue
            
        pn = patent.get("patent_number")
        title = patent.get("title")
        abstract = patent.get("abstract")
        assignee = patent.get("assignee")
        year = patent.get("year")

        # Check basic existence of required values
        if pn is None or title is None or abstract is None:
            if pn is None:
                malformed_records += 1
            elif title is None:
                missing_titles += 1
            else:
                missing_abstracts += 1
            continue

        # Convert to string and strip whitespace
        pn_str = str(pn).strip()
        title_str = str(title).strip()
        abstract_str = str(abstract).strip()

        # 2. Check length constraints
        if len(title_str) < 10:
            malformed_records += 1
            continue
            
        if len(abstract_str) < 50:
            malformed_records += 1
            continue

        # 3. Deduplication (case-insensitive comparison of patent_number and title)
        # Create a unique case-insensitive identifier tuple
        dedup_id = (pn_str.lower(), title_str.lower())
        if dedup_id in seen_identifiers:
            duplicates_count += 1
            continue

        # Add to seen and build clean record
        seen_identifiers.add(dedup_id)
        
        clean_record = {
            "patent_number": pn_str,
            "title": title_str,
            "abstract": abstract_str,
            "assignee": str(assignee).strip() if assignee is not None else "Unknown Assignee",
            "year": int(year) if year is not None else None
        }
        cleaned_patents.append(clean_record)

    stats = {
        "total_raw_records": total_raw,
        "total_clean_records": len(cleaned_patents),
        "duplicates_removed": duplicates_count,
        "missing_titles_removed": missing_titles,
        "missing_abstracts_removed": missing_abstracts,
        "malformed_records_removed": malformed_records
    }
    
    logger.info(f"Cleaning complete: {len(cleaned_patents)} patents kept, {total_raw - len(cleaned_patents)} removed.")
    logger.info(f"Statistics: {stats}")
    
    return cleaned_patents, stats
