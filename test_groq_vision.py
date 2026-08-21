import os
import base64
from dotenv import load_dotenv
from groq import Groq

load_dotenv("backend/.env")
groq_key = os.getenv("GROQ_API_KEY")

if groq_key:
    client = Groq(api_key=groq_key)
    print("Testing Groq Vision...")
    try:
        # Create a small dummy 100x100 white image
        import io
        from PIL import Image
        img = Image.new('RGB', (100, 100), color = 'red')
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "¿De qué color es esta imagen?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                ]
            }],
            model="llama-3.2-11b-vision-preview",
            temperature=0.1
        )
        print("Groq Vision Response:", chat_completion.choices[0].message.content)
    except Exception as e:
        print("Groq Vision Error:", e)
else:
    print("No GROQ_API_KEY in .env")
