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
    return {"message": "Hello from ZTDIGS Service!"}

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