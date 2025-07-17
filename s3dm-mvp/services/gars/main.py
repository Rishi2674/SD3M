# services/gars/gars_core.py
from typing import List, Optional, Dict, Any, Set
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# --- MongoDB Setup ---
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable not set. Please create a .env file in services/gars.")

client: Optional[MongoClient] = None

def get_mongo_db_connection():
    """Returns the MongoDB database instance."""
    global client
    if client is None:
        try:
            client = MongoClient(MONGO_URI)
            client.admin.command('ping') # Test connection
            print("GARS Core: MongoDB connection successful!")
        except ConnectionFailure as e:
            print(f"GARS Core: MongoDB connection failed: {e}")
            raise ConnectionFailure(f"Database connection error: {e}") # Re-raise for calling code to handle
    
    db_name_from_uri = MONGO_URI.split('/')[-1].split('?')[0] if '/' in MONGO_URI else ""
    db_name = db_name_from_uri if db_name_from_uri and not db_name_from_uri.startswith('?') else "s3dm_db"
    
    return client[db_name]

def close_mongo_db_connection():
    """Closes MongoDB connection."""
    global client
    if client:
        client.close()
        print("GARS Core: MongoDB connection closed.")

# --- Data Models (Python dictionaries for simplicity without Pydantic) ---

def create_agent_data(
    name: str,
    capabilities: List[str],
    jurisdiction_country: str,
    jurisdiction_city: str,
    cost: int,
    trust_score: int = 5,
    active: int = 1
) -> Dict[str, Any]:
    """Helper to structure agent data."""
    return {
        "name": name,
        "capabilities": capabilities,
        "jurisdiction_country": jurisdiction_country,
        "jurisdiction_city": jurisdiction_city,
        "cost": cost,
        "trust_score": trust_score,
        "active": active
    }

# --- Core GARS Functions ---

def register_agent(agent_data: Dict[str, Any]) -> Dict[str, Any]:
    """Registers a new agent in the Global Agent Registry."""
    db = get_mongo_db_connection()
    agents_collection = db["agents"]
    
    if agents_collection.find_one({"name": agent_data["name"]}):
        raise ValueError(f"Agent with name '{agent_data['name']}' already exists.")
        
    result = agents_collection.insert_one(agent_data)
    new_agent_doc = agents_collection.find_one({"_id": result.inserted_id})
    if new_agent_doc:
        new_agent_doc["id"] = str(new_agent_doc.pop("_id")) # Rename _id to id and convert to string
        return new_agent_doc
    else:
        raise RuntimeError("Failed to retrieve newly registered agent.")

