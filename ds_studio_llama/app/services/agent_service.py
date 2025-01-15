from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.agent import Agent, AgentType, AgentStatus
from app.schemas.agent import AgentCreate, AgentUpdate, TestCase, TestResult
from app.services.agent_types import AgentFactory
from app.core.database import SessionLocal
from app.core.config import settings
import os
import logging

logger = logging.getLogger(__name__)

class AgentService:
    def __init__(self):
        self.agent_factory = AgentFactory()

    def get_db(self) -> Session:
        return SessionLocal()

    def _ensure_vector_store_exists(self, agent_id: str) -> None:
        """Ensure vector store directory exists for the agent."""
        vector_store_path = os.path.join(settings.VECTOR_STORE_PATH, f"agent_{agent_id}")
        os.makedirs(vector_store_path, exist_ok=True)

    def create_agent(self, agent: AgentCreate) -> Agent:
        """Create a new agent with proper initialization."""
        db = self.get_db()
        try:
            # Create agent in database
            db_agent = Agent(
                name=agent.name,
                type=agent.type,
                status=agent.status or AgentStatus.ACTIVE,
                configuration=agent.configuration or {}
            )
            db.add(db_agent)
            db.commit()
            db.refresh(db_agent)

            # Initialize configuration if not provided
            if not db_agent.configuration:
                db_agent.configuration = {}

            # Add description based on agent type
            if agent.type == AgentType.RAG:
                db_agent.configuration.update({
                    "description": "A document-aware AI assistant that can answer questions based on uploaded files.",
                    "supported_formats": [
                    ".pdf", ".txt", ".doc", ".docx",
                    ".xlsx", ".xls", ".csv",
                    ".pptx", ".ppt",
                    ".png", ".jpg", ".jpeg", ".gif", ".bmp",
                    ".md", ".json"
                    ],
                    "embedding_model": "all-MiniLM-L6-v2",
                    "max_tokens": 1000
                })
                self._ensure_vector_store_exists(str(db_agent.id))
            
            elif agent.type == AgentType.CONVERSATIONAL:
                db_agent.configuration.update({
                    "description": "A general-purpose AI assistant called kazuri for natural conversations.",
                    "prompt_template": (
                        "You are a helpful AI assistant called kazuri. Please respond to the following message:\n\n"
                        "{input}"
                    )
                })
            
            elif agent.type == AgentType.TOOL_CALLING:
                db_agent.configuration.update({
                    "description": "An AI assistant that can use external tools and APIs to help accomplish tasks."
                })
            
            elif agent.type == AgentType.CODING:
                db_agent.configuration.update({
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
                    ],
                    "formatters": {
                        "python": ["black", "autopep8", "yapf"],
                        "javascript": ["prettier"],
                        "typescript": ["prettier"],
                        "java": ["google-java-format"],
                        "c++": ["clang-format"],
                        "go": ["gofmt"],
                        "rust": ["rustfmt"]
                    },
                    "prompt_templates": {
                        "generate": (
                            "You are an expert {language} developer. Please write clean, well-documented "
                            "{language} code in response to the following request. Include comments explaining "
                            "key parts of the code and best practices used:\n\n{input}"
                        ),
                        "troubleshoot": (
                            "You are an expert {language} developer helping to troubleshoot code. "
                            "Please analyze the following error and provide a detailed explanation "
                            "and solution with corrected code:\n\n{input}"
                        ),
                        "explain": (
                            "You are an expert {language} developer. Please analyze the following code "
                            "and provide a detailed explanation of how it works, including best practices "
                            "and potential improvements:\n\n{input}"
                        )
                    }
                })

            db.commit()
            db.refresh(db_agent)
            return db_agent
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()

    def get_agent(self, agent_id: int) -> Optional[Agent]:
        """Get agent by ID."""
        db = self.get_db()
        try:
            return db.query(Agent).filter(Agent.id == agent_id).first()
        finally:
            db.close()

    def get_agents(self) -> List[Agent]:
        """Get all agents."""
        db = self.get_db()
        try:
            return db.query(Agent).all()
        finally:
            db.close()

    def update_agent(self, agent_id: int, agent_update: AgentUpdate) -> Optional[Agent]:
        """Update agent with proper reconfiguration."""
        db = self.get_db()
        try:
            db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
            if not db_agent:
                return None

            update_data = agent_update.dict(exclude_unset=True)
            
            # If changing to RAG type, ensure vector store exists
            if "type" in update_data and update_data["type"] == AgentType.RAG:
                self._ensure_vector_store_exists(str(agent_id))

            # Update fields
            for field, value in update_data.items():
                setattr(db_agent, field, value)

            db.commit()
            db.refresh(db_agent)
            return db_agent
        except Exception as e:
            logger.error(f"Error updating agent: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()

    def delete_agent(self, agent_id: int) -> bool:
        """Delete agent and clean up resources."""
        db = self.get_db()
        try:
            db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
            if not db_agent:
                return False

            # Clean up vector store if RAG agent
            if db_agent.type == AgentType.RAG:
                vector_store_path = os.path.join(settings.VECTOR_STORE_PATH, f"agent_{agent_id}")
                if os.path.exists(vector_store_path):
                    import shutil
                    shutil.rmtree(vector_store_path)

            db.delete(db_agent)
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting agent: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()

    async def query_agent(self, agent_id: str, query: str, additional_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Query an agent with proper error handling."""
        try:
            # Get agent from database
            db_agent = self.get_agent(int(agent_id))
            if not db_agent:
                raise ValueError(f"Agent {agent_id} not found")

            # Verify agent is active
            if db_agent.status != AgentStatus.ACTIVE:
                raise ValueError(f"Agent {agent_id} is not active")

            # Create appropriate agent instance
            agent = self.agent_factory.create_agent(db_agent.type)

            # Process query with context
            context = {
                "collection_name": f"agent_{agent_id}",
                "configuration": db_agent.configuration
            }
            
            # Add prompt template if available
            if db_agent.configuration and "prompt_template" in db_agent.configuration:
                context["prompt_template"] = db_agent.configuration["prompt_template"]
            
            # Add any additional context
            if additional_context:
                context.update(additional_context)
            
            response = await agent.process(query, context)
            
            # Add agent info to response metadata
            if "metadata" not in response:
                response["metadata"] = {}
            response["metadata"]["agent_id"] = agent_id
            response["metadata"]["agent_type"] = db_agent.type
            
            return response

        except Exception as e:
            logger.error(f"Error querying agent: {str(e)}", exc_info=True)
            raise
