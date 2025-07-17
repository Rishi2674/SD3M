import re
import json
import httpx
from dotenv import load_dotenv
import os

# --- Load Environment Variables ---
load_dotenv()

# --- Groq API Setup ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # 🔑 <--- Put your actual API key here
GROQ_MODEL = "llama3-8b-8192"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- Core Function ---
async def call_groq_llm(prompt: str) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("Groq API key not configured.")
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are an assistant that extracts issue data as JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 400
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(GROQ_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

# --- Test Function ---
import asyncio

async def test_map_issue():
    user_message = "My smart light keeps flickering and won't turn off."

    prompt = f"""
Analyze the following smart home device issue description and extract the following details in a JSON format.
If a detail is not explicitly mentioned or clearly inferable, use "unknown" or "general" as appropriate.

User message: "{user_message}"

Output JSON:
{{
  "issue_type": "string", 
  "device_type": "string", 
  "severity": "string"
}}
"""
    try:
        llm_output = await call_groq_llm(prompt)
        print("\n🧠 Groq LLM Raw Output:\n", llm_output)

        json_match = re.search(r'\{(?:[^{}]|(?R))*\}', llm_output, re.DOTALL)
        parsed_json_str = json_match.group(0) if json_match else ""

        parsed_json_str = parsed_json_str.replace('\n', '').replace('\\"', '"')
        parsed_json_str = re.sub(r'(,)\s*([}\]])', r'\2', parsed_json_str)

        extracted_data = json.loads(parsed_json_str)
        print("\n✅ Parsed Output:\n", extracted_data)

    except Exception as e:
        print("\n❌ Test Failed:", e)

# --- Run Directly ---
if __name__ == "__main__":
    asyncio.run(test_map_issue())
