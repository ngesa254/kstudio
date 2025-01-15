from fastapi import FastAPI
from app.core.database import Base, engine, SessionLocal
from app.models.agent import Agent, AgentType, AgentStatus

def create_default_agents():
    """Create default agents if they don't exist."""
    db = SessionLocal()
    try:
        # Check if we have any agents
        if db.query(Agent).count() == 0:
            # Create default conversational agent
            conversational = Agent(
                name="General Assistant",
                type=AgentType.CONVERSATIONAL,
                status=AgentStatus.ACTIVE,
                configuration={
                    "description": "A general-purpose AI assistant for natural conversations.",
                    "prompt_template": (
                        "You are a helpful AI assistant. Please respond to the following message:\n\n"
                        "{input}"
                    )
                }
            )
            
            # Create default coding agent
            coding = Agent(
                name="Code Assistant",
                type=AgentType.CODING,
                status=AgentStatus.ACTIVE,
                configuration={
                    "description": "An expert coding assistant that generates clean, formatted code.",
                    "supported_languages": [
                        "python",
                        "javascript",
                        "typescript",
                        "java",
                        "c++",
                        "go",
                        "rust"
                    ],
                    "features": [
                        "Code Generation",
                        "Error Troubleshooting",
                        "Code Explanation",
                        "Best Practices",
                        "Code Review",
                        "Performance Tips"
                    ]
                }
            )
            
            # Create default tool calling agent
            tool_calling = Agent(
                name="Tool Assistant",
                type=AgentType.TOOL_CALLING,
                status=AgentStatus.ACTIVE,
                configuration={
                    "description": "An AI assistant that can use external tools and APIs to help accomplish tasks.",
                    "tools": ["multiply", "add"]  # Default sample tools
                }
            )
            
            db.add(conversational)
            db.add(coding)
            db.add(tool_calling)
            db.commit()
    except Exception as e:
        print(f"Error creating default agents: {e}")
        db.rollback()
    finally:
        db.close()

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Create default agents
    create_default_agents()
    
    # Create FastAPI app
    app = FastAPI(title="DS Studio API")
    
    return app
