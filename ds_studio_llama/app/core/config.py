import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base directory is the parent of the app directory
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Directory for temporary file uploads
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    
    # Directory for vector store data
    VECTOR_STORE_PATH: str = os.path.join(BASE_DIR, "vectorstore")
    
    # Database configuration
    DATABASE_URL: str = "sqlite:///" + os.path.join(BASE_DIR, "db", "app.db")
    
    # Ensure directories exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    os.makedirs(os.path.dirname(DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)

settings = Settings()
