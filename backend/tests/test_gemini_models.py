import os
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import settings

def test_models():
    api_key = settings.GOOGLE_API_KEY
    if not api_key:
        print("Error: No API key found.")
        return
        
    models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.5-flash"]
    for model_name in models:
        print(f"Testing model: {model_name}...")
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0.1
            )
            response = llm.invoke("Say hello.")
            print(f"  [SUCCESS] {model_name} responded: {response.content.strip()}")
            return model_name
        except Exception as e:
            print(f"  [FAILED] {model_name}: {e}")
            
    return None

if __name__ == "__main__":
    test_models()
