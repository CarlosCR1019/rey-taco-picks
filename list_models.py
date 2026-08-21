import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv("backend/.env")
groq_key = os.getenv("GROQ_API_KEY")

if groq_key:
    client = Groq(api_key=groq_key)
    models = client.models.list()
    for m in models.data:
        print(f"Model ID: {m.id}")
