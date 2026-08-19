import os
import sys
import re
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from groq import Groq

load_dotenv("backend/.env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

for model in ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.6-27b", "groq/compound-mini"]:
    try:
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": "Devuelve un JSON array con 2 equipos de fútbol: ['América', 'Chivas']"}],
            model=model,
            temperature=0.1
        )
        print(f"OK: Modelo {model} funciona: {resp.choices[0].message.content.strip()[:100]}")
    except Exception as e:
        print(f"FAIL: Error en {model}: {e}")
