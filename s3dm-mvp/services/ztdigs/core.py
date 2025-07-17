# services/ztdigs/ztdigs_core.py
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from dotenv import load_dotenv
import os
import hashlib # For data hashing
from Crypto.PublicKey import RSA # From pycryptodome
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import time # For timestamps
import json # For consistent hashing of dicts

# Load environment variables from .env file
load_dotenv()

# --- MongoDB Setup ---
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable not set. Please create a .env file in services/ztdigs.")

client: Optional[MongoClient] = None

def get_mongo_db_connection():
    """Returns the MongoDB database instance."""
    global client
    if client is None:
        try:
            client = MongoClient(MONGO_URI)
            client.admin.command('ping')
            print("ZTDIGS Core: MongoDB connection successful!")
        except ConnectionFailure as e:
            print(f"ZTDIGS Core: MongoDB connection failed: {e}")
            raise ConnectionFailure(f"Database connection error: {e}")
    
    db_name_from_uri = MONGO_URI.split('/')[-1].split('?')[0] if '/' in MONGO_URI else ""
    db_name = db_name_from_uri if db_name_from_uri and not db_name_from_uri.startswith('?') else "s3dm_db"
    return client[db_name]

def close_mongo_db_connection():
    """Closes MongoDB connection."""
    global client
    if client:
        client.close()
        print("ZTDIGS Core: MongoDB connection closed.")

# --- Cryptographic Helpers (Dummy for MVP) ---
# In a real system, private keys would be securely managed by each agent.
# Here, we generate a single dummy key pair for demonstration.
# DO NOT USE IN PRODUCTION.
try:
    _key = RSA.generate(2048)
    _private_key_obj = _key
    _public_key_obj = _key.publickey()
    print("ZTDIGS Core: Dummy RSA key pair generated.")
except Exception as e:
    print(f"ZTDIGS Core: Warning: Could not generate dummy RSA key: {e}. Signatures will be placeholders.")
    _private_key_obj = None
    _public_key_obj = None

def calculate_data_hash(data: Dict[str, Any]) -> str:
    """Calculates SHA256 hash of a dictionary (ensuring consistent serialization)."""
    # Sort keys to ensure consistent JSON serialization for hashing
    json_string = json.dumps(data, sort_keys=True, default=str) # default=str handles ObjectId
    return hashlib.sha256(json_string.encode('utf-8')).hexdigest()

def generate_signature(data_to_sign_str: str) -> str:
    """Generates a dummy RSA signature for the given data string."""
    if _private_key_obj:
        h = SHA256.new(data_to_sign_str.encode('utf-8'))
        signer = pkcs1_15.new(_private_key_obj)
        signature = signer.sign(h)
        return signature.hex() # Return hex string of the signature
    return "DUMMY_SIGNATURE_PLACEHOLDER"

def verify_signature(data_to_verify_str: str, signature_hex: str) -> bool:
    """Verifies a dummy RSA signature for the given data string."""
    if _public_key_obj and signature_hex != "DUMMY_SIGNATURE_PLACEHOLDER":
        h = SHA256.new(data_to_verify_str.encode('utf-8'))
        verifier = pkcs1_15.new(_public_key_obj)
        try:
            verifier.verify(h, bytes.fromhex(signature_hex))
            return True
        except (ValueError, TypeError):
            return False
    return True # If no key or placeholder signature, always "verify" as true for MVP demo


# --- Data Contract Functions ---
def create_data_contract_doc(
    ticket_id: str,
    parties_involved: List[Dict[str, str]], # [{"agent_id": "...", "role": "..."}]
    data_elements_allowed: List[str], # e.g., ["device_id", "error_code"]
    purpose: str, # e.g., "for_diagnostics"
    expiry_timestamp: float, # Unix timestamp
    jurisdiction_rules_applied: List[str] # e.g., ["GDPR", "LGPD"]
) -> Dict[str, Any]:
    """Helper to structure data contract data."""
    contract_data = {
        "ticket_id": ticket_id,
        "parties_involved": parties_involved,
        "data_elements_allowed": data_elements_allowed,
        "purpose": purpose,
        "expiry_timestamp": expiry_timestamp,
        "jurisdiction_rules_applied": jurisdiction_rules_applied,
        "created_at": time.time()
    }
    contract_data["policy_hash"] = calculate_data_hash(contract_data) # Hash of the contract itself
    return contract_data

