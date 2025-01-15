from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.agent import AgentType, AgentStatus
import logging

logger = logging.getLogger(__name__)

class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: AgentType
    status: Optional[AgentStatus] = Field(default=AgentStatus.ACTIVE)
    configuration: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('type', pre=True)
    def validate_type(cls, v):
        """Convert type to uppercase before validation"""
        if isinstance(v, str):
            return v.upper()
        return v

    @validator('configuration')
    def validate_configuration(cls, v, values):
        if v is None:
            v = {}
        
        # Validate configuration based on agent type
        agent_type = values.get('type')
        if agent_type:
            if agent_type == AgentType.RAG:
                v.setdefault('description', "A document-aware AI assistant that can answer questions based on uploaded files.")
                v.setdefault('supported_formats', [
                    ".pdf", ".txt", ".doc", ".docx",
                    ".xlsx", ".xls", ".csv",
                    ".pptx", ".ppt",
                    ".png", ".jpg", ".jpeg", ".gif", ".bmp",
                    ".md", ".json"
                ])
                v.setdefault('embedding_model', "all-MiniLM-L6-v2")
                v.setdefault('max_tokens', 1000)
            
            elif agent_type == AgentType.CONVERSATIONAL:
                v.setdefault('description', "A general-purpose AI assistant for natural conversations.")
                v.setdefault('prompt_template', (
                    "You are a helpful AI assistant. Please respond to the following message:\n\n"
                    "{input}"
                ))
            
            elif agent_type == AgentType.TOOL_CALLING:
                v.setdefault('description', "An AI assistant that can use external tools and APIs to help accomplish tasks.")
                v.setdefault('tools', ["multiply", "add"])  # Default sample tools
            
            elif agent_type == AgentType.CODING:
                v.setdefault('description', "An expert coding assistant that generates clean, formatted code.")
                v.setdefault('supported_languages', [
                    "python",
                    "javascript",
                    "typescript",
                    "java",
                    "c++",
                    "go",
                    "rust"
                ])
                v.setdefault('features', [
                    "Code Generation",
                    "Error Troubleshooting",
                    "Code Explanation",
                    "Best Practices",
                    "Code Review",
                    "Performance Tips"
                ])
        
        return v

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[AgentType] = None
    status: Optional[AgentStatus] = None
    configuration: Optional[Dict[str, Any]] = None

    @validator('type', pre=True)
    def validate_type(cls, v):
        """Convert type to uppercase before validation"""
        if isinstance(v, str):
            return v.upper()
        return v

    @validator('configuration')
    def validate_configuration(cls, v, values):
        if v is None:
            return {}
        return v

class Agent(AgentBase):
    id: int

    class Config:
        from_attributes = True

    @validator('configuration')
    def ensure_configuration(cls, v):
        return v or {}

class TestCase(BaseModel):
    input: str = Field(..., min_length=1)
    expected_output: str = Field(..., min_length=1)

class TestResult(BaseModel):
    test_case: TestCase
    actual_output: str
    passed: bool
    timestamp: datetime = Field(default_factory=datetime.now)

class AgentResponse(BaseModel):
    response: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('metadata')
    def ensure_metadata(cls, v):
        return v or {}
