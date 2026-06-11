import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import settings

def generate_response(prompt: str) -> str:
    """
    Call Gemini 2.5 Flash model with the given prompt.
    Returns the raw string output.
    """
    print("[LLM Client] Sending request to Gemini 2.5 Flash...")
    
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
    
    # 1. Check if the prompt is for the Research Agent
    if "research topics" in prompt_lower or "research_topics" in prompt_lower or "abstracts" in prompt_lower:
        # Check domain context
        if "healthcare" in prompt_lower or "medical" in prompt_lower or "diagnostic" in prompt_lower:
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
        elif "vehicle" in prompt_lower or "battery" in prompt_lower or "charging" in prompt_lower:
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
        elif any(kw in prompt_lower for kw in ["cybersecurity", "security", "cryptography", "firewall", "malware", "network"]):
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
        elif any(kw in prompt_lower for kw in ["ai", "machine learning", "deep learning", "neural", "intelligence", "language model"]):
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
        
    return "[]"
