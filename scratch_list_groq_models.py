import os
import sys
from groq import Groq
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('backend/.env')
key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=key)

try:
    models = client.models.list()
    print("Modelos disponibles en Groq:")
    for m in models.data:
        print(f" - {m.id}")
except Exception as e:
    print(f"Error listando modelos: {e}")
