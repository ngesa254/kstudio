import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import agents, tools
from app.services.tools_service import ToolsService
from app.core.init_app import create_app
from app.core.database import Base, engine, SessionLocal
from sqlalchemy import text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables and initialize app
logger.info("Creating database tables...")
Base.metadata.create_all(bind=engine)

# Create tools directory if it doesn't exist
os.makedirs("db/tools", exist_ok=True)

# Create FastAPI app
logger.info("Creating FastAPI app...")
app = create_app()

# Initialize tools service as a global instance
logger.info("Initializing tools service...")
tools_service = ToolsService()

# Make tools service available to endpoints
def get_tools_service():
    return tools_service

# Override the tools service dependency in the tools router
tools.get_tools_service = get_tools_service

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router, prefix="/agents", tags=["agents"])
app.include_router(tools.router, prefix="/tools", tags=["tools"])

# Log available routes
@app.on_event("startup")
async def startup_event():
    logger.info("Available routes:")
    for route in app.routes:
        if hasattr(route, "methods"):
            methods = ", ".join(route.methods)
            logger.info(f"{methods}: {route.path}")
    
    # Log database status
    db = SessionLocal()
    try:
        # Use SQLAlchemy text() for raw SQL
        agent_count = db.execute(text("SELECT COUNT(*) FROM agents")).scalar()
        logger.info(f"Found {agent_count} agents in database")
    except Exception as e:
        logger.error(f"Error checking database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
