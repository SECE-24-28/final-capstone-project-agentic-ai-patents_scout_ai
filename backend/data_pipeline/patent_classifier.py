import logging
from typing import List, Dict, Any

logger = logging.getLogger("PatentClassifier")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Domain to keyword mappings for text analysis scoring
DOMAIN_KEYWORDS = {
    "Artificial Intelligence": [
        "ai", "artificial intelligence", "neural network", "machine learning", 
        "deep learning", "transformer", "natural language", "image classification", 
        "computer vision", "classifier", "reinforcement learning", "supervised learning"
    ],
    "Healthcare": [
        "healthcare", "medical", "vital signs", "telemetry", "clinical", 
        "infusion pump", "cardiovascular", "radiological", "diagnostics", 
        "treatment", "patient", "vital sign"
    ],
    "Biotechnology": [
        "biotechnology", "crispr", "gene editing", "dna sequencing", "genomic", 
        "biology", "molecular", "base calling", "guide rna", "genetics"
    ],
    "Agriculture": [
        "agriculture", "crop", "tractor", "farming", "precision irrigation", 
        "irrigation", "soil moisture", "plant", "harvesting", "agricultural", "row-crop"
    ],
    "Renewable Energy": [
        "renewable energy", "solar", "grid sync", "wind turbine", "rotor pitch", 
        "photovoltaic", "clean energy", "hydroelectric", "power grid", "blade pitch"
    ],
    "Cybersecurity": [
        "cybersecurity", "zero trust", "network threat", "threat isolation", 
        "malicious behavior", "firewall", "encryption", "security gateway", 
        "intrusion", "authentication", "cyber threat"
    ],
    "Robotics": [
        "robotics", "robotic arm", "lidar", "autonomous mobile robot", 
        "inverse kinematics", "path planning", "manipulator", "robot", "robotic"
    ],
    "Internet of Things (IoT)": [
        "internet of things", "iot", "wireless sensor", "sensor node", 
        "mesh network", "routing protocol", "sleep-wake", "mesh routing"
    ],
    "Smart Cities": [
        "smart cities", "smart city", "traffic management", "parking space", "smart parking", 
        "urban", "occupancy detector", "traffic signal", "metropolitan", "toll road", "toll lane"
    ],
    "Education Technology": [
        "education technology", "learning path", "virtual classroom", "whiteboard", 
        "pedagogy", "e-learning", "student", "curriculum", "test performance"
    ],
    "FinTech": [
        "fintech", "ledger", "blockchain", "mobile payments", "transaction gateway", 
        "credit card", "fraud detection", "financial", "banking", "cryptographic transaction"
    ],
    "Sustainability": [
        "sustainability", "biodegradable", "water recycling", "reverse osmosis", 
        "membrane pressure", "recycling", "ecofriendly", "compostable", "bioplastic", "polylactic"
    ]
}

def classify_patents(patents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Classifies patent records into one of the 12 supported domains
    using a keyword scoring strategy on title and abstract.

    Args:
        patents (List[Dict[str, Any]]): Cleaned list of patent dicts.

    Returns:
        List[Dict[str, Any]]: List of classified patent dicts with 'domain' populated.
    """
    logger.info("Starting domain classification on patents...")
    
    classified_patents: List[Dict[str, Any]] = []
    
    for patent in patents:
        title = patent.get("title", "").lower()
        abstract = patent.get("abstract", "").lower()
        text_to_analyze = f"{title} {abstract}"
        
        # Calculate scores for each domain
        scores = {}
        for domain, keywords in DOMAIN_KEYWORDS.items():
            score = 0
            for kw in keywords:
                # Add higher weight if keyword is found in title (e.g. weight 3)
                if kw in title:
                    score += 3
                # Add standard weight if found in abstract (e.g. weight 1)
                if kw in abstract:
                    score += text_to_analyze.count(kw)
            scores[domain] = score
            
        # Select domain with the maximum score
        max_score = -1
        selected_domain = "Sustainability"  # Default domain fallback
        
        for domain, score in scores.items():
            if score > max_score and score > 0:
                max_score = score
                selected_domain = domain
                
        # Update domain field
        classified_record = dict(patent)
        classified_record["domain"] = selected_domain
        classified_patents.append(classified_record)

    logger.info(f"Classification complete for {len(classified_patents)} patents.")
    return classified_patents
