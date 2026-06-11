import os
import sys
import json
import logging
import requests
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("GooglePatentsFetchTest")

def safe_str(s: str) -> str:
    """Safely formats a string to be printable on consoles with restricted character maps (like CP1252)."""
    if not s:
        return ""
    encoding = sys.stdout.encoding or 'utf-8'
    try:
        return s.encode(encoding, errors='replace').decode(encoding)
    except Exception:
        return s.encode('ascii', errors='replace').decode('ascii')

def test_google_patents_fetch():
    print("=" * 60)
    print("Google Patents Programmatic Access Validation Script")
    print("=" * 60)

    # 1. Accept domain input (with safe fallback for non-interactive environments)
    if not sys.stdin.isatty():
        domain = "Smart Cities"
    else:
        try:
            domain = input("Enter technology domain to search (default: Smart Cities): ").strip()
            if not domain:
                domain = "Smart Cities"
        except Exception:
            domain = "Smart Cities"

    # Ensure search domain text is safely encoded
    domain_safe = safe_str(domain)
    print(f"\n[Google Patents] Starting query for domain: '{domain_safe}'...")

    # 2-3. Query Google Patents using XHR endpoint
    query_param = f"q={requests.utils.quote(domain)}&num=10"
    xhr_url = f"https://patents.google.com/xhr/query?url={requests.utils.quote(query_param)}&exp="

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://patents.google.com/",
    }

    try:
        response = requests.get(xhr_url, headers=headers, timeout=15)
    except Exception as req_err:
        print(f"\n[ERROR] Connection failed: {req_err}")
        sys.exit(1)

    # 4. Print HTTP response stats
    status_code = response.status_code
    content_type = response.headers.get("Content-Type", "")
    response_length = len(response.text)

    print(f"\nHTTP Response Statistics:")
    print(f"  - HTTP Status Code: {status_code}")
    print(f"  - Content Type: {content_type}")
    print(f"  - Response Length: {response_length} bytes")

    # Define paths for saving output files
    tests_dir = Path(__file__).resolve().parent
    json_out_path = tests_dir / "google_patents_raw_response.json"
    txt_out_path = tests_dir / "google_patents_raw_response.txt"

    # 8. Check if Google blocks or rate limits the request
    if status_code in [403, 429] or "captcha" in response.text.lower():
        print(f"\n[ERROR] Google blocked the request!")
        print(f"  - Status Code: {status_code}")
        if "captcha" in response.text.lower():
            print("  - Reason: CAPTCHA challenge detected.")
        else:
            print("  - Reason: Rate limiting or forbidden access.")
        
        # Save HTML block response to text file
        try:
            txt_out_path.write_text(response.text, encoding="utf-8")
            print(f"  - Saved block response HTML to: {txt_out_path}")
        except Exception as save_err:
            print(f"  - Failed to save block response: {save_err}")
        sys.exit(1)

    if status_code != 200:
        print(f"\n[ERROR] Unexpected response status code: {status_code}")
        try:
            txt_out_path.write_text(response.text, encoding="utf-8")
            print(f"  - Saved unexpected response body to: {txt_out_path}")
        except Exception as save_err:
            print(f"  - Failed to save response: {save_err}")
        sys.exit(1)

    # 7. Detect if response is HTML instead of JSON
    is_json = "application/json" in content_type.lower() or response.text.strip().startswith("{")
    if not is_json:
        print(f"\n[WARNING] Google returned HTML/Text instead of JSON!")
        try:
            txt_out_path.write_text(response.text, encoding="utf-8")
            print(f"  - Saved HTML response to: {txt_out_path}")
        except Exception as save_err:
            print(f"  - Failed to save HTML response: {save_err}")
        sys.exit(0)

    # 5. Extract and print JSON patent details
    try:
        data = response.json()
        
        # Save the formatted JSON response to disk
        try:
            with open(json_out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"  - Saved raw JSON response to: {json_out_path}")
        except Exception as save_err:
            print(f"  - Failed to save JSON response: {save_err}")

        # Extract total results count
        total_results = data.get("results", {}).get("total_num_results", 0)
        print(f"  - Number of Patents Found (Total): {total_results}")

        # Extract results array
        clusters = data.get("results", {}).get("cluster", [])
        patent_list = []
        if clusters and isinstance(clusters, list):
            # Take patents from the first cluster
            patent_list = clusters[0].get("result", [])

        num_extracted = len(patent_list)
        print(f"  - Extracted {num_extracted} patents from the first results cluster.")

        if num_extracted == 0:
            print("\n[WARNING] No patent elements found in the JSON payload.")
            sys.exit(0)

        # Print details for at least the first 5 patents
        print("\n" + "=" * 50)
        print("FIRST 5 PATENT DETAILS:")
        print("=" * 50)

        for i, item in enumerate(patent_list[:5]):
            patent_info = item.get("patent", {})
            title = patent_info.get("title", "N/A").strip()
            patent_number = patent_info.get("publication_number", "N/A").strip()
            assignee = patent_info.get("assignee", "N/A").strip()
            
            # Extract Year from publication_date
            pub_date = patent_info.get("publication_date", "")
            year = "N/A"
            if pub_date and isinstance(pub_date, str):
                year = pub_date.split("-")[0]

            print(f"\nPatent #{i+1}")
            print(f"  - Title: {safe_str(title)}")
            print(f"  - Patent Number: {safe_str(patent_number)}")
            print(f"  - Assignee: {safe_str(assignee)}")
            print(f"  - Publication/Filing Year: {safe_str(year)}")
            print(f"  - Source: Google Patents")

    except json.JSONDecodeError as decode_err:
        print(f"\n[ERROR] Failed to parse JSON response: {decode_err}")
        try:
            txt_out_path.write_text(response.text, encoding="utf-8")
            print(f"  - Saved malformed response to: {txt_out_path}")
        except Exception as save_err:
            print(f"  - Failed to save malformed response: {save_err}")

if __name__ == "__main__":
    test_google_patents_fetch()
