import re
import json
import httpx
from dotenv import load_dotenv
import os

# --- Load Environment Variables ---
# Load .env file from project root (two directories up)
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
env_file_path = os.path.join(project_root, ".env")
load_dotenv(env_file_path)

# --- Groq API Setup ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # 🔑 <--- Put your actual API key here
GROQ_MODEL = "llama3-8b-8192"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- Core Function ---
async def call_groq_llm(prompt: str) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("Groq API key not configured. Please set GROQ_API_KEY in your .env file.")
    
    if GROQ_API_KEY == "your_groq_api_key_here":
        raise RuntimeError("Please replace 'your_groq_api_key_here' with your actual Groq API key in the .env file.")
    
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
        try:
            response = await client.post(GROQ_URL, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise RuntimeError("Invalid Groq API key. Please check your GROQ_API_KEY in the .env file.")
            else:
                raise RuntimeError(f"Groq API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Failed to call Groq API: {str(e)}")

# --- Exhaustive Prompt Builder ---
def build_exhaustive_prompt(user_message: str, fields: list) -> str:
    # Format the JSON template
    json_template = "{\n" + ",\n".join([f'  "{field}": "string"' for field in fields]) + "\n}"
    
    # Detailed field descriptions for better extraction
    field_descriptions = {
        "issue_type": "Type of problem (functionality, connectivity, power, security, performance, hardware, software, user_error)",
        "device_type": "Specific device category (smart_light, smart_lock, thermostat, camera, speaker, sensor, hub, switch, outlet, etc.)",
        "severity": "Impact level (critical, high, medium, low) - critical: device unusable, high: major features broken, medium: some features affected, low: minor issues",
        "location": "Physical location (living_room, bedroom, kitchen, bathroom, garage, outdoor, hallway, basement, attic, office, etc.)",
        "model": "Device model number or name (extract from text if mentioned)",
        "brand": "Manufacturer name (Philips, Samsung, Google, Amazon, Apple, Nest, Ring, TP-Link, etc.)",
        "power_source": "How device is powered (battery, wired, solar, usb, plug-in, hardwired)",
        "last_working_time": "When it last worked properly (just_now, minutes_ago, hours_ago, yesterday, days_ago, weeks_ago, months_ago, unknown)",
        "frequency": "How often issue occurs (always, frequently, occasionally, rarely, first_time, intermittent)",
        "user_action_taken": "What user tried to fix it (restart, reset, power_cycle, app_reinstall, check_connections, none, multiple_attempts)",
        "connected_devices": "Other devices affected or involved (list specific devices or 'none' or 'unknown')",
        "firmware_version": "Software/firmware version if mentioned",
        "error_code": "Any error codes, numbers, or messages mentioned",
        "environmental_conditions": "Relevant environment factors (weather, temperature, humidity, power_outage, wifi_issues, recent_changes)",
        "recurrence": "Pattern of occurrence (daily, weekly, random, after_updates, during_specific_times, weather_related)",
        "user_expertise_level": "Technical skill level implied (beginner, intermediate, advanced) - based on language used and troubleshooting attempted"
    }
    
    # Build detailed field list with descriptions
    field_list = "\n".join([f"- {field}: {field_descriptions.get(field, 'Extract relevant information')}" for field in fields])
    
    prompt = f"""
You are an expert smart home device support analyst. Analyze the following user issue description and extract comprehensive technical details in JSON format.

EXTRACTION GUIDELINES:
1. Read the user message carefully and extract ALL relevant information
2. For each field, provide the most specific and accurate value possible
3. Use the provided value options when they match the situation
4. If information is not explicitly stated but can be reasonably inferred from context, make that inference
5. Only use "unknown" when absolutely no information or reasonable inference is possible
6. For severity, consider: Does it affect safety? Is the device completely unusable? Are core functions broken?
7. For user_expertise_level, analyze: technical language used, troubleshooting steps mentioned, familiarity with device terminology

FIELDS TO EXTRACT:
{field_list}

USER ISSUE DESCRIPTION: "{user_message}"

ANALYSIS INSTRUCTIONS:
- Extract device type with maximum specificity (e.g., "smart_bulb" not just "light")
- Infer severity based on user's tone and impact described
- Look for temporal clues for last_working_time and frequency
- Identify any mentioned brands, models, or technical details
- Note any troubleshooting steps the user has already tried
- Consider environmental factors that might be relevant
- Assess user's technical knowledge from their description

OUTPUT ONLY VALID JSON (no comments, no explanations, no additional text):
{json_template}

IMPORTANT: Return ONLY the JSON object. Do not include any explanatory text, notes, or comments before or after the JSON.
"""
    return prompt

# --- Test Function ---
import asyncio

async def test_map_issue():
    # Test cases with varying complexity
    test_cases = [
        "My smart light keeps flickering and won't turn off.",
        "The Philips Hue bulb in my bedroom stopped responding yesterday after the power went out. I tried restarting the app and power cycling it but nothing works.",
        "My Ring doorbell camera isn't recording motion events anymore. It worked fine last week but now the live view shows but no recordings are saved. The LED is blue.",
        "Nest thermostat showing error E73. Temperature reading seems off by 5 degrees. I checked the wiring connections and they look fine. This started after the latest firmware update 3 days ago."
    ]
    
    # Use the first test case for demonstration
    user_message = test_cases[1]  # Using more detailed case
    
    fields = [
        "issue_type",
        "device_type", 
        "severity",
        "location",
        "model",
        "brand",
        "power_source",
        "last_working_time",
        "frequency",
        "user_action_taken",
        "connected_devices",
        "firmware_version",
        "error_code",
        "environmental_conditions",
        "recurrence",
        "user_expertise_level"
    ]
    
    print(f"\n[TEST] Analyzing issue: '{user_message}'\n")
    prompt = build_exhaustive_prompt(user_message, fields)
    
    try:
        llm_output = await call_groq_llm(prompt)
        print("\n[LLM] Groq LLM Raw Output:\n", llm_output)

        # Enhanced JSON extraction with better cleaning
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', llm_output, re.DOTALL)
        if not json_match:
            # Fallback: try to find any JSON-like structure
            json_match = re.search(r'\{.*?\}', llm_output, re.DOTALL)
        
        parsed_json_str = json_match.group(0) if json_match else ""
        
        if not parsed_json_str:
            raise ValueError("No JSON found in LLM output")

        # Clean up the JSON string more thoroughly
        # Remove comments like "(inferred from brand)"
        parsed_json_str = re.sub(r'\s*\([^)]*\)', '', parsed_json_str)
        parsed_json_str = parsed_json_str.replace('\n', ' ').replace('\\"', '"')
        parsed_json_str = re.sub(r'(,)\s*([}\]])', r'\2', parsed_json_str)
        parsed_json_str = re.sub(r'\s+', ' ', parsed_json_str)  # Normalize whitespace

        extracted_data = json.loads(parsed_json_str)
        
        print("\n[SUCCESS] Parsed Output:")
        for key, value in extracted_data.items():
            print(f"  {key}: {value}")
        
        return extracted_data

    except Exception as e:
        print("\n[ERROR] Test Failed:", e)

# --- Run Directly ---
async def run_multiple_tests():
    """Test the exhaustive prompt with various scenarios"""
    test_cases = [
        {
            "name": "Simple Issue",
            "message": "My smart light keeps flickering and won't turn off."
        },
        {
            "name": "Detailed Issue", 
            "message": "The Philips Hue bulb in my bedroom stopped responding yesterday after the power went out. I tried restarting the app and power cycling it but nothing works."
        },
        {
            "name": "Security Device Issue",
            "message": "My Ring doorbell camera isn't recording motion events anymore. It worked fine last week but now the live view shows but no recordings are saved. The LED is blue."
        },
        {
            "name": "Technical Issue with Error Code",
            "message": "Nest thermostat showing error E73. Temperature reading seems off by 5 degrees. I checked the wiring connections and they look fine. This started after the latest firmware update 3 days ago."
        }
    ]
    
    fields = [
        "issue_type", "device_type", "severity", "location", "model", "brand",
        "power_source", "last_working_time", "frequency", "user_action_taken",
        "connected_devices", "firmware_version", "error_code", 
        "environmental_conditions", "recurrence", "user_expertise_level"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {test_case['name']}")
        print(f"{'='*60}")
        print(f"Message: '{test_case['message']}'")
        
        try:
            prompt = build_exhaustive_prompt(test_case['message'], fields)
            llm_output = await call_groq_llm(prompt)
            
            # Clean and parse JSON
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', llm_output, re.DOTALL)
            if not json_match:
                json_match = re.search(r'\{.*?\}', llm_output, re.DOTALL)
            
            if json_match:
                parsed_json_str = json_match.group(0)
                parsed_json_str = re.sub(r'\s*\([^)]*\)', '', parsed_json_str)
                parsed_json_str = parsed_json_str.replace('\n', ' ')
                parsed_json_str = re.sub(r'\s+', ' ', parsed_json_str)
                
                extracted_data = json.loads(parsed_json_str)
                print(f"\n[SUCCESS] Extracted Data:")
                for key, value in extracted_data.items():
                    print(f"  {key}: {value}")
            else:
                print(f"[ERROR] No JSON found in output")
                
        except Exception as e:
            print(f"[ERROR] Test failed: {e}")
        
        if i < len(test_cases):
            print(f"\n{'-'*40}")

if __name__ == "__main__":
    # Run single test or multiple tests
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        asyncio.run(run_multiple_tests())
    else:
        asyncio.run(test_map_issue())