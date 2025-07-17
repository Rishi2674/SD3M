# main.py
from fastapi import FastAPI, HTTPException, Body, Query, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import time

# Import all logic modules
from db.db import  close_mongo_db_connection, get_mongo_db_connection
from services.gars.gars_core import register_agent, query_agents, get_all_capabilities, add_sample_agents
from services.issue_mapping_agent.map_issue import map_issue as map_issue_llm
from services.ztdigs.core import generate_and_store_contract, get_data_contract, log_provenance_event, verify_provenance_chain, check_duplicate_claim, create_data_contract_doc, create_provenance_log_entry_data
# from services. import submit_feedback_db, get_observability_metrics_db, get_agent_trust_scores_db
from services.rsps.main  import plan_and_submit_ticket # The main integrated planning function


app = FastAPI(
    title="S3DM Monolith API",
    description="Centralized API for Smart Home Device Maintenance (Fellowship of the Cogs).",
    version="1.0.0"
)
app.mount("/ui", StaticFiles(directory="services/ui-ds/cisc/build", html=True), name="static_ui")

# --- Application Lifecycle Events ---
@app.on_event("startup")
async def startup_event():
    print("App: Starting up S3DM Monolith...")
    # Initialize DB connection
    get_mongo_db_connection()
    # Add sample agents to GARS (will only add if not present)
    add_sample_agents()
    # Initialize LLM (downloads model if not present)
    # get_llm_generator()
    print("App: S3DM Monolith started.")

@app.on_event("shutdown")
async def shutdown_event():
    print("App: Shutting down S3DM Monolith...")
    close_mongo_db_connection()
    print("App: S3DM Monolith shut down.")

# --- Pydantic Models (Re-defining for FastAPI API endpoints) ---

# GARS Models
class AgentInput(BaseModel):
    name: str = Field(..., min_length=3)
    capabilities: List[str] = Field(..., min_items=1)
    jurisdiction_country: str
    jurisdiction_city: str
    cost: int = Field(..., ge=0)
    trust_score: int = Field(5, ge=1, le=10)
    active: int = Field(1, ge=0, le=1)
    compliant_regions: List[str] = Field(default_factory=list) # New field

