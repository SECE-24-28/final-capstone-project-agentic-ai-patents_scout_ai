import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import settings

def generate_response(prompt: str) -> str:
    """
    Call Gemini 2.5 Flash model with the given prompt.
    Returns the raw string output.
    """
    print("[LLM Client] Sending request to Gemini 1.5 Flash...")
    
    # Check if key is available
    api_key = settings.GOOGLE_API_KEY
    if not api_key:
        print("[LLM Client] Warning: GOOGLE_API_KEY is not configured in .env. Using mock JSON fallback...")
        return get_fallback_json(prompt)
        
    try:
        # Initialize LangChain Google GenAI client
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.1
        )
        
        # Call model
        response = llm.invoke(prompt)
        raw_text = response.content
        if isinstance(raw_text, bytes):
            raw_text = raw_text.decode("utf-8")
        return raw_text.strip()
    except Exception as e:
        print(f"[LLM Client] Gemini API call failed: {e}. Using fallback generator...")
        return get_fallback_json(prompt)

def get_fallback_json(prompt: str) -> str:
    """
    Generates realistic looking mock JSON arrays matching expected agent schemas 
    if the API is unavailable, tailored to the domain keyword.
    """
    prompt_lower = prompt.lower()
    
    # Extract domain query from the prompt for context-specific matching
    domain_query = ""
    if "target domain:" in prompt_lower:
        try:
            part = prompt_lower.split("target domain:", 1)[1]
            domain_query = part.split("\n", 1)[0].strip()
        except Exception:
            pass
    elif "about " in prompt_lower:
        try:
            part = prompt_lower.split("about ", 1)[1]
            domain_query = part.split(",", 1)[0].strip()
        except Exception:
            pass
    elif "domain: " in prompt_lower:
        try:
            part = prompt_lower.split("domain: ", 1)[1]
            domain_query = part.split("\n", 1)[0].strip()
        except Exception:
            pass
            
    match_target = domain_query if domain_query else prompt_lower

    # 0. Check FIRST if the prompt is for the Innovation Agent
    #    (must be before patent-cluster check since innovation prompt contains 'saturation')
    if ("innovation concepts" in prompt_lower or "novelty_score" in prompt_lower
            or "potential_benefits" in prompt_lower
            or "core_technology" in prompt_lower or "target_market" in prompt_lower):
        if "vehicle" in match_target or "battery" in match_target or "charging" in match_target:
            mock_ideas = [
                {
                    "title": "AI-Based Battery Health Prognostics Engine",
                    "description": "An onboard diagnostics platform that leverages physics-informed machine learning to predict lithium-ion battery capacity fade and dendrite formation in real-time, enabling adaptive charging regulation that significantly extends pack lifespan.",
                    "core_technology": "Physics-informed neural networks (PINNs), electrochemical impedance spectroscopy analysis, and low-power microcontroller edge deployment.",
                    "target_market": "Electric vehicle manufacturers, battery pack integrators, and commercial fleet operators.",
                    "potential_benefits": [
                        "Increases battery pack lifespan by up to 25% through adaptive charging regulation",
                        "Provides accurate state-of-health diagnostics down to individual cell levels",
                        "Early detection of thermal runaway hazards before they manifest physically"
                    ],
                    "novelty_score": 90,
                    "market_potential": "High"
                },
                {
                    "title": "Offline Bidirectional Charging Orchestration Platform",
                    "description": "A vehicle-to-grid (V2G) management system that operates using only local communication to coordinate bidirectional energy flows between EV fleets and residential microgrids without relying on central cloud infrastructure.",
                    "core_technology": "Edge-deployed reinforcement learning scheduler, IEEE 2030.5 protocol stack, and fault-tolerant peer-to-peer mesh communication.",
                    "target_market": "Residential microgrid operators, commercial EV fleet managers, and utility companies piloting demand response.",
                    "potential_benefits": [
                        "Eliminates latency from cloud-based orchestration, enabling real-time demand response",
                        "Avoids reliance on central server infrastructure, reducing single points of failure",
                        "Minimal existing patent coverage in decentralized V2G mesh coordination"
                    ],
                    "novelty_score": 85,
                    "market_potential": "High"
                }
            ]
        elif "cybersecurity" in match_target or "security" in match_target:
            mock_ideas = [
                {
                    "title": "Quantum-Resistant Identity Verification Gateway",
                    "description": "A post-quantum biometric authentication gateway that performs lattice-based cryptographic verification on local user hardware to prevent identity theft in zero-trust environments without any cloud dependency.",
                    "core_technology": "Lattice-based cryptography (Kyber/Dilithium), homomorphic signature verification, and secure hardware enclave isolation.",
                    "target_market": "Financial institutions, critical infrastructure providers, and government security agencies.",
                    "potential_benefits": [
                        "Protects identity signatures against future quantum decryption attacks",
                        "Maintains zero-trust security posture on untrusted edge devices",
                        "Minimal latency compared to cloud-based post-quantum cryptographic schemes"
                    ],
                    "novelty_score": 95,
                    "market_potential": "High"
                }
            ]
        elif "renewable" in match_target or "solar" in match_target or "energy" in match_target:
            mock_ideas = [
                {
                    "title": "Solid-State Solar Pack Lifetime Optimizer",
                    "description": "An edge-deployed optimization engine for solid-state solar storage arrays that continuously monitors electrolyte interface integrity and adapts charge-discharge cycles to maximize cycle lifetime beyond current liquid-electrolyte limitations.",
                    "core_technology": "Electrochemical degradation modeling, solid-state interface simulation, and on-device anomaly detection neural networks.",
                    "target_market": "Residential solar installers, off-grid energy storage vendors, and utility-scale battery integrators.",
                    "potential_benefits": [
                        "Extends solid-state pack lifetime by 30%+ through precision cycle management",
                        "Enables reliable off-grid power for remote or disaster-resilient infrastructure",
                        "Very low patent saturation in the solid-state pack optimization area"
                    ],
                    "novelty_score": 90,
                    "market_potential": "High"
                }
            ]
        elif "healthcare" in match_target or "medical" in match_target:
            mock_ideas = [
                {
                    "title": "Federated Genomic Drug Dosage Personalization Engine",
                    "description": "A privacy-preserving federated learning platform that trains personalized cancer drug dosage models across hospital networks without sharing raw patient genomic data, enabling precision oncology at scale.",
                    "core_technology": "Federated learning with differential privacy, genomic sequence alignment models, and FHIR-compliant secure data exchange.",
                    "target_market": "Oncology hospital networks, precision medicine startups, and pharmaceutical research organizations.",
                    "potential_benefits": [
                        "Enables precision dosage without exposing sensitive genomic data across institutions",
                        "Significantly improves drug response outcomes in complex cancer treatments",
                        "Near-zero patent coverage in federated genomic-based dosage optimization"
                    ],
                    "novelty_score": 91,
                    "market_potential": "High"
                }
            ]
        elif "city" in match_target or "cities" in match_target or "urban" in match_target:
            mock_ideas = [
                {
                    "title": "Decentralized Urban Privacy Telemetry Mesh",
                    "description": "A city-scale distributed sensor mesh that collects and anonymizes municipal telemetry data using local differential privacy computation, eliminating centralized data collection vulnerabilities.",
                    "core_technology": "Differential privacy algorithms, local federated aggregation, LoRaWAN IoT mesh protocols, and distributed consensus ledgers.",
                    "target_market": "Smart city administrations, municipal infrastructure vendors, and civil liberties-focused technology integrators.",
                    "potential_benefits": [
                        "Protects citizen privacy by design without relying on data anonymization at a central server",
                        "Reduces attack surface of city sensor networks by eliminating central aggregation points",
                        "Near-zero existing patent coverage in decentralized municipal differential privacy"
                    ],
                    "novelty_score": 94,
                    "market_potential": "High"
                }
            ]
        elif any(kw in match_target for kw in ["ai", "machine learning", "intelligence"]):
            mock_ideas = [
                {
                    "title": "Federated Multi-Agent Memory Consensus Platform",
                    "description": "A privacy-preserving state synchronization infrastructure that enables multiple LLM agents in a distributed organization to share learned memory embeddings without centralizing sensitive reasoning traces.",
                    "core_technology": "Federated learning, encrypted memory embedding storage, zero-knowledge proof verification of model updates, and multi-party computation.",
                    "target_market": "Enterprise AI labs, regulated industries deploying multi-agent systems, and government AI programs.",
                    "potential_benefits": [
                        "Enables multi-agent collaboration without sharing sensitive reasoning or data traces",
                        "No existing patent coverage in federated LLM state consensus mechanisms",
                        "Reduces hallucination rates by sharing grounded memory embeddings across agents"
                    ],
                    "novelty_score": 92,
                    "market_potential": "High"
                }
            ]
        else:
            # Default smart agriculture
            mock_ideas = [
                {
                    "title": "Edge-Native Plant Pathogen Classifier",
                    "description": "A mobile offline computer vision diagnostic tool that runs lightweight autoencoders directly on low-power agricultural sensors to identify crop leaf diseases instantly without cloud connectivity.",
                    "core_technology": "Mobile-optimized convolutional neural network, quantization-aware training, local disease database, microclimate sensor telemetry.",
                    "target_market": "Smallholder farmers, organic cooperatives, agritech sensor vendors, and remote agricultural research centers.",
                    "potential_benefits": [
                        "No cellular or internet connection required — ideal for remote areas",
                        "Extremely low power consumption enables continuous monitoring",
                        "Immediate detection reduces crop loss and chemical use"
                    ],
                    "novelty_score": 88,
                    "market_potential": "High"
                }
            ]
        return json.dumps(mock_ideas)

    # 1. Check if the prompt is for the Research Agent
    if ("research topics" in prompt_lower or "research_topics" in prompt_lower or "abstracts" in prompt_lower) and "patent" not in prompt_lower:
        # Check domain context
        if "healthcare" in match_target or "medical" in match_target or "diagnostic" in match_target:
            mock_topics = [
                {
                    "topic": "AI-Assisted Diagnostics",
                    "description": "Deep learning models classifying diseases from radiology scans and MRI images.",
                    "research_activity": "High",
                    "citation_strength": 95
                },
                {
                    "topic": "Wearable Health Sensors",
                    "description": "Continuous telemetry of vital signs for cardiovascular tracking and early anomaly warning.",
                    "research_activity": "High",
                    "citation_strength": 88
                },
                {
                    "topic": "Remote Patient Telemedicine",
                    "description": "Virtual care interfaces managing patient workflows and secure clinical data sharing.",
                    "research_activity": "Medium",
                    "citation_strength": 70
                },
                {
                    "topic": "Personalized Genomic Medicine",
                    "description": "Tailoring oncology drug dosages based on specific gene sequencing biomarkers.",
                    "research_activity": "Low",
                    "citation_strength": 35
                }
            ]
        elif "vehicle" in match_target or "battery" in match_target or "charging" in match_target:
            mock_topics = [
                {
                    "topic": "Battery Health Prediction",
                    "description": "Predicting lithium-ion state of health using capacity fading tracking models.",
                    "research_activity": "High",
                    "citation_strength": 90
                },
                {
                    "topic": "Solid-State Battery Tech",
                    "description": "Solid electrolyte materials replacing liquid counterparts for high safety EV blocks.",
                    "research_activity": "High",
                    "citation_strength": 86
                },
                {
                    "topic": "Ultra-Fast Charging Station",
                    "description": "High-power cooling and charger grids delivering rapid charge times without cell damage.",
                    "research_activity": "Medium",
                    "citation_strength": 68
                }
            ]
        elif any(kw in match_target for kw in ["cybersecurity", "security", "cryptography", "firewall", "malware", "network"]):
            mock_topics = [
                {
                    "topic": "Zero Trust Network Access",
                    "description": "Continuous verification and micro-segmentation architectures to prevent lateral movement inside enterprise networks.",
                    "research_activity": "High",
                    "citation_strength": 92
                },
                {
                    "topic": "Homomorphic Encryption",
                    "description": "Cryptographic schemes allowing computation on encrypted datasets without revealing underlying plaintexts.",
                    "research_activity": "High",
                    "citation_strength": 87
                },
                {
                    "topic": "AI-Driven Threat Detection",
                    "description": "Anomalous behavior monitoring using neural networks to block real-time cyber threats and zero-day exploits.",
                    "research_activity": "High",
                    "citation_strength": 94
                },
                {
                    "topic": "Automated Software Vulnerability Scanning",
                    "description": "Static and dynamic program analysis to autonomously patch flaws in software supply chains.",
                    "research_activity": "Medium",
                    "citation_strength": 72
                }
            ]
        elif any(kw in match_target for kw in ["ai", "machine learning", "deep learning", "neural", "intelligence", "language model"]):
            mock_topics = [
                {
                    "topic": "Large Language Model Reasoning",
                    "description": "Techniques to improve multi-step planning and logical execution paths in transformer architectures.",
                    "research_activity": "High",
                    "citation_strength": 96
                },
                {
                    "topic": "AI Agent Orchestration",
                    "description": "Multi-agent frameworks managing state, memory systems, and tools to solve complex objectives.",
                    "research_activity": "High",
                    "citation_strength": 93
                },
                {
                    "topic": "Efficient Model Distillation",
                    "description": "Compressing parameter counts of foundation models into fast edge runtimes without quality degradation.",
                    "research_activity": "High",
                    "citation_strength": 88
                },
                {
                    "topic": "Explainable Deep Learning",
                    "description": "Visualizing activation pathways and feature attribution methods inside deep neural nets.",
                    "research_activity": "Medium",
                    "citation_strength": 70
                }
            ]
        elif "city" in match_target or "cities" in match_target or "urban" in match_target:
            mock_topics = [
                {
                    "topic": "Urban IoT Infrastructure",
                    "description": "Architectures and communication protocols for deploying high-density sensor networks across municipal areas.",
                    "research_activity": "High",
                    "citation_strength": 92
                },
                {
                    "topic": "Dynamic Traffic Routing",
                    "description": "Reinforcement learning algorithms for adaptive traffic signal control and emergency vehicle routing.",
                    "research_activity": "High",
                    "citation_strength": 88
                },
                {
                    "topic": "Data Privacy in Smart Spaces",
                    "description": "Privacy-preserving frameworks for handling crowdsourced municipal and citizen telemetry data.",
                    "research_activity": "Medium",
                    "citation_strength": 75
                }
            ]
        else:
            # Default to Smart Agriculture
            mock_topics = [
                {
                    "topic": "Crop Disease Detection",
                    "description": "Computer vision models trained on leaf imagery to classify fungal and viral infections.",
                    "research_activity": "High",
                    "citation_strength": 92
                },
                {
                    "topic": "Precision Irrigation Controllers",
                    "description": "Sensors and reinforcement learning systems adjusting flow rate based on real-time soil moisture.",
                    "research_activity": "High",
                    "citation_strength": 85
                },
                {
                    "topic": "Microclimate Weather Forecasting",
                    "description": "Localized weather predicting models using edge nodes placed in individual field blocks.",
                    "research_activity": "Medium",
                    "citation_strength": 64
                },
                {
                    "topic": "Drone-Based Autonomous Monitoring",
                    "description": "Unmanned aerial vehicles flying scheduled paths to capture multispectral crop health grids.",
                    "research_activity": "Low",
                    "citation_strength": 40
                }
            ]
        return json.dumps(mock_topics)
    elif "patent clusters" in prompt_lower or "patent_clusters" in prompt_lower or "patent_saturation" in prompt_lower or "patent count" in prompt_lower or "saturation" in prompt_lower:
        # Check domain context
        if "healthcare" in match_target or "medical" in match_target or "diagnostic" in match_target:
            mock_clusters = [
                {
                    "category": "Wearable Vital Sensors",
                    "description": "Patented hardware for continuous telemetry of ECG and blood oxygen metrics.",
                    "saturation": "High",
                    "major_assignees": ["Medtronic", "Philips", "Apple"]
                },
                {
                    "category": "AI Diagnostics Systems",
                    "description": "Patents covering neural networks for computerized diagnostic scoring and anomaly alerts.",
                    "saturation": "High",
                    "major_assignees": ["Google Health", "IBM Watson", "Siemens Healthineers"]
                },
                {
                    "category": "Telemedicine Data Platforms",
                    "description": "Secure clinical teleconferencing and encrypted medical record database systems.",
                    "saturation": "Medium",
                    "major_assignees": ["Teladoc", "Amwell", "Epic Systems"]
                }
            ]
        elif "vehicle" in match_target or "battery" in match_target or "charging" in match_target:
            mock_clusters = [
                {
                    "category": "Battery Cell Configuration",
                    "description": "Patented modular cell configurations and internal link setups for EV battery pack efficiency.",
                    "saturation": "High",
                    "major_assignees": ["Tesla", "Panasonic", "CATL"]
                },
                {
                    "category": "Thermal Regulation Grids",
                    "description": "Patents covering pack-level cooling channels and heat sink setups for temperature safety.",
                    "saturation": "High",
                    "major_assignees": ["Tesla", "LG Energy Solution", "BYD"]
                },
                {
                    "category": "Fast Charging Circuits",
                    "description": "High-amperage charging interfaces and power regulation circuitry to protect active cells.",
                    "saturation": "Medium",
                    "major_assignees": ["ChargePoint", "ABB", "Siemens"]
                }
            ]
        elif any(kw in match_target for kw in ["cybersecurity", "security", "cryptography", "firewall", "malware", "network"]):
            mock_clusters = [
                {
                    "category": "Network Security Gateways",
                    "description": "Patented firewall filtering devices and hardware security appliances for enterprise routing.",
                    "saturation": "High",
                    "major_assignees": ["Cisco Systems", "Palo Alto Networks", "Fortinet"]
                },
                {
                    "category": "Encrypted Communication Protocols",
                    "description": "Cryptographic authentication patents protecting data transfers across distributed systems.",
                    "saturation": "High",
                    "major_assignees": ["RSA Security", "Symantec", "Microsoft"]
                },
                {
                    "category": "Automated Threat Isolation",
                    "description": "Intrusion detection software systems automatically isolating compromised virtual domains.",
                    "saturation": "Medium",
                    "major_assignees": ["CrowdStrike", "FireEye", "Splunk"]
                }
            ]
        elif any(kw in match_target for kw in ["ai", "machine learning", "deep learning", "neural", "intelligence", "language model"]):
            mock_clusters = [
                {
                    "category": "Neural Net Optimization Hardware",
                    "description": "Patented neuromorphic acceleration structures and logic gates designed for parallel tensor math.",
                    "saturation": "High",
                    "major_assignees": ["NVIDIA", "Intel", "Google"]
                },
                {
                    "category": "Natural Language Processing Models",
                    "description": "Patents covering speech-to-text decoding frameworks and attention-based weights systems.",
                    "saturation": "High",
                    "major_assignees": ["Google", "Microsoft", "Meta Platforms"]
                },
                {
                    "category": "Automated Code Compilation",
                    "description": "Generative code creation pipelines utilizing compiler validation to resolve syntax bugs.",
                    "saturation": "Medium",
                    "major_assignees": ["GitHub", "Microsoft", "OpenAI"]
                }
            ]
        elif "city" in match_target or "cities" in match_target or "urban" in match_target:
            mock_clusters = [
                {
                    "category": "Intelligent Traffic Management",
                    "description": "Patented systems for real-time traffic signal optimization and congestion prediction using vehicle telematics.",
                    "saturation": "High",
                    "major_assignees": ["Siemens", "IBM", "Cisco Systems"]
                },
                {
                    "category": "Smart Grid Power Distribution",
                    "description": "Patents covering automated load balancing and renewable energy integration in municipal grids.",
                    "saturation": "High",
                    "major_assignees": ["General Electric", "Schneider Electric", "ABB"]
                },
                {
                    "category": "Environmental Sensor Networks",
                    "description": "Distributed sensor mesh networks for monitoring air quality, noise, and climate indicators in urban spaces.",
                    "saturation": "Medium",
                    "major_assignees": ["Honeywell", "Intel", "Bosch"]
                }
            ]
        else:
            # Default to Smart Agriculture
            mock_clusters = [
                {
                    "category": "Automated Irrigation Valves",
                    "description": "Patented flow control systems adjusting irrigation release based on sensor triggers.",
                    "saturation": "High",
                    "major_assignees": ["John Deere", "Lindsay Corporation", "Valmont Industries"]
                },
                {
                    "category": "Soil Nutrient Sensors",
                    "description": "Patents covering localized electro-chemical probes measuring moisture and NPK indexes.",
                    "saturation": "High",
                    "major_assignees": ["Trimble", "Raven Industries", "Climate Corporation"]
                },
                {
                    "category": "Drone Ingestion Imaging",
                    "description": "Spectral camera mounting rigs and software stitching scheduled field flight grids.",
                    "saturation": "Medium",
                    "major_assignees": ["DJI", "PrecisionHawk", "AeroVironment"]
                }
            ]
        return json.dumps(mock_clusters)
        
    return "[]"
