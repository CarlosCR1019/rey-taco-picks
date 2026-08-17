import os
import sys
from groq import Groq
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('backend/.env')
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

models_to_test = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.6-27b", "groq/compound-mini"]

for m in models_to_test:
    try:
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": "Di 'HOLA'"}],
            model=m,
            temperature=0.2
        )
        print(f"OK {m}: {resp.choices[0].message.content.strip()}")
    except Exception as e:
        print(f"ERR {m}: {e}")