class AgentOutput(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    capabilities: List[str]
    jurisdiction_country: str
    jurisdiction_city: str
    cost: int
    trust_score: int
    active: int
    compliant_regions: List[str]
    created_at: float

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {object: str}

# Issue Mapping Models (for API response)
class UserMessageInput(BaseModel):
    user_message: str
    user_location: str = "Bengaluru, India"

class MappedIssueOutput(BaseModel):
    original_query: str
    issue_type: str
    device_type: str
    severity: str
    llm_raw_output: str

# ZTDIGS Models (for API)
class DataContractInput(BaseModel):
    ticket_id: str
    parties_involved: List[Dict[str, str]]
    data_elements_allowed: List[str]
    purpose: str
    expiry_timestamp: float
    jurisdiction_rules_applied: List[str]

class DataContractOutput(DataContractInput):
    id: str = Field(..., alias="_id")
    policy_hash: str
    created_at: float

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {object: str}

class ProvenanceLogInput(BaseModel):
    ticket_id: str
    agent_id: str
    event_type: str
    details: str
    data_payload: Dict[str, Any]
    contract_id: Optional[str] = None

class ProvenanceLogOutput(ProvenanceLogInput):
    id: str = Field(..., alias="_id")
    timestamp: float
    previous_log_hash: Optional[str] = None
    signature: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {object: str}

# Removed LLOS Models
# class FeedbackInput(BaseModel):
#     ticket_id: str
#     rating: int = Field(..., ge=1, le=5)
#     comments: Optional[str] = None
#     fraud_flag: bool = False

# class FeedbackOutput(FeedbackInput):
#     id: str = Field(..., alias="_id")
#     timestamp: float

#     class Config:
#         populate_by_name = True
#         arbitrary_types_allowed = True
#         json_encoders = {ObjectId: str}

class ObservabilityMetricsOutput(BaseModel):
    total_tickets: int = 0  # Defaulting for now as actual metrics might come from ZTDIGS directly
    avg_csat_score: float = 0.0
    fraud_flags_count: int = 0

# Removed AgentTrustScoreOutput
# class AgentTrustScoreOutput(BaseModel):
#     agent_id: str
#     agent_name: str
#     trust_score: float

# RSPS Models (for ticket submission)
class CustomerConstraintsInput(BaseModel):
    budget: Optional[float] = None
    max_hops: Optional[int] = None
    data_stays_in_eu: bool = False

class TicketSubmissionInput(BaseModel):
    user_message: str
    user_location: str = "Bengaluru, India"
    customer_constraints: Optional[Dict[str, Any]] = None
    
class WorkflowStepOutput(BaseModel):
    task_name: str
    capability: str
    description: str
    status: str
    assigned_agent_id: Optional[str] = None
    assigned_agent_name: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    contract_id: Optional[str] = None

class TicketSubmissionOutput(BaseModel):
    id: str = Field(..., alias="_id")
    original_user_message: str
    issue_type: str
    device_type: str
    severity: str
    user_location: str
    status: str
    planned_workflow: List[WorkflowStepOutput]
    current_step_index: int
    created_at: float
    customer_constraints: Optional[Dict[str, Any]] = None
    total_planned_cost: Optional[float] = None
    total_hops: Optional[int] = None

    class Config:
        populate_by_name = True
        object = True
        json_encoders = {object: str}

# --- Health Check ---
# @app.get("/health", summary="Overall API Health Check")
# async def health_check():
#     try:
#         get_mongo_db_connection().admin.command('ping')
#         llm_status = "loaded" if get_llm_generator() else "failed_to_load"
#         return {"status": "ok", "db_status": "connected", "llm_status": llm_status}
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Service or DB connection failed: {e}")

# --- GARS Endpoints ---
@app.post("/gars/agents/register", response_model=AgentOutput, summary="Register a new agent")
async def register_agent_api(agent_data: AgentInput):
    try:
        new_agent = register_agent(agent_data.model_dump())
        return AgentOutput(**new_agent)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to register agent: {e}")

@app.get("/gars/agents/query", response_model=List[AgentOutput], summary="Query agents by capabilities and location")
async def query_agents_api(
    capability: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    required_compliance_region: Optional[str] = Query(None, description="e.g., 'EU-GDPR', 'India-PDPB'")
):
    try:
        agents = query_agents(capability, country, city, required_compliance_region)
        return [AgentOutput(**agent) for agent in agents]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to query agents: {e}")

@app.get("/gars/capabilities", response_model=List[str], summary="Get all unique registered capabilities")
async def get_all_capabilities_api():
    try:
        return get_all_capabilities()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get capabilities: {e}")

# --- Issue Mapping Agent Endpoints ---
@app.post("/ima/map_issue", response_model=MappedIssueOutput, summary="Map user message to structured issue using LLM")
async def map_issue_api(input: UserMessageInput):
    try:
        mapped_data = map_issue_llm(input.user_message, input.user_location)
        return MappedIssueOutput(**mapped_data)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"LLM mapping error: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to map issue: {e}")

# --- ZTDIGS Endpoints ---
@app.post("/ztdigs/contracts/generate", response_model=DataContractOutput, summary="Generate and store a new data-sharing contract")
async def generate_contract_api(contract_data_input: DataContractInput):
    try:
        new_contract = generate_and_store_contract(contract_data_input.model_dump())
        return DataContractOutput(**new_contract)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate contract: {e}")

@app.get("/ztdigs/contracts/{contract_id}", response_model=DataContractOutput, summary="Retrieve a data-sharing contract by ID")
async def get_contract_api(contract_id: str):
    contract = get_data_contract(contract_id)
    if contract:
        return DataContractOutput(**contract)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found.")

