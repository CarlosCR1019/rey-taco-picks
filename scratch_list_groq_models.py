import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv('backend/.env')
api_key = os.getenv("GROQ_API_KEY")
print("API Key exists:", bool(api_key))
client = Groq(api_key=api_key)

try:
    models = client.models.list()
    print("Available Groq Models on this key:")
    for m in models.data:
        print(f" - {m.id}")
except Exception as e:
    print(f"Error listing models: {e}")
