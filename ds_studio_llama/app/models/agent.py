from sqlalchemy import Column, Integer, String, JSON, Enum as SQLEnum
from app.core.database import Base
import enum
import logging

logger = logging.getLogger(__name__)

class AgentType(str, enum.Enum):
    RAG = "rag"
    CONVERSATIONAL = "conversational"
    TOOL_CALLING = "tool_calling"
    CODING = "coding"

    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive lookup"""
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member.value == value:
                    return member
        return None

class AgentStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive lookup"""
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member.value == value:
                    return member
        return None

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String, index=True)  # Store as string to avoid SQLAlchemy enum issues
    status = Column(String, default=AgentStatus.ACTIVE.value)
    configuration = Column(JSON, nullable=True)

    def to_dict(self):
        """Convert agent to dictionary with proper type handling."""
        try:
            return {
                "id": self.id,
                "name": self.name,
                "type": self.type.lower() if self.type else None,
                "status": self.status.lower() if self.status else AgentStatus.ACTIVE.value,
                "configuration": self.configuration or {}
            }
        except Exception as e:
            logger.error(f"Error converting agent to dict: {e}")
            # Provide a safe fallback
            return {
                "id": self.id,
                "name": self.name,
                "type": "conversational",
                "status": "active",
                "configuration": {}
            }

    @classmethod
    def from_dict(cls, data: dict) -> 'Agent':
        """Create agent from dictionary with proper type handling."""
        try:
            # Convert type string to lowercase
            if isinstance(data.get('type'), str):
                agent_type = AgentType(data['type'].lower())  # Validate against enum
                data['type'] = agent_type.value  # Store lowercase string
            
            # Convert status string to lowercase
            if isinstance(data.get('status'), str):
                agent_status = AgentStatus(data['status'].lower())  # Validate against enum
                data['status'] = agent_status.value  # Store lowercase string
            elif 'status' not in data:
                data['status'] = AgentStatus.ACTIVE.value
            
            # Ensure configuration is a dict
            if 'configuration' not in data or data['configuration'] is None:
                data['configuration'] = {}
            
            return cls(**data)
        except Exception as e:
            logger.error(f"Error creating agent from dict: {e}")
            raise ValueError(f"Invalid agent data: {e}")
