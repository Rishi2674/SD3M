# services/gars/test_gars.py
from services.gars.main import register_agent, query_agents, get_all_capabilities, add_sample_agents, close_mongo_db_connection, create_agent_data
from pymongo.errors import ConnectionFailure

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

if __name__ == "__main__":
    run_gars_tests()