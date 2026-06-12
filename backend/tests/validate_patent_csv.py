import os
import sys
import argparse
import pandas as pd

def validate_patent_csv(file_path: str) -> bool:
    """
    Validates the exported Google Patents BigQuery CSV file for compatibility
    with PatentScout AI's pipeline.
    """
    print("=" * 60)
    print(f"AUDITING & VALIDATING PATENT DATASET: {file_path}")
    print("=" * 60)

    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return False

    try:
        # Load CSV using pandas
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"[ERROR] Failed to read CSV file: {e}")
        return False

    total_records = len(df)
    print(f"Total records loaded: {total_records}")

    if total_records == 0:
        print("[ERROR] The dataset is empty.")
        return False

    # 1. Verify required columns exist
    required_columns = ["patent_number", "title", "abstract", "assignee", "year", "domain"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"[ERROR] Missing required columns: {missing_columns}")
        return False
    print("[SUCCESS] All required columns exist.")

    # 2. Check for nulls/empty values in core fields
    null_patents = df["patent_number"].isna().sum()
    null_titles = df["title"].isna().sum()
    null_abstracts = df["abstract"].isna().sum()

    if null_patents > 0:
        print(f"[ERROR] Found {null_patents} records with missing patent_number.")
        return False
    if null_titles > 0:
        print(f"[ERROR] Found {null_titles} records with missing title.")
        return False
    if null_abstracts > 0:
        print(f"[ERROR] Found {null_abstracts} records with missing abstract.")
        return False
    print("[SUCCESS] No missing titles, abstracts, or patent numbers found.")

    # 3. Check quality thresholds
    short_titles_count = (df["title"].astype(str).str.strip().str.len() < 10).sum()
    short_abstracts_count = (df["abstract"].astype(str).str.strip().str.len() < 50).sum()

    if short_titles_count > 0:
        print(f"[ERROR] Found {short_titles_count} records with title length < 10 characters.")
        return False
    if short_abstracts_count > 0:
        print(f"[ERROR] Found {short_abstracts_count} records with abstract length < 50 characters.")
        return False
    print("[SUCCESS] All records meet title (>=10) and abstract (>=50) quality thresholds.")

    # 4. Check for duplicates
    duplicates_count = df.duplicated(subset=["patent_number"]).sum()
    if duplicates_count > 0:
        print(f"[WARNING] Found {duplicates_count} duplicate patent numbers in dataset.")
    else:
        print("[SUCCESS] No duplicate patent numbers found.")

    # 5. Print Dataset Statistics
    avg_title_len = df["title"].astype(str).str.len().mean()
    avg_abstract_len = df["abstract"].astype(str).str.len().mean()
    unique_assignees = df["assignee"].nunique()
    top_assignees = df["assignee"].value_counts().head(5).to_dict()
    years_distribution = df["year"].value_counts().sort_index().to_dict()
    domains = df["domain"].value_counts().to_dict()

    print("-" * 60)
    print("DATASET METRICS & STATISTICS")
    print("-" * 60)
    print(f"Average Title Length:    {avg_title_len:.1f} characters")
    print(f"Average Abstract Length: {avg_abstract_len:.1f} characters")
    print(f"Unique Assignees Count:  {unique_assignees}")
    print("\nTop 5 Assignees in Sample:")
    for assignee, count in top_assignees.items():
        print(f"  - {assignee}: {count} patents")
    print("\nPublication Years Distribution:")
    for yr, count in years_distribution.items():
        print(f"  - {yr}: {count} patents")
    print("\nTechnology Domains:")
    for dom, count in domains.items():
        print(f"  - {dom}: {count} patents")
    print("=" * 60)
    print("[SUCCESS] Dataset validation completed successfully! Ready for ingestion.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate patent CSV files for PatentScout AI.")
    parser.add_argument(
        "--file", 
        type=str, 
        default="data/raw_patents/raw_patents.csv",
        help="Path to the patent CSV file to validate."
    )
    args = parser.parse_args()
    success = validate_patent_csv(args.file)
    sys.exit(0 if success else 1)
