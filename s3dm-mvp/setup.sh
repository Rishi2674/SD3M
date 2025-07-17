#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Setting up S3DM MVP Project ---"

# 1. Create main project directory
if [ ! -d "s3dm-mvp" ]; then
    mkdir s3dm-mvp
fi
cd s3dm-mvp

# 2. Create Python virtual environment
echo "Creating Python virtual environment..."
python -m venv .venv
source .venv/bin/activate # Activate it for the current shell

echo "Virtual environment created and activated."

# 3. Create services directory
echo "Creating services directories and initial files..."
mkdir -p services/gars services/rsps services/ztdigs services/llos services/ui-ds db

# 4. Create initial Docker Compose file
cat <<EOF > docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:13
    restart: always
    environment:
      POSTGRES_DB: s3dm_db
      POSTGRES_USER: s3dm_user
      POSTGRES_PASSWORD: s3dm_password
    volumes:
      - ./db:/var/lib/postgresql/data # Persistent data
    ports:
      - "5432:5432" # Expose for local development/debugging

  rabbitmq:
    image: rabbitmq:3-management
    restart: always
    ports:
      - "5672:5672" # AMQP port
      - "15672:15672" # Management UI
    environment:
      RABBITMQ_DEFAULT_USER: user
      RABBITMQ_DEFAULT_PASS: password

  gars:
    build: ./services/gars
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./services/gars:/app
    ports:
      - "8001:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://s3dm_user:s3dm_password@db:5432/s3dm_db

  rsps:
    build: ./services/rsps
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./services/rsps:/app
    ports:
      - "8002:8000"
    depends_on:
      - db
      - rabbitmq
      - gars # RSPS depends on GARS for agent discovery
    environment:
      DATABASE_URL: postgresql://s3dm_user:s3dm_password@db:5432/s3dm_db
      GARS_URL: http://gars:8000 # Internal Docker network URL

  ztdigs:
    build: ./services/ztdigs
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./services/ztdigs:/app
    ports:
      - "8003:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://s3dm_user:s3dm_password@db:5432/s3dm_db

  llos:
    build: ./services/llos
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./services/llos:/app
    ports:
      - "8004:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://s3dm_user:s3dm_password@db:5432/s3dm_db

  ui-ds:
    build: ./services/ui-ds
    # For a simple static file server, you might use Nginx or Python's http.server
    # For React/Vue, you'd run 'npm start' or 'npm run dev'
    command: python3 -m http.server 8000 # Simple placeholder for static files
    volumes:
      - ./services/ui-ds:/app
    ports:
      - "8000:8000" # UI will be on port 8000
    depends_on:
      - gars
      - rsps
      - ztdigs
      - llos
EOF

# 5. Create README.md
cat <<EOF > README.md
# S3DM MVP: Secure Swarm for Smart Home Device Maintenance

This repository contains the basic setup for the Secure Swarm for Smart Home Device Maintenance (S3DM) Minimum Viable Product (MVP).

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
EOF

# 6. Create service-specific files
for service in gars rsps ztdigs llos; do
    echo "Creating files for $service..."
    cat <<EOF > services/$service/Dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

    cat <<EOF > services/$service/requirements.txt
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
EOF
    # Add specific crypto for ZTDIGS
    if [ "$service" == "ztdigs" ]; then
        echo "Adding pycryptodome to ztdigs requirements."
        echo "pycryptodome" >> services/$service/requirements.txt
    fi

    cat <<EOF > services/$service/main.py
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

app = FastAPI()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://s3dm_user:s3dm_password@localhost:5432/s3dm_db")
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define a simple model for demonstration
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)

# Create tables (run this once, e.g., on service startup or as a separate script)
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    print(f"Database tables created for {os.path.basename(os.getcwd())}")

@app.get("/")
async def read_root():
    return {"message": "Hello from $service Service!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Example endpoint to add an item (will be replaced by actual service logic)
@app.post("/items/")
async def create_item(name: str, description: str):
    db = SessionLocal()
    try:
        new_item = Item(name=name, description=description)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return {"message": "Item created", "item_id": new_item.id}
    finally:
        db.close()
EOF
done

# 7. Create placeholder for ui-ds
cat <<EOF > services/ui-ds/Dockerfile
FROM nginx:alpine

COPY . /usr/share/nginx/html

EXPOSE 8000
CMD ["nginx", "-g", "daemon off;"]
EOF

cat <<EOF > services/ui-ds/index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>S3DM UI/DS - Coming Soon!</title>
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f0f2f5; color: #333; }
        .container { text-align: center; padding: 40px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); background-color: #fff; }
        h1 { color: #007bff; }
        p { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>S3DM User Interface & Designer Sandbox</h1>
        <p>This is a placeholder. Frontend development will go here!</p>
        <p>Check the backend services:</p>
        <ul>
            <li><a href="http://localhost:8001/docs" target="_blank">GARS Docs (8001)</a></li>
            <li><a href="http://localhost:8002/docs" target="_blank">RSPS Docs (8002)</a></li>
            <li><a href="http://localhost:8003/docs" target="_blank">ZTDIGS Docs (8003)</a></li>
            <li><a href="http://localhost:8004/docs" target="_blank">LLOS Docs (8004)</a></li>
            <li><a href="http://localhost:15672" target="_blank">RabbitMQ Management (15672)</a></li>
        </ul>
    </div>
</body>
</html>
EOF

cat <<EOF > services/ui-ds/README.md
# UI/DS (User Interface & Designer Sandbox)

This directory is for the frontend application.

**For MVP, it currently serves a placeholder HTML page.**

## Next Steps for Frontend Development:

1.  **Initialize a React/Vue Project**:
    \`\`\`bash
    # Inside this directory (services/ui-ds)
    # For React:
    npx create-react-app .
    # For Vue:
    npm init vue@latest
    \`\`\`
2.  **Update Dockerfile**: Replace the Nginx Dockerfile with one that builds and serves your React/Vue app (e.g., using Node.js for development server, or building static assets for Nginx).
3.  **Update docker-compose.yml**: Adjust the \`command\` for the \`ui-ds\` service to run your frontend development server (e.g., \`npm start\`).
EOF

echo "Initial files created successfully."
echo "--- Setup Complete ---"
echo "To proceed:"
echo "1. Navigate into the project directory: cd s3dm-mvp"
echo "2. Activate the virtual environment (if you open a new terminal): source .venv/bin/activate"
echo "3. Start all services using Docker Compose: docker-compose up --build"
echo "4. Access the UI at http://localhost:8000"
echo "5. Access API docs for other services (e.g., GARS) at http://localhost:8001/docs"