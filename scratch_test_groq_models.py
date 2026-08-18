import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv('backend/.env')
key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=key)

models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]

for m in models:
    try:
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": "Di 'OK'"}],
            model=m,
            max_tokens=10
        ).choices[0].message.content.strip()
        print(f"✅ Modelo {m}: {resp}")
    except Exception as e:
        print(f"❌ Modelo {m}: {e}")