@app.post("/ztdigs/provenance/log", response_model=ProvenanceLogOutput, summary="Log a new event to the immutable provenance chain")
async def log_provenance_api(log_input: ProvenanceLogInput):
    try:
        # Create data dict to ensure proper hashing before logging
        log_data_dict = create_provenance_log_entry_data(
            ticket_id=log_input.ticket_id,
            agent_id=log_input.agent_id,
            event_type=log_input.event_type,
            details=log_input.details,
            data_payload=log_input.data_payload,
            contract_id=log_input.contract_id
        )
        logged_event = log_provenance_event(log_data_dict) # This function performs checks internally
        return ProvenanceLogOutput(**logged_event)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Provenance logging error: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to log provenance: {e}")

@app.get("/ztdigs/provenance/verify", response_model=Dict[str, Any], summary="Verify the integrity of the entire provenance chain")
async def verify_provenance_api():
    try:
        return verify_provenance_chain()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to verify provenance: {e}")

@app.get("/ztdigs/claims/check_duplicate", response_model=Dict[str, Any], summary="Check for duplicate claims (e.g., invoices) for a ticket")
async def check_duplicate_claim_api(
    ticket_id: str = Query(..., description="Ticket ID to check for duplicates."),
    event_type: str = Query("invoice_issued", description="Event type to check for duplicates (e.g., 'invoice_issued', 'task_completed')."),
    time_window_seconds: int = Query(86400, description="Time window in seconds to consider for duplicates.")
):
    try:
        return check_duplicate_claim(ticket_id, event_type, time_window_seconds)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to check duplicate claims: {e}")

# Removed LLOS Endpoints
# @app.post("/llos/feedback", response_model=FeedbackOutput, summary="Submit customer feedback for a ticket")
# async def submit_feedback_api(feedback_data: FeedbackInput):
#     try:
#         new_feedback = submit_feedback_db(feedback_data.model_dump())
#         return FeedbackOutput(**new_feedback)
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to submit feedback: {e}")

@app.get("/llos/metrics", response_model=ObservabilityMetricsOutput, summary="Get overall system observability metrics (Simplified from ZTDIGS data)")
async def get_observability_metrics_api():
    # This endpoint will now rely on data available directly via MongoDB for tickets and provenance
    # LLOS logic to update agent trust scores etc. is not present in the app/llos_logic.py provided
    # so we'll just pull simple counts from DB here.
    try:
        db = get_mongo_db_connection()
        tickets_collection = db["tickets"]
        
        # In a full LLOS, feedback would also be here, for now it's not handled.
        # feedback_collection = db["feedback"] 
        
        total_tickets = tickets_collection.count_documents({})
        
        # Placeholder for CSAT and fraud flags as LLOS logic is removed
        # In future, these would come from the full LLOS logic.
        avg_csat_score = 0.0 
        fraud_flags_count = 0 
        
        return ObservabilityMetricsOutput(
            total_tickets=total_tickets,
            avg_csat_score=avg_csat_score,
            fraud_flags_count=fraud_flags_count
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get metrics: {e}")

# Removed AgentTrustScoreOutput endpoint
# @app.get("/llos/agents/trust_scores", response_model=List[AgentTrustScoreOutput], summary="Get trust scores for all agents")
# async def get_agent_trust_scores_api():
#     try:
#         return get_agent_trust_scores_db()
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get agent trust scores: {e}")


# --- RSPS Endpoint (Main Ticket Submission) ---
@app.post("/tickets/submit", response_model=TicketSubmissionOutput, summary="Submit a new smart home device repair ticket and plan its workflow")
async def submit_ticket_api(ticket_input: TicketSubmissionInput):
    try:
        # Call the core planning logic
        # This function internally calls IMA, GARS, ZTDIGS logic
        planned_ticket = plan_and_submit_ticket(
            user_message=ticket_input.user_message,
            user_location=ticket_input.user_location,
            # customer_constraints=ticket_input.customer_constraints.model_dump() if ticket_input.customer_constraints else {}
        )
        return TicketSubmissionOutput(**planned_ticket)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during ticket submission: {e}")