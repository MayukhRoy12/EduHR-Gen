from google import genai
import os

# REPLACE THIS WITH YOUR ACTUAL API KEY
API_KEY = "AIzaSyB7e06-Hq1LEwe4jJ1MXRY2rbIr8UY8OwE" 

try:
    client = genai.Client(api_key=API_KEY)
    print("🔄 Connecting to Google AI...")
    
    # List all available models
    models = client.models.list()
    
    print("\n✅ AVAILABLE MODELS FOR YOU:")
    found_any = False
    for m in models:
        # We only care about models that can 'generateContent'
        if 'generateContent' in m.supported_generation_methods:
            print(f" - {m.name}")
            found_any = True
            
    if not found_any:
        print("❌ No text generation models found. Check your API Key permissions.")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
