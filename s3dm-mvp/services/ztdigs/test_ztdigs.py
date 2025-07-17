# services/ztdigs/test_ztdigs.py
import time
from core import (
    get_mongo_db_connection, close_mongo_db_connection,
    generate_and_store_contract, get_data_contract,
    log_provenance_event, verify_provenance_chain,
    check_duplicate_claim, create_data_contract_doc, create_provenance_log_entry_data,
    calculate_data_hash # For testing
)
from pymongo.errors import ConnectionFailure

def run_ztdigs_tests():
    print("--- Running ZTDIGS Core Tests ---")
    try:
        db = get_mongo_db_connection()
        # Clean collections for a fresh test run (optional, for repeatable tests)
        db["data_contracts"].delete_many({})
        db["provenance_log"].delete_many({})
        print("ZTDIGS: Cleared old test data.")

        # --- Test Data Contract Management ---
        ticket_id_1 = "TKT001"
        agent_id_1 = "AGT001_RepairCo"
        agent_id_2 = "AGT002_Logistics"

        print("\n--- Testing Data Contract Generation ---")
        contract_data_1 = create_data_contract_doc(
            ticket_id=ticket_id_1,
            parties_involved=[{"agent_id": agent_id_1, "role": "Repair"}, {"agent_id": agent_id_2, "role": "Logistics"}],
            data_elements_allowed=["device_id", "part_number", "repair_status"],
            purpose="part_replacement_workflow",
            expiry_timestamp=time.time() + 3600, # Expires in 1 hour
            jurisdiction_rules_applied=["GDPR"] # Example rule
        )
        contract_1 = generate_and_store_contract(contract_data_1)
        print(f"Generated Contract 1: ID={contract_1['id']}, Policy Hash={contract_1['policy_hash']}")

        contract_data_2 = create_data_contract_doc(
            ticket_id="TKT002",
            parties_involved=[{"agent_id": "AGT003_AI", "role": "Diagnostics"}],
            data_elements_allowed=["device_id", "error_code", "diagnostic_log"],
            purpose="initial_diagnostic",
            expiry_timestamp=time.time() + 7200, # Expires in 2 hours
            jurisdiction_rules_applied=["PDPB"] # Example rule
        )
        contract_2 = generate_and_store_contract(contract_data_2)
        print(f"Generated Contract 2: ID={contract_2['id']}, Policy Hash={contract_2['policy_hash']}")

        retrieved_contract = get_data_contract(contract_1['id'])
        print(f"Retrieved Contract 1: {retrieved_contract is not None}, ID={retrieved_contract['id'] if retrieved_contract else 'N/A'}")

        # --- Test Provenance Logging ---
        print("\n--- Testing Provenance Logging ---")
        # Log event 1
        event_data_1 = create_provenance_log_entry_data(
            ticket_id=ticket_id_1,
            agent_id=agent_id_1,
            event_type="task_dispatched",
            details="Repair task dispatched.",
            data_payload={"task_name": "Fix Light", "agent_assigned": agent_id_1},
            contract_id=contract_1['id']
        )
        logged_event_1 = log_provenance_event(event_data_1)
        print(f"Logged Event 1: ID={logged_event_1['id']}, PrevHash={logged_event_1.get('previous_log_hash')[:8] if logged_event_1.get('previous_log_hash') else 'N/A'}")

        # Log event 2 (data shared, implicitly covered by contract 1)
        event_data_2 = create_provenance_log_entry_data(
            ticket_id=ticket_id_1,
            agent_id=agent_id_2, # Logistic agent sharing part info
            event_type="data_shared",
            details="Part number shared.",
            data_payload={"part_number": "XYZ789", "device_id": "DEV001"}, # Fits data_elements_allowed
            contract_id=contract_1['id']
        )
        logged_event_2 = log_provenance_event(event_data_2)
        print(f"Logged Event 2: ID={logged_event_2['id']}, PrevHash={logged_event_2.get('previous_log_hash')[:8] if logged_event_2.get('previous_log_hash') else 'N/A'}")

        # Log event 3 (task completed)
        event_data_3 = create_provenance_log_entry_data(
            ticket_id=ticket_id_1,
            agent_id=agent_id_1,
            event_type="task_completed",
            details="Repair completed.",
            data_payload={"repair_status": "Fixed", "device_id": "DEV001", "report_link": "http://report.com/1"},
            contract_id=contract_1['id'] # Even task completion can be under a contract's scope
        )
        logged_event_3 = log_provenance_event(event_data_3)
        print(f"Logged Event 3: ID={logged_event_3['id']}, PrevHash={logged_event_3.get('previous_log_hash')[:8] if logged_event_3.get('previous_log_hash') else 'N/A'}")
        
        # Test an event with data not explicitly allowed by contract 1 (should log warning)
        event_data_4 = create_provenance_log_entry_data(
            ticket_id=ticket_id_1,
            agent_id=agent_id_1,
            event_type="billing_info_sent",
            details="Billing info sent (contains customer PII).",
            data_payload={"customer_name": "John Doe", "address": "123 Main St", "device_id": "DEV001"},
            contract_id=contract_1['id'] # This contract doesn't explicitly allow PII
        )
        print("\n--- Logging event with potentially disallowed data (expect warning) ---")
        logged_event_4 = log_provenance_event(event_data_4)
        print(f"Logged Event 4 (with potential warning): ID={logged_event_4['id']}")


        # --- Test Provenance Verification ---
        print("\n--- Testing Provenance Chain Verification ---")
        verification_result = verify_provenance_chain()
        print(f"Verification Result: {verification_result['status']}")
        if not verification_result['passed']:
            print(f"Reason: {verification_result.get('reason')}")

        # --- Test Anti-Fraud: Duplicate Claim ---
        print("\n--- Testing Anti-Fraud: Duplicate Claim Detection ---")
        # Log a second invoice event for the same ticket
        event_data_invoice_1 = create_provenance_log_entry_data(
            ticket_id=ticket_id_1,
            agent_id="AGT004_Billing",
            event_type="invoice_issued",
            details="First invoice issued.",
            data_payload={"invoice_amount": 150},
            contract_id=contract_1['id'] # Link to contract
        )
        logged_invoice_1 = log_provenance_event(event_data_invoice_1)
        print(f"Logged Invoice 1: ID={logged_invoice_1['id']}")

        time.sleep(1) # Simulate a slight delay before second claim

        event_data_invoice_2 = create_provenance_log_entry_data(
            ticket_id=ticket_id_1,
            agent_id="AGT004_Billing",
            event_type="invoice_issued",
            details="Second invoice issued for the same ticket.",
            data_payload={"invoice_amount": 150},
            contract_id=contract_1['id'] # Link to contract
        )
        logged_invoice_2 = log_provenance_event(event_data_invoice_2)
        print(f"Logged Invoice 2: ID={logged_invoice_2['id']}")

        duplicate_check = check_duplicate_claim(ticket_id_1, "invoice_issued", time_window_seconds=60) # Check within 60 seconds
        print(f"Duplicate Claim Check for TKT001: {duplicate_check['message']} (Count: {duplicate_check['count']})")
        assert duplicate_check['is_duplicate'] is True, "Duplicate claim not detected!"

        print("\n--- ZTDIGS Core Tests PASSED! ---")

    except ConnectionFailure:
        print("\n--- ZTDIGS Core Tests FAILED! (MongoDB connection issue) ---")
        print("Please ensure your MongoDB Atlas cluster is running and accessible, and your MONGO_URI in .env is correct.")
    except Exception as e:
        print(f"\n--- ZTDIGS Core Tests FAILED unexpectedly! ---")
        print(f"An error occurred: {e}")
    finally:
        close_mongo_db_connection()

if __name__ == "__main__":
    run_ztdigs_tests()