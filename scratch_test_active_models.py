import os
import sys
from groq import Groq
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('backend/.env')
key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=key)

test_models = ["qwen/qwen3.6-27b", "groq/compound", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]

for m in test_models:
    try:
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": "Analiza brevemente: Dodgers vs Mariners"}],
            model=m,
            max_tokens=50
        ).choices[0].message.content.strip()
        print(f"EXITO con {m}: {resp[:80]}...")
    except Exception as e:
        print(f"FALLO con {m}: {e}")
