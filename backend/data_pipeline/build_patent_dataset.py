import os
import json
import logging
from pathlib import Path
from typing import Dict, Any
import pandas as pd

from backend.data_pipeline.patent_collector import collect_patents
from backend.data_pipeline.patent_cleaner import clean_patents
from backend.data_pipeline.patent_classifier import classify_patents
from backend.data_pipeline.patent_balancer import balance_patents

# Configure structured logging
logger = logging.getLogger("BuildPatentDataset")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def run_build_pipeline(source_dir: str = "data/raw_patents", output_dir: str = "data/processed_patents") -> Dict[str, Any]:
    """
    Orchestrates the real patent dataset ingestion and classification pipeline:
    1. Loads raw patents from data/raw_patents/
    2. Cleans, filters, and deduplicates records
    3. Classifies records into one of the 12 domains
    4. Balances domains without oversampling
    5. Saves outputs to processed_patents
    6. Generates and saves a metrics report

    Returns:
        Dict[str, Any]: The pipeline report metrics.
    """
    logger.info("Initializing Patent Dataset Build Pipeline...")
    
    # Ensure directories exist
    Path(source_dir).mkdir(parents=True, exist_ok=True)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Step 1: Collect / Load raw dataset
    try:
        raw_patents = collect_patents(source_dir)
    except FileNotFoundError as fnf_err:
        logger.error(f"Ingestion failed: {fnf_err}")
        raise

    # Step 2: Clean patents (deduplicate, validation)
    cleaned_patents, clean_stats = clean_patents(raw_patents)

    # Step 3: Classify domains
    classified_patents = classify_patents(cleaned_patents)

    # Step 4: Balance domains (downsample only, no oversampling)
    balanced_patents = balance_patents(classified_patents, target_size_per_domain=1000)

    # Step 5: Save outputs
    logger.info("Saving balanced dataset outputs...")
    df_balanced = pd.DataFrame(balanced_patents)
    
    csv_output_path = Path(output_dir) / "patents_balanced.csv"
    json_output_path = Path(output_dir) / "patents_balanced.json"
    report_output_path = Path(output_dir) / "dataset_report.json"
    
    # Save CSV
    df_balanced.to_csv(csv_output_path, index=False, encoding="utf-8")
    logger.info(f"Saved balanced CSV dataset to: {csv_output_path}")
    
    # Save JSON
    df_balanced.to_json(json_output_path, orient="records", indent=2, force_ascii=False)
    logger.info(f"Saved balanced JSON dataset to: {json_output_path}")

    # Step 6: Generate and save report metrics
    # Group and count patents per domain
    domain_counts = df_balanced["domain"].value_counts().to_dict()
    
    # Compile the final report metrics
    report = {
        "total_raw_records": clean_stats["total_raw_records"],
        "total_clean_records": clean_stats["total_clean_records"],
        "duplicates_removed": clean_stats["duplicates_removed"],
        "missing_titles_removed": clean_stats["missing_titles_removed"],
        "missing_abstracts_removed": clean_stats["missing_abstracts_removed"],
        "malformed_records_removed": clean_stats["malformed_records_removed"],
        "patents_per_domain": domain_counts,
        "final_dataset_size": len(balanced_patents)
    }

    with open(report_output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved dataset pipeline report to: {report_output_path}")
    
    print("\n" + "=" * 60)
    print("PATENT PIPELINE RUN SUMMARY")
    print("=" * 60)
    print(f"Total Raw Records Loaded: {report['total_raw_records']}")
    print(f"Clean Records after Filters: {report['total_clean_records']}")
    print(f"Duplicates Removed: {report['duplicates_removed']}")
    print(f"Final Balanced Dataset Size: {report['final_dataset_size']}")
    print("\nPatents Per Domain:")
    for dom, count in report["patents_per_domain"].items():
        print(f"  - {dom}: {count} patents")
    print("=" * 60 + "\n")

    return report

if __name__ == "__main__":
    run_build_pipeline()
