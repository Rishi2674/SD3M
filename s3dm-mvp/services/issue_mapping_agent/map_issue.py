import re
import json
import httpx
import os
from dotenv import load_dotenv

# --- Load Environment Variables ---
# project_root = os.path.join(os.path.dirname(__file__), "..", "..")
# env_file_path = os.path.join(project_root, ".env")
load_dotenv()

# --- Groq API Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama3-8b-8192"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- Prompt Builder ---
def build_exhaustive_prompt(user_message: str, fields: list) -> str:
    json_template = "{\n" + ",\n".join([f'  "{field}": "string"' for field in fields]) + "\n}"

    field_descriptions = {
        "issue_type": "Type of problem (functionality, connectivity, power, security, performance, hardware, software, user_error)",
        "device_type": "Specific device category (smart_light, smart_lock, thermostat, camera, speaker, sensor, hub, switch, outlet, etc.)",
        "severity": "Impact level (critical, high, medium, low)",
        "location": "Physical location (living_room, bedroom, kitchen, etc.)",
        # "model": "Device model number or name",
        "brand": "Manufacturer name",
        # "power_source": "How device is powered (battery, wired, etc.)",
        # "last_working_time": "When it last worked (just_now, yesterday, etc.)",
        # "frequency": "How often issue occurs (always, first_time, etc.)",
        # "user_action_taken": "What user tried to fix it",
        # "connected_devices": "Other devices affected",
        # "firmware_version": "Firmware version",
        "error_code": "Any error codes or messages",
        "environmental_conditions": "Environment factors (weather, power outage, etc.)",
        # "recurrence": "Pattern of occurrence",
        # "user_expertise_level": "Technical skill level implied (beginner, intermediate, advanced)"
    }

    field_list = "\n".join([f"- {field}: {field_descriptions.get(field, '')}" for field in fields])

    prompt = f"""
You are an expert smart home device support analyst. Analyze the following user issue description and extract comprehensive technical details in JSON format.

EXTRACTION GUIDELINES:
1. Extract ALL relevant information
2. Use provided value options where appropriate
3. Make reasonable inferences
4. Only use "unknown" when absolutely no information is available

FIELDS TO EXTRACT:
{field_list}

USER ISSUE DESCRIPTION: "{user_message}"

OUTPUT ONLY VALID JSON:
{json_template}

IMPORTANT: Return ONLY the JSON object.
"""
    return prompt

# --- Core LLM Call (Synchronous) ---
def call_groq_llm_sync(prompt: str) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("Groq API key not configured in .env")

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

    with httpx.Client(timeout=30) as client:
        response = client.post(GROQ_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

# --- Main Function ---
def map_issue(user_message: str) -> dict:
    fields = [
        "issue_type", "device_type", "severity", "location", "brand",
        "error_code", "environmental_conditions"
    ]

    prompt = build_exhaustive_prompt(user_message, fields)
    llm_output = call_groq_llm_sync(prompt)

    # Extract and clean JSON
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', llm_output, re.DOTALL)
    if not json_match:
        raise ValueError("No JSON found in LLM output")

    parsed_json_str = json_match.group(0)
    parsed_json_str = re.sub(r'\s*\([^)]*\)', '', parsed_json_str)
    parsed_json_str = parsed_json_str.replace('\n', ' ')
    parsed_json_str = re.sub(r'\s+', ' ', parsed_json_str)
    parsed_json_str = re.sub(r'(,)\s*([}\]])', r'\2', parsed_json_str)

    return json.loads(parsed_json_str)


if __name__ == "__main__":
    user_input = "The Philips Hue bulb in my bedroom stopped responding yesterday after the power went out. I tried restarting the app and power cycling it but nothing works."
    extracted = map_issue(user_input)
    print(json.dumps(extracted, indent=2))
