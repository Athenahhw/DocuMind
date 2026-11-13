
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing")

print("1. API Key loaded", flush=True)
print(f"2. Model: {model}", flush=True)

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        timeout=60000,
        retry_options=types.HttpRetryOptions(
            attempts=1,
        ),
    ),
)

print("3. Sending request to Gemini...", flush=True)
start = time.time()

try:
    
    response = client.models.generate_content(
    model=model,
    contents="Reply with exactly one word: Hello",
    config=types.GenerateContentConfig(
        max_output_tokens=100,
    ),
)


    print(f"4. Response received in {time.time() - start:.1f}s")
    print(response.text)

except Exception as e:
    print(f"Request failed after {time.time() - start:.1f}s")
    print(f"Error type: {type(e).__name__}")
    print(f"Error: {e}")
