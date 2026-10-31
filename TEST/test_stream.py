import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key = os.getenv("OPENAI_KEY"))

stream = client.chat.completions.create(
    model = "gpt-4o-mini",
    messages = [
        {
            "role" : "user",
            "content" : "Explain fever in 3 sentences"
        }
    ],
    stream = True
)

for chunks in stream:
    if chunks.choices:
        text = chunks.choices[0].delta.content
        if text:
            print(text, end="", flush=True)
print()