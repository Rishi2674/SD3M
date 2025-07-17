# services/rsps/rsps_core.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from services.issue_mapping_agent.map_issue import map_issue
from services.gars.main import query_agents
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from dotenv import load_dotenv
import os
import time

# Load environment variables from .env file
load_dotenv()

# --- MongoDB Setup ---
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable not set. Please create a .env file in services/rsps.")

client: Optional[MongoClient] = None

def get_mongo_db_connection():
    global client
    if client is None:
        try:
            client = MongoClient(MONGO_URI)
            client.admin.command('ping')
            print("RSPS Core: MongoDB connection successful!")
        except ConnectionFailure as e:
            print(f"RSPS Core: MongoDB connection failed: {e}")
            raise

    db_name = "s3dm_db"
    return client[db_name]

def close_mongo_db_connection():
    global client
    if client:
        client.close()
        print("RSPS Core: MongoDB connection closed.")

# --- Workflow Templates ---
WORKFLOW_TEMPLATES = {
    "lighting_fault": [
        {"task_name": "Remote Diagnostics", "capability": "remote_diagnostics", "description": "Perform initial remote diagnostics of the smart light."},
        {"task_name": "Physical Repair", "capability": "smart_lighting_repair", "description": "Dispatch technician for physical repair."},
        {"task_name": "Verify Fix", "capability": "verify_fix", "description": "Verify the fix with customer or automated test."}
    ],
    "temperature_control_issue": [
        {"task_name": "Remote Diagnostics", "capability": "remote_diagnostics", "description": "Perform initial remote diagnostics of the thermostat."},
        {"task_name": "HVAC Repair", "capability": "hvac_repair", "description": "Dispatch HVAC specialist for repair."},
        {"task_name": "Verify Fix", "capability": "verify_fix", "description": "Verify the fix with customer or automated test."}
    ],
    "security_camera_fault": [
        {"task_name": "Remote Diagnostics", "capability": "remote_diagnostics", "description": "Perform initial remote diagnostics of the security camera."},
        {"task_name": "Network Diagnostics", "capability": "network_diagnostics", "description": "Check network connectivity for camera."},
        {"task_name": "Physical Repair", "capability": "security_system_repair", "description": "Dispatch technician for physical repair if needed."},
        {"task_name": "Verify Fix", "capability": "verify_fix", "description": "Verify the fix with customer or automated test."}
    ],
    "general_device_fault": [
        {"task_name": "Initial Assessment", "capability": "general_diagnostics", "description": "Perform general remote diagnostics."},
        {"task_name": "General Repair", "capability": "general_diagnostics", "description": "Dispatch general technician for repair."},
        {"task_name": "Verify Fix", "capability": "verify_fix", "description": "Verify the fix with customer or automated test."}
    ],
    "unclassified_issue": [
        {"task_name": "Initial Assessment", "capability": "general_diagnostics", "description": "Perform initial assessment for unclassified issue."},
        {"task_name": "Manual Review", "capability": "manual_review", "description": "Escalate for manual review by human agent."}
    ]
}

# --- Data Models ---
def create_ticket_data_doc(original_user_message, issue_type, device_type, severity, user_location, status="Received"):
    return {
        "original_user_message": original_user_message,
        "issue_type": issue_type,
        "device_type": device_type,
        "severity": severity,
        "user_location": user_location,
        "status": status,
        "planned_workflow": [],
        "current_step_index": 0,
        "created_at": time.time()
    }

def create_workflow_step_data(task_name, capability, description, status="pending", assigned_agent_id=None, assigned_agent_name=None, start_time=None, end_time=None):
    return {
        "task_name": task_name,
        "capability": capability,
        "description": description,
        "status": status,
        "assigned_agent_id": assigned_agent_id,
        "assigned_agent_name": assigned_agent_name,
        "start_time": start_time,
        "end_time": end_time
    }

# --- Core RSPS Logic ---
def plan_and_submit_ticket(user_message: str, user_location: str) -> Dict[str, Any]:
    db = get_mongo_db_connection()
    tickets_collection = db["tickets"]

    try:
        mapped_data = map_issue(user_message)
        print(f"RSPS: Mapped issue data from LLM: {mapped_data['issue_type']} for {mapped_data['device_type']}")

        new_ticket_doc = create_ticket_data_doc(
            user_message,
            mapped_data['issue_type'],
            mapped_data['device_type'],
            mapped_data['severity'],
            user_location,
            status="Processing"
        )
        result = tickets_collection.insert_one(new_ticket_doc)
        ticket_id_str = str(result.inserted_id)
        new_ticket_doc["_id"] = result.inserted_id

        workflow_template = WORKFLOW_TEMPLATES.get(mapped_data["issue_type"], WORKFLOW_TEMPLATES["general_device_fault"])
        planned_workflow_steps = []
        all_agents_found = True

        city, country = (user_location.split(',') + [None]*2)[:2]
        city, country = city.strip(), country.strip() if country else None

        for task in workflow_template:
            required_capability = task["capability"]
            try:
                agents = query_agents(required_capability, country, city)
            except Exception as e:
                print(f"RSPS: GARS query error for capability '{required_capability}': {e}")
                agents = []

            if agents:
                agent = agents[0]
                planned_workflow_steps.append(create_workflow_step_data(task["task_name"], required_capability, task["description"], assigned_agent_id=agent["id"], assigned_agent_name=agent["name"]))
            else:
                all_agents_found = False
                planned_workflow_steps.append(create_workflow_step_data(task["task_name"], required_capability, task["description"], status="unassigned"))

        ticket_status = "Workflow Planned" if all_agents_found else "Workflow Partially Planned (Missing Agents)"
        tickets_collection.update_one({"_id": ObjectId(ticket_id_str)}, {"$set": {"planned_workflow": planned_workflow_steps, "status": ticket_status}})

        updated_ticket = tickets_collection.find_one({"_id": ObjectId(ticket_id_str)})
        if updated_ticket:
            updated_ticket["id"] = str(updated_ticket.pop("_id"))
        return updated_ticket

    except Exception as e:
        print(f"RSPS: Error processing ticket: {e}")
        raise

# --- Test Block ---
def run_rsps_tests_sync():
    print("--- Running RSPS Core Tests (Synchronous) ---")
    try:
        messages = [
            ("My smart light in the living room is not turning on.", "Bengaluru, India"),
            ("Thermostat is broken.", "Delhi, India"),
            ("Quantum machine issue.", "Antarctica")
        ]
        for msg, loc in messages:
            print(f"\nProcessing: '{msg}' in {loc}")
            result = plan_and_submit_ticket(msg, loc)
            print(f"Ticket ID: {result['id']}, Status: {result['status']}")
            for step in result.get("planned_workflow", [])[:3]:
                print(f"  - {step['task_name']} ({step['capability']}) => {step.get('assigned_agent_name', 'Unassigned')} [{step['status']}]")

    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        close_mongo_db_connection()

if __name__ == "__main__":
    run_rsps_tests_sync()
