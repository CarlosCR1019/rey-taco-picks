import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv("backend/.env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    models = client.models.list()
    print("Modelos disponibles en tu API Key de Groq:")
    for m in models.data:
        print(f" - {m.id}")
except Exception as e:
    print(f"Error listando modelos: {e}")
