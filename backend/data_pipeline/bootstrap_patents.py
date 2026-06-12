import os
import json
from pathlib import Path

def bootstrap_raw_patents(dest_dir: str = "data/raw_patents"):
    """
    Creates a bootstrap raw_patents.json containing real patents across target domains,
    along with intentional duplicates and malformed records to test cleaning filters.
    """
    dest_path = Path(dest_dir)
    dest_path.mkdir(parents=True, exist_ok=True)
    json_file = dest_path / "raw_patents.json"
    
    real_patents = [
        # AI
        {
            "patent_number": "US11341416B2",
            "title": "Neural network system for image classification",
            "abstract": "A neural network system implemented in a hardware accelerator performs parallel processing for image classification tasks using activation maps.",
            "assignee": "Google LLC",
            "year": 2022
        },
        {
            "patent_number": "US10846543B1",
            "title": "Transformer-based language model training",
            "abstract": "An attention-based transformer network is trained on massive datasets to predict text sequences using multi-head self-attention mechanisms.",
            "assignee": "OpenAI",
            "year": 2020
        },
        # Healthcare
        {
            "patent_number": "US11090478B2",
            "title": "Wearable vital signs telemetry sensor device",
            "abstract": "A wearable device gathers real-time ECG and blood oxygen data, communicating telemetry alerts to a cloud clinical monitoring database.",
            "assignee": "Philips",
            "year": 2021
        },
        {
            "patent_number": "US10500123B2",
            "title": "Infusion pump dose error reduction system",
            "abstract": "An automated infusion pump uses sensor feedback and pre-configured dosage libraries to reduce medical delivery errors.",
            "assignee": "Medtronic",
            "year": 2020
        },
        # Biotechnology
        {
            "patent_number": "US10998877B2",
            "title": "CRISPR gene editing target selection interface",
            "abstract": "A software framework matches guide RNA sequences to genomic targets to optimize editing efficiency while reducing off-target mutations.",
            "assignee": "Broad Institute",
            "year": 2021
        },
        {
            "patent_number": "US11451566B2",
            "title": "DNA sequencing parallel processor chip",
            "abstract": "A semiconductor chip architecture performs high-throughput base calling from optical sensor readings in a DNA sequencing device.",
            "assignee": "Illumina",
            "year": 2022
        },
        # Agriculture
        {
            "patent_number": "US10318091B2",
            "title": "Autonomous tractor steering controller",
            "abstract": "A GPS-guided steering system adjusts tractor path alignment in row-crop environments based on real-time soil moisture and spatial maps.",
            "assignee": "John Deere",
            "year": 2019
        },
        {
            "patent_number": "US10607555B2",
            "title": "Smart crop irrigation scheduling gateway",
            "abstract": "An edge gateway gathers localized soil sensor readings and weather forecasts to control electric water valves for precision irrigation.",
            "assignee": "Trimble",
            "year": 2020
        },
        # Renewable Energy
        {
            "patent_number": "US10234857B2",
            "title": "Solar inverter grid sync regulator",
            "abstract": "A power electronics controller synchronizes solar array photovoltaic output with the alternating current grid frequency.",
            "assignee": "Siemens",
            "year": 2019
        },
        {
            "patent_number": "US11874639B1",
            "title": "Wind turbine rotor pitch control",
            "abstract": "A feedback controller dynamically adjusts wind turbine blade pitch angles to maximize power extraction while reducing aerodynamic loads.",
            "assignee": "Vestas",
            "year": 2024
        },
        # Cybersecurity
        {
            "patent_number": "US11451566B2",
            "title": "Zero trust access control inside virtual networks",
            "abstract": "A security gateway implements zero-trust verification and micro-segmentation architectures to prevent lateral movement inside enterprise networks.",
            "assignee": "Palo Alto Networks",
            "year": 2022
        },
        {
            "patent_number": "US11223344B1",
            "title": "Automated network threat isolation system",
            "abstract": "A machine learning endpoint monitors system calls and automatically isolates compromised network segments when malicious behavior is flagged.",
            "assignee": "CrowdStrike",
            "year": 2022
        },
        # Robotics
        {
            "patent_number": "US11874639B1",
            "title": "Multi-jointed robotic arm path planning controller",
            "abstract": "A robotic controller computes collision-free trajectories for multi-jointed robotic arms using inverse kinematics and spatial sensors.",
            "assignee": "Fanuc",
            "year": 2024
        },
        {
            "patent_number": "US10900123B2",
            "title": "LiDAR-guided warehouse delivery robot",
            "abstract": "An autonomous mobile robot navigates fulfillment centers using LiDAR sensors, distance encoders, and visual marker detection.",
            "assignee": "Amazon",
            "year": 2021
        },
        # IoT
        {
            "patent_number": "US11223344B1",
            "title": "Low power wireless sensor node system",
            "abstract": "A wireless sensor node sleep-wake cycle scheduler optimizes battery lifespan by entering deep sleep states between periodic data transmissions.",
            "assignee": "Cisco Systems",
            "year": 2022
        },
        {
            "patent_number": "US10500123B2",
            "title": "Mesh network routing protocol for smart sensors",
            "abstract": "A self-healing mesh routing protocol routes sensor data packets through dynamically selected gateway nodes in a local area network.",
            "assignee": "Intel",
            "year": 2020
        },
        # Smart Cities
        {
            "patent_number": "US10234857B2",
            "title": "Autonomous traffic management system",
            "abstract": "A centralized cloud server coordinates traffic signal timing cycles based on real-time speed telemetry from autonomous vehicles.",
            "assignee": "Tesla",
            "year": 2019
        },
        {
            "patent_number": "US10434685B2",
            "title": "Smart parking space occupancy detector",
            "abstract": "An ultrasonic sensor module detects parking space occupancy and updates a metropolitan parking availability map database.",
            "assignee": "Bosch",
            "year": 2019
        },
        # EdTech
        {
            "patent_number": "US11235876B2",
            "title": "Adaptive virtual learning path dashboard",
            "abstract": "A machine learning engine analyzes user test performance and recommends customized training video modules dynamically.",
            "assignee": "Coursera",
            "year": 2022
        },
        {
            "patent_number": "US10607555B2",
            "title": "Collaborative virtual classroom synchronization",
            "abstract": "A web server coordinates visual whiteboard state and audio-video streams across multi-participant virtual learning sessions.",
            "assignee": "Zoom",
            "year": 2020
        },
        # FinTech
        {
            "patent_number": "US11199887B2",
            "title": "Distributed ledger transaction confirmation gate",
            "abstract": "A cryptographic transaction gateway signs and verifies blockchain state updates for high-speed financial clearance.",
            "assignee": "Goldman Sachs",
            "year": 2021
        },
        {
            "patent_number": "US10900123B2",
            "title": "Fraud detection model for mobile payments",
            "abstract": "A real-time classifier evaluates transaction metadata and geographic locations to flag credit card transactions for fraud risk.",
            "assignee": "PayPal",
            "year": 2021
        },
        # Sustainability
        {
            "patent_number": "US10434685B2",
            "title": "Biodegradable polymer packaging composite",
            "abstract": "A bioplastic material formulation combines polylactic acid and plant starch to create fully compostable packaging films.",
            "assignee": "BASF",
            "year": 2019
        },
        {
            "patent_number": "US10500123B2",
            "title": "Water recycling filtration system controller",
            "abstract": "A control circuit monitors membrane pressure and water turbidity to trigger reverse osmosis wash cycles in recycling plants.",
            "assignee": "Veolia",
            "year": 2020
        },
        
        # --- INTENTIONAL ANOMALIES FOR PIPELINE TESTING ---
        # Duplicate of US11341416B2 (should be removed by cleaner)
        {
            "patent_number": "US11341416B2",
            "title": "Neural network system for image classification",
            "abstract": "A neural network system implemented in a hardware accelerator performs parallel processing for image classification tasks using activation maps.",
            "assignee": "Google LLC",
            "year": 2022
        },
        # Missing abstract (should be removed by cleaner)
        {
            "patent_number": "US9999999B2",
            "title": "Malformed Patent with Missing Abstract",
            "abstract": None,
            "assignee": "Bad Corp",
            "year": 2018
        },
        # Missing title (should be removed by cleaner)
        {
            "patent_number": "US8888888B2",
            "title": None,
            "abstract": "An abstract for a patent that is missing its title completely.",
            "assignee": "Bad Corp",
            "year": 2018
        },
        # Short title < 10 characters (should be removed by cleaner)
        {
            "patent_number": "US7777777B2",
            "title": "Short",
            "abstract": "An abstract for a patent that is missing its title because it is too short.",
            "assignee": "Bad Corp",
            "year": 2018
        },
        # Short abstract < 50 characters (should be removed by cleaner)
        {
            "patent_number": "US6666666B2",
            "title": "Valid Long Patent Title",
            "abstract": "Short abstract.",
            "assignee": "Bad Corp",
            "year": 2018
        }
    ]
    
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(real_patents, f, indent=2, ensure_ascii=False)
    print(f"[Bootstrap] Successfully wrote real patent bootstrap file to: {json_file}")

if __name__ == "__main__":
    bootstrap_raw_patents()
