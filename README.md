## Project Structure

- \`.venv/\`: Python virtual environment for local development.
- \`docker-compose.yml\`: Defines and runs the multi-container Docker application.
- \`setup.sh\`: Initial setup script.
- \`services/\`: Contains individual FastAPI microservices:
    - \`gars/\`: Global Agent Registry Service
    - \`rsps/\`: Runtime Swarm Planner Service
    - \`ztdigs/\`: Zero-Trust Data & Identity Guardrails Service
    - \`llos/\`: Learning Loop & Observability Service
    - \`ui-ds/\`: User Interface & Designer Sandbox (Frontend)
- \`db/\`: Persistent volume for PostgreSQL data.

## Getting Started

1.  **Run the setup script**:
    \`\`\`bash
    ./setup.sh
    \`\`\`
    This will create the directory structure, virtual environment, and initial files.

2.  **Activate the virtual environment**:
    \`\`\`bash
    source .venv/bin/activate
    \`\`\`
    (You'll need to do this in each new terminal session if you want to run Python commands locally).

3.  **Install local dependencies (optional, for local development outside Docker)**:
    \`\`\`bash
    pip install -r services/gars/requirements.txt
    pip install -r services/rsps/requirements.txt
    # ... and so on for other services
    \`\`\`

4.  **Build and run the Docker containers**:
    \`\`\`bash
    docker-compose up --build
    \`\`\`
    Add \`-d\` to run in detached mode.

5.  **Access Services**:
    - UI/DS: \`http://localhost:8000\`
    - GARS: \`http://localhost:8001\`
    - RSPS: \`http://localhost:8002\`
    - ZTDIGS: \`http://localhost:8003\`
    - LLOS: \`http://localhost:8004\`
    - RabbitMQ Management: \`http://localhost:15672\` (user: guest, pass: guest)

## Next Steps

-   **Implement API Endpoints**: Start filling out the \`main.py\` files for each service based on the roadmap.
-   **Database Models**: Define SQLAlchemy/SQLModel models for each service's data.
-   **Frontend Development**: Set up a React/Vue project in \`services/ui-ds\` (replace the placeholder \`Dockerfile\` and \`command\` in \`docker-compose.yml\` accordingly).
-   **Add Logic**: Implement the core business logic for each service.
-   **Testing**: Write unit and integration tests.