def query_agents(
    capability: Optional[str] = None,
    country: Optional[str] = None,
    city: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Queries registered agents based on specified criteria.
    Agents are filtered by active status and sorted by trust score (desc) then cost (asc).
    """
    db = get_mongo_db_connection()
    agents_collection = db["agents"]
    
    query_filter = {"active": 1}

    if capability:
        query_filter["capabilities"] = capability
    if country:
        query_filter["jurisdiction_country"] = country
    if city and city.lower() != "any":
        query_filter["jurisdiction_city"] = {"$in": [city, "Any"]}
    elif city and city.lower() == "any":
        query_filter["jurisdiction_city"] = "Any"

    agents_cursor = agents_collection.find(query_filter).sort([("trust_score", -1), ("cost", 1)])
    
    agents_list = []
    for agent in agents_cursor:
        agent["id"] = str(agent.pop("_id")) # Rename _id to id and convert to string
        agents_list.append(agent)
    return agents_list

def get_all_capabilities() -> List[str]:
    """Returns a list of all unique capabilities registered by active agents."""
    db = get_mongo_db_connection()
    agents_collection = db["agents"]
    
    pipeline = [
        {"$match": {"active": 1}},
        {"$unwind": "$capabilities"},
        {"$group": {"_id": None, "all_capabilities": {"$addToSet": "$capabilities"}}}
    ]
    
    result = list(agents_collection.aggregate(pipeline))
    
    if result and result[0].get("all_capabilities"):
        return sorted(list(result[0]["all_capabilities"]))
    return []

def add_sample_agents():
    """Adds sample agents to the database if they don't already exist."""
    db = get_mongo_db_connection()
    agents_collection = db["agents"]
    
    sample_agents_data = [
        create_agent_data("Bengaluru Smart Light Repair Co.", ["smart_lighting_repair", "electrical_diagnostics", "general_diagnostics"], "India", "Bengaluru", 50, 8, 1),
        create_agent_data("Delhi HVAC Solutions Inc.", ["hvac_repair", "temperature_sensor_calibration", "general_diagnostics"], "India", "Delhi", 70, 7, 1),
        create_agent_data("Global Logistics Express", ["part_delivery", "device_pickup"], "India", "Any", 30, 9, 1),
        create_agent_data("Smart Device Diagnostics AI", ["remote_diagnostics", "firmware_update"], "Global", "Any", 10, 9, 1),
        create_agent_data("European Fridge Manufacturer", ["fridge_diagnostics", "compressor_replacement", "part_identification"], "Germany", "Berlin", 100, 8, 1),
        create_agent_data("Bengaluru General Technician", ["general_diagnostics", "physical_repair"], "India", "Bengaluru", 45, 7, 1),
        create_agent_data("Global Software Support", ["software_troubleshooting", "firmware_update"], "Global", "Any", 20, 8, 1),
        create_agent_data("Mumbai Electrician Service", ["electrical_diagnostics", "physical_repair"], "India", "Mumbai", 55, 6, 1)
    ]

    for agent_data in sample_agents_data:
        if agents_collection.count_documents({"name": agent_data["name"]}) == 0:
            agents_collection.insert_one(agent_data)
            print(f"GARS Core: Added sample agent: {agent_data['name']}.")
            
def run_gars_tests():
    print("--- Running GARS Core Tests ---")
    try:
        # 1. Add sample agents (will only add if they don't exist)
        print("\nAttempting to add sample agents...")
        add_sample_agents()
        print("Sample agents check/addition complete.")

        # 2. Test Register Agent
        print("\nAttempting to register a new agent (Mumbai HVAC Specialists)...")
        new_agent_data = create_agent_data(
            name="Mumbai HVAC Specialists",
            capabilities=["hvac_repair", "installation"],
            jurisdiction_country="India",
            jurisdiction_city="Mumbai",
            cost=80,
            trust_score=7,
            active=1
        )
        try:
            registered_agent = register_agent(new_agent_data)
            print(f"Registered new agent: {registered_agent['name']} with ID: {registered_agent['id']}")
        except ValueError as e:
            print(f"Could not register agent: {e}") # Expected if agent already exists

        # 3. Test Query Agents
        print("\nQuerying agents with capability 'smart_lighting_repair' in 'Bengaluru', 'India'...")
        lighting_agents = query_agents(
            capability="smart_lighting_repair",
            country="India",
            city="Bengaluru"
        )
        print(f"Found {len(lighting_agents)} lighting agent(s):")
        for agent in lighting_agents:
            print(f" - {agent['name']} (ID: {agent['id']}) - Trust: {agent['trust_score']}, Cost: {agent['cost']}")

        print("\nQuerying agents with capability 'remote_diagnostics' (Global coverage)...")
        remote_diagnostics_agents = query_agents(
            capability="remote_diagnostics"
        )
        print(f"Found {len(remote_diagnostics_agents)} remote diagnostics agent(s):")
        for agent in remote_diagnostics_agents:
            print(f" - {agent['name']} (ID: {agent['id']}) - Country: {agent['jurisdiction_country']}")

        print("\nQuerying agents with capability 'hvac_repair' in 'Mumbai', 'India' (should find 'Mumbai HVAC Specialists')...")
        mumbai_hvac_agents = query_agents(
            capability="hvac_repair",
            country="India",
            city="Mumbai"
        )
        print(f"Found {len(mumbai_hvac_agents)} Mumbai HVAC agent(s):")
        for agent in mumbai_hvac_agents:
            print(f" - {agent['name']} (ID: {agent['id']}) - City: {agent['jurisdiction_city']}")


        # 4. Test Get All Capabilities
        print("\nGetting all unique capabilities...")
        all_caps = get_all_capabilities()
        print(f"All capabilities: {all_caps}")

        print("\n--- GARS Core Tests PASSED! ---")

    except ConnectionFailure:
        print("\n--- GARS Core Tests FAILED! (MongoDB connection issue) ---")
        print("Please ensure your MongoDB Atlas cluster is running and accessible, and your MONGO_URI in .env is correct.")
    except Exception as e:
        print(f"\n--- GARS Core Tests FAILED unexpectedly! ---")
        print(f"An error occurred: {e}")
    finally:
        close_mongo_db_connection()

# if __name__ == "__main__":
#     run_gars_tests()