def generate_and_store_contract(contract_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generates a new data contract and stores it in MongoDB."""
    db = get_mongo_db_connection()
    contracts_collection = db["data_contracts"]
    
    result = contracts_collection.insert_one(contract_data)
    new_contract_doc = contracts_collection.find_one({"_id": result.inserted_id})
    if new_contract_doc:
        new_contract_doc["id"] = str(new_contract_doc.pop("_id"))
        return new_contract_doc
    else:
        raise RuntimeError("Failed to retrieve newly generated contract.")

def get_data_contract(contract_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a data contract by its ID."""
    db = get_mongo_db_connection()
    contracts_collection = db["data_contracts"]
    contract_doc = contracts_collection.find_one({"_id": ObjectId(contract_id)})
    if contract_doc:
        contract_doc["id"] = str(contract_doc.pop("_id"))
        return contract_doc
    return None

# --- Provenance Log Functions ---
def create_provenance_log_entry_data(
    ticket_id: str,
    agent_id: str,
    event_type: str, # e.g., "task_dispatched", "data_shared", "task_completed", "invoice_issued"
    details: str,
    data_payload: Dict[str, Any], # The actual data being logged/shared (will be hashed)
    contract_id: Optional[str] = None # Link to the relevant data contract
) -> Dict[str, Any]:
    """Helper to structure provenance log data."""
    event_timestamp = time.time()
    data_hash = calculate_data_hash(data_payload)

    return {
        "ticket_id": ticket_id,
        "agent_id": agent_id,
        "event_type": event_type,
        "details": details,
        "data_payload": data_payload, # Store original payload (can be redacted later)
        "data_hash": data_hash,
        "timestamp": event_timestamp,
        "contract_id": contract_id
    }

def log_provenance_event(log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Logs a new event to the immutable provenance log, with chaining and basic enforcement."""
    db = get_mongo_db_connection()
    provenance_collection = db["provenance_log"]

    # 1. Basic Contract Enforcement (simplified for MVP)
    if log_data.get("contract_id"):
        contract = get_data_contract(log_data["contract_id"])
        if not contract:
            raise ValueError(f"ZTDIGS: Contract {log_data['contract_id']} not found for event {log_data['event_type']}")
        
        # Check contract expiry
        if time.time() > contract.get("expiry_timestamp", 0):
            raise ValueError(f"ZTDIGS: Contract {contract['id']} has expired for event {log_data['event_type']}")
        
        # Check policy hash (if provided by sender, ensures sender uses correct contract)
        # For this simplified version, we just store the hash. Full check requires sender to send hash.
        if log_data.get("policy_hash") and log_data["policy_hash"] != contract["policy_hash"]:
             raise ValueError(f"ZTDIGS: Policy hash mismatch for contract {contract['id']}. Tampering detected or incorrect contract used.")

        # Check data elements allowed (conceptual for MVP)
        allowed_elements = set(contract.get("data_elements_allowed", []))
        if log_data.get("data_payload"):
            for key in log_data["data_payload"].keys():
                if key not in allowed_elements and allowed_elements: # If allowed_elements is not empty, check strictness
                    print(f"ZTDIGS: Warning: Data element '{key}' in payload not explicitly allowed by contract {contract['id']}.")
                    # In a strict system, this would raise an error.

        # Basic Jurisdiction Compliance Check (Conceptual)
        # Example: If contract specifies "GDPR" rules apply, and data contains PII, ensure agent is EU-compliant.
        # This requires more metadata from GARS and richer data payloads
        if "GDPR" in contract.get("jurisdiction_rules_applied", []):
            if "customer_name" in log_data.get("data_payload", {}) and "non_eu_agent_id" in log_data.get("agent_id", ""):
                 print(f"ZTDIGS: Warning: PII logged for GDPR contract to potentially non-EU agent. Requires review.")
                 # In a strict system, this would block the transaction.


    # 2. Get the hash of the last log entry for cryptographic chaining
    last_log_entry = provenance_collection.find_one(sort=[('_id', -1)])
    previous_log_hash = None
    if last_log_entry:
        # Create a hashable representation of the previous document
        temp_doc = last_log_entry.copy()
        temp_doc.pop("_id", None) # Remove _id for consistent hashing
        # Ensure ObjectId within payload is converted to string for consistent hash
        if 'data_payload' in temp_doc and isinstance(temp_doc['data_payload'], dict):
            if '_id' in temp_doc['data_payload'] and isinstance(temp_doc['data_payload']['_id'], ObjectId):
                temp_doc['data_payload']['_id'] = str(temp_doc['data_payload']['_id'])
        
        previous_log_hash = calculate_data_hash(temp_doc)

    # 3. Prepare the new log entry
    log_data["previous_log_hash"] = previous_log_hash
    # Generate signature for the event, ensuring agent_id is part of signed data
    data_for_sig = f"{log_data['ticket_id']}-{log_data['agent_id']}-{log_data['event_type']}-{log_data['timestamp']}-{log_data['data_hash']}-{log_data.get('contract_id', '')}-{previous_log_hash}"
    log_data["signature"] = generate_signature(data_for_sig)

    # 4. Insert into MongoDB
    result = provenance_collection.insert_one(log_data)
    new_log_entry_doc = provenance_collection.find_one({"_id": result.inserted_id})
    if new_log_entry_doc:
        new_log_entry_doc["id"] = str(new_log_entry_doc.pop("_id")) # Rename _id to id
        return new_log_entry_doc
    else:
        raise RuntimeError("Failed to retrieve newly logged provenance entry.")

def verify_provenance_chain() -> Dict[str, Any]:
    """Verifies the integrity of the entire provenance log chain."""
    db = get_mongo_db_connection()
    provenance_collection = db["provenance_log"]

    entries = list(provenance_collection.find().sort("timestamp", 1)) # Get all, sorted chronologically

    if not entries:
        return {"status": "No entries to verify.", "passed": True}

    is_tamper_proof = True
    for i in range(len(entries)):
        current_entry = entries[i]
        current_id = str(current_entry.get("_id"))

        # 1. Verify signature for current entry
        data_to_verify_sig = f"{current_entry.get('ticket_id')}-{current_entry.get('agent_id')}-{current_entry.get('event_type')}-{current_entry.get('timestamp')}-{current_entry.get('data_hash')}-{current_entry.get('contract_id', '')}-{current_entry.get('previous_log_hash')}"
        if not verify_signature(data_to_verify_sig, current_entry.get("signature", "")):
            is_tamper_proof = False
            print(f"ZTDIGS: Signature verification FAILED for entry {current_id}")
            return {"status": "FAILED", "reason": f"Signature mismatch for entry {current_id}", "entry_id": current_id, "passed": False}

        # 2. Verify chaining hash for subsequent entries
        if i > 0:
            previous_entry = entries[i-1]
            # Create a hashable representation of the *previous* document
            temp_prev_doc = previous_entry.copy()
            temp_prev_doc.pop("_id", None) 
            if 'data_payload' in temp_prev_doc and isinstance(temp_prev_doc['data_payload'], dict):
                if '_id' in temp_prev_doc['data_payload'] and isinstance(temp_prev_doc['data_payload']['_id'], ObjectId):
                    temp_prev_doc['data_payload']['_id'] = str(temp_prev_doc['data_payload']['_id'])
            
            recalculated_hash = calculate_data_hash(temp_prev_doc)

            if recalculated_hash != current_entry.get("previous_log_hash"):
                is_tamper_proof = False
                print(f"ZTDIGS: Chaining hash mismatch detected at entry {current_id}")
                return {"status": "FAILED", "reason": f"Chaining hash mismatch at entry {current_id}", "entry_id": current_id, "recalculated_hash": recalculated_hash, "expected_hash": current_entry.get("previous_log_hash"), "passed": False}

    return {"status": "PASSED", "message": "All provenance log entries verified successfully.", "passed": True}

def check_duplicate_claim(ticket_id: str, event_type: str = "invoice_issued", time_window_seconds: int = 86400) -> Dict[str, Any]:
    """
    Checks for duplicate claims (e.g., invoices) for a given ticket within a time window.
    This is a basic anti-fraud guardrail.
    """
    db = get_mongo_db_connection()
    provenance_collection = db["provenance_log"]

    # Find existing events of the specified type for the given ticket_id
    current_time = time.time()
    query_filter = {
        "ticket_id": ticket_id,
        "event_type": event_type,
        "timestamp": {"$gt": current_time - time_window_seconds} # Events within the last X seconds
    }
    
    count = provenance_collection.count_documents(query_filter)
    
    if count > 1:
        return {"is_duplicate": True, "message": f"More than one '{event_type}' event found for ticket {ticket_id} within the last {time_window_seconds} seconds.", "count": count}
    return {"is_duplicate": False, "message": "No duplicate claims detected.", "count": count}