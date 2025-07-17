"""
Groq API Configuration Test Script
This script verifies that the Groq API key is properly configured.
"""

import os
from dotenv import load_dotenv

def check_groq_config():
    print("=== Groq API Configuration Check ===\n")
    
    # Load environment variables from project root
    project_root = os.path.join(os.path.dirname(__file__), "..", "..")
    env_file_path = os.path.join(project_root, ".env")
    load_dotenv(env_file_path)
    
    # Check if .env file exists
    if os.path.exists(env_file_path):
        print(f"[SUCCESS] .env file found at {env_file_path}")
    else:
        print(f"[ERROR] .env file not found at {env_file_path}")
        return False
    
    # Check if API key is set
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[ERROR] GROQ_API_KEY not found in environment variables")
        return False
    elif api_key == "your_groq_api_key_here":
        print("[ERROR] GROQ_API_KEY is still set to placeholder value")
        print("Please update your .env file with your actual Groq API key")
        return False
    elif api_key.startswith("gsk_"):
        print("[SUCCESS] GROQ_API_KEY is properly configured")
        print(f"API Key: {api_key[:10]}...{api_key[-4:]}")  # Show partial key for verification
        return True
    else:
        print("[WARNING] GROQ_API_KEY format doesn't match expected pattern (should start with 'gsk_')")
        return False

if __name__ == "__main__":
    if check_groq_config():
        print("\n[READY] Groq API is configured and ready to use!")
        print("You can now run the issue mapping agent successfully.")
    else:
        print("\n[ACTION NEEDED] Please configure your Groq API key:")
        print("1. Get your API key from: https://console.groq.com/")
        print("2. Update the GROQ_API_KEY in your .env file")
        print("3. Run this script again to verify")
