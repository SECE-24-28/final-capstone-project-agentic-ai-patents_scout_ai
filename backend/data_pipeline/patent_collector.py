import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

logger = logging.getLogger("PatentCollector")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def collect_patents(source_dir: str = "data/raw_patents") -> List[Dict[str, Any]]:
    """
    Loads raw patents from real dataset source (CSV or JSON).
    Validates required columns exist.
    If no source file is found, raises FileNotFoundError.

    Args:
        source_dir (str): Directory where raw patents are stored.

    Returns:
        List[Dict[str, Any]]: Normalized list of patent dictionaries.
    """
    logger.info("Initializing Patent Collector...")
    dir_path = Path(source_dir)
    
    csv_path = dir_path / "raw_patents.csv"
    json_path = dir_path / "raw_patents.json"
    
    # Check if either file exists
    if not csv_path.exists() and not json_path.exists():
        logger.error(f"No raw patent source file found in {source_dir}. Expected raw_patents.csv or raw_patents.json.")
        raise FileNotFoundError(f"Real patent dataset source file not found in '{source_dir}'. Stop execution immediately.")

    df = None
    if csv_path.exists():
        logger.info(f"Loading raw patents from CSV: {csv_path}")
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            logger.error(f"Failed to read CSV file: {e}")
            raise
    elif json_path.exists():
        logger.info(f"Loading raw patents from JSON: {json_path}")
        try:
            df = pd.read_json(json_path)
        except Exception as e:
            logger.error(f"Failed to read JSON file: {e}")
            raise

    if df is None or df.empty:
        logger.warning("Loaded dataset is empty.")
        return []

    # Validate required fields
    required_fields = ["patent_number", "title", "abstract", "assignee", "year"]
    for field in required_fields:
        if field not in df.columns:
            logger.error(f"Required field '{field}' is missing from raw dataset columns: {list(df.columns)}")
            raise KeyError(f"Missing required field '{field}' in dataset.")

    # Normalize records: replace NaN/NaT/Null with None, convert to dict list
    raw_patents = []
    for record in df.to_dict(orient="records"):
        normalized = {}
        for k, v in record.items():
            if pd.isna(v):
                normalized[k] = None
            else:
                normalized[k] = v
        raw_patents.append(normalized)
    logger.info(f"Successfully loaded and normalized {len(raw_patents)} raw patent records.")
    return raw_patents
