# services/issue-mapping-agent/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from transformers import pipeline, set_seed
import os
import re # For simple output parsing

app = FastAPI(
    title="Issue Mapping Agent",
    description="Maps user natural language queries to structured issue types using an LLM prompt.",
    version="2.0.0" # Updated version to reflect new approach
)

# --- LLM Setup ---
# Using a small text generation model. For structured output, a model
# fine-tuned for instruction following or specific extraction tasks would be better.
# For MVP, this demonstrates prompt-based extraction.
# You might need to change the model if you encounter issues or want better performance.
# Examples: 'gpt2', 'distilgpt2', 'facebook/opt-125m'
# Note: 'gpt2' is ~500MB, 'distilgpt2' is smaller (~300MB).
# Downloading might take time on first run.
MODEL_NAME = os.getenv("LLM_MODEL_NAME", "distilgpt2") # Using distilgpt2 for smaller size
GENERATION_MAX_LENGTH = 150 # Max tokens for the LLM response

try:
    # Set seed for reproducibility (useful for demos)
    set_seed(42)
    # Use text-generation pipeline
    generator = pipeline("text-generation", model=MODEL_NAME)
    print(f"LLM ({MODEL_NAME}) text-generation pipeline loaded successfully.")
except Exception as e:
    print(f"Error loading LLM pipeline: {e}")
    generator = None # Set to None if loading fails

# --- Pydantic Models for Request/Response ---
class UserMessageInput(BaseModel):
    user_message: str
    user_location: str = "Bengaluru, India" # Default for context

class MappedIssueOutput(BaseModel):
    original_query: str
    issue_type: str = Field(..., description="Standardized category (e.g., lighting_fault, temperature_control_issue, security_camera_issue, general_device_fault).")
    device_type: str = Field(..., description="Specific device type (e.g., smart light, thermostat, security camera, unknown_device).")
    severity: str = Field(..., description="Estimated impact level (e.g., critical, major, minor, medium).")
    llm_raw_output: str = Field(..., description="The direct, unparsed text output from the LLM.")

# --- API Endpoints ---
@app.get("/health")
async def health_check():
    if generator is None:
        raise HTTPException(status_code=503, detail="LLM pipeline not loaded.")
    return {"status": "ok", "llm_status": "loaded", "model": MODEL_NAME}

@app.post("/map_issue", response_model=MappedIssueOutput)
async def map_issue(input: UserMessageInput):
    if generator is None:
        raise HTTPException(status_code=503, detail="LLM pipeline is not loaded. Cannot process request.")

    user_message = input.user_message

    # Craft the prompt for the LLM
    # We ask the LLM to provide its answer in a specific JSON-like format
    prompt_template = f"""
Analyze the following smart home device issue description and extract the following details in a JSON format.
If a detail is not explicitly mentioned or clearly inferable, use "unknown" or "general" as appropriate.

User message: "{user_message}"

Output JSON:
{{
  "issue_type": "string", // Example: "lighting_fault", "temperature_control_issue", "security_camera_issue", "general_device_fault", "unclassified_issue"
  "device_type": "string", // Example: "smart light", "thermostat", "security camera", "smart lock", "unknown_device"
  "severity": "string" // Example: "critical", "major", "minor", "medium"
}}
"""
    
    try:
        # Generate text using the LLM
        # num_return_sequences=1 ensures we get one output
        # max_new_tokens limits the length of the generated response
        # trust_remote_code=True if using custom model code
        # do_sample=False for deterministic output (might not be fully deterministic with some models)
        llm_output = generator(prompt_template, 
                                max_new_tokens=GENERATION_MAX_LENGTH, 
                                num_return_sequences=1, 
                                do_sample=False, # Attempt for deterministic output
                                pad_token_id=generator.tokenizer.eos_token_id # Important for generation
                                )[0]['generated_text']

        # Extract only the JSON part from the LLM's full output
        # LLMs often repeat the prompt or add conversational text.
        json_match = re.search(r'\{\s*"issue_type":\s*".*?".*?\}', llm_output, re.DOTALL)
        
        parsed_json_str = ""
        if json_match:
            parsed_json_str = json_match.group(0)
            print(f"Parsed JSON from LLM output: {parsed_json_str}")
        else:
            print(f"Could not find JSON in LLM output. Raw output: {llm_output}")
            # Fallback to defaults or raise error if JSON not found
            # For robustness, you might apply a simpler keyword parser here if LLM fails.
            
        # Attempt to parse the extracted JSON string
        try:
            # Need to fix common LLM JSON output issues (like trailing commas, newlines)
            # This is a very basic fix, a more robust JSON parser might be needed for complex outputs
            parsed_json_str = parsed_json_str.replace('\n', '').replace('\\"', '"')
            # Removing potential trailing commas before closing braces if the LLM adds them
            parsed_json_str = re.sub(r',\s*\}', '}', parsed_json_str)

            extracted_data = json.loads(parsed_json_str)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}. Raw extracted string: {parsed_json_str}")
            # Fallback if JSON parsing fails
            extracted_data = {
                "issue_type": "unclassified_issue",
                "device_type": "unknown_device",
                "severity": "medium"
            }

    except Exception as e:
        print(f"Error during LLM inference or parsing: {e}")
        raise HTTPException(status_code=500, detail=f"LLM processing error: {e}")

    # Use extracted data, provide defaults if LLM didn't fill them
    issue_type = extracted_data.get("issue_type", "unclassified_issue")
    device_type = extracted_data.get("device_type", "unknown_device")
    severity = extracted_data.get("severity", "medium")

    return MappedIssueOutput(
        original_query=user_message,
        issue_type=issue_type,
        device_type=device_type,
        severity=severity,
        llm_raw_output=llm_output # Provide raw output for debugging
    )

@app.get("/")
async def root():
    return {"message": "Issue Mapping Agent is running with LLM prompting!"}