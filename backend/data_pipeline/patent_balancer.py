import logging
from typing import List, Dict, Any
import pandas as pd

logger = logging.getLogger("PatentBalancer")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def balance_patents(patents: List[Dict[str, Any]], target_size_per_domain: int = 1000) -> List[Dict[str, Any]]:
    """
    Balances the dataset across domains.
    Downsamples any domain that has more than target_size_per_domain patents.
    Does NOT oversample, duplicate, or generate fake records if a domain is short.

    Args:
        patents (List[Dict[str, Any]]): List of classified patent dicts.
        target_size_per_domain (int): Target maximum size per domain. Defaults to 1000.

    Returns:
        List[Dict[str, Any]]: List of balanced patent records.
    """
    logger.info(f"Balancing dataset with target size per domain <= {target_size_per_domain}...")
    
    if not patents:
        return []

    # Convert to DataFrame for easy grouping and sampling
    df = pd.DataFrame(patents)
    
    balanced_dfs = []
    
    # Group by domain and apply balancing rules
    for domain, group in df.groupby("domain"):
        current_size = len(group)
        logger.info(f"Domain '{domain}' has {current_size} valid patents.")
        
        if current_size > target_size_per_domain:
            # Downsample using random state to ensure reproducibility
            sampled_group = group.sample(n=target_size_per_domain, random_state=42)
            logger.info(f"  - Downsampled '{domain}' from {current_size} to {target_size_per_domain}")
            balanced_dfs.append(sampled_group)
        else:
            # Keep all available records (do NOT oversample or create synthetic data)
            logger.info(f"  - Keeping all {current_size} patents for '{domain}' (no oversampling applied)")
            balanced_dfs.append(group)
            
    if not balanced_dfs:
        return []
        
    balanced_df = pd.concat(balanced_dfs, ignore_index=True)
    balanced_records = balanced_df.to_dict(orient="records")
    
    logger.info(f"Balancing complete. Total dataset size: {len(balanced_records)} patents.")
    return balanced_records
