import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
print(f"API Key starting with: {api_key[:10] if api_key else 'None'}")

if api_key:
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            models_data = response.json()
            print("Available models:")
            for m in models_data.get("models", []):
                print(f" - {m.get('name')} (DisplayName: {m.get('displayName')})")
                print(f"   Supported methods: {m.get('supportedGenerationMethods')}")
        else:
            print("Error response:")
            print(response.text)
    except Exception as e:
        print(f"Error querying API: {e}")
else:
    print("No API key found in env.")
