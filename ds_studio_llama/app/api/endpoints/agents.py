from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from app.services.agent_service import AgentService
from app.services.document_service import DocumentService
from app.core.config import settings
from app.schemas.agent import AgentCreate, AgentUpdate, Agent, AgentResponse
from app.models.agent import AgentType, AgentStatus
from typing import List, Optional
import os
import logging
import aiofiles

logger = logging.getLogger(__name__)
router = APIRouter()

agent_service = AgentService()
document_service = DocumentService(settings.VECTOR_STORE_PATH)

@router.get("/", response_model=List[Agent])
async def list_agents():
    """List all agents."""
    try:
        agents = agent_service.get_agents()
        # Convert agent types to uppercase before validation
        return [Agent.model_validate({
            **agent.to_dict(),
            'type': agent.to_dict()['type'].upper()
        }) for agent in agents]
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Agent)
async def create_agent(agent: AgentCreate):
    """Create a new agent."""
    try:
        # Convert type to uppercase before validation
        if isinstance(agent.type, str):
            agent.type = agent.type.upper()
        
        # Set default configuration based on agent type
        if agent.type == AgentType.RAG and not agent.configuration:
            agent.configuration = {
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
            }
        elif agent.type == AgentType.CONVERSATIONAL and not agent.configuration:
            agent.configuration = {
                "description": "A general-purpose AI assistant for natural conversations.",
                "prompt_template": (
                    "You are a helpful AI assistant. Please respond to the following message:\n\n"
                    "{input}"
                )
            }
        elif agent.type == AgentType.TOOL_CALLING and not agent.configuration:
            agent.configuration = {
                "description": "An AI assistant that can use external tools and APIs to help accomplish tasks."
            }
        elif agent.type == AgentType.CODING and not agent.configuration:
            agent.configuration = {
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
            }
        
        db_agent = agent_service.create_agent(agent)
        # Convert type to uppercase in response
        return Agent.model_validate({
            **db_agent.to_dict(),
            'type': db_agent.to_dict()['type'].upper()
        })
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{agent_id}/upload")
async def upload_document(agent_id: str, file: UploadFile = File(...)):
    """Upload a document for the agent to process."""
    file_path = None
    try:
        # Check if this is a PowerPoint temp file
        if file.filename.startswith("~$"):
            raise HTTPException(
                status_code=400, 
                detail="Cannot process PowerPoint temporary files. Please close PowerPoint and try again."
            )

        # Get agent to verify it exists and is RAG type
        db_agent = agent_service.get_agent(int(agent_id))
        if not db_agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        if db_agent.type.lower() != AgentType.RAG.value:  # RAG.value is already lowercase from the enum
            raise HTTPException(status_code=400, detail="Only RAG agents can process documents")

        # Check if file format is supported
        _, ext = os.path.splitext(file.filename)
        
        # Update agent configuration if needed
        if not db_agent.configuration or "supported_formats" not in db_agent.configuration:
            db = agent_service.get_db()
            try:
                # Update agent configuration
                db_agent.configuration = {
                    **(db_agent.configuration or {}),
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
                }
                db.add(db_agent)
                db.commit()
                db.refresh(db_agent)
            finally:
                db.close()

        supported_formats = db_agent.configuration.get("supported_formats", [])
        logger.info(f"Checking file extension {ext.lower()} against supported formats: {supported_formats}")
        if ext.lower() not in supported_formats:
            error_msg = f"Unsupported file format. Supported formats: {', '.join(supported_formats)}"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)

        # Create uploads directory if it doesn't exist
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Save uploaded file with agent ID prefix to avoid conflicts
        file_path = os.path.join(settings.UPLOAD_DIR, f"agent_{agent_id}_{file.filename}")
        
        # Clean up any existing PowerPoint temp files
        if ext.lower() in ['.ppt', '.pptx']:
            for temp_file in os.listdir(settings.UPLOAD_DIR):
                if temp_file.startswith("~$"):
                    temp_path = os.path.join(settings.UPLOAD_DIR, temp_file)
                    try:
                        os.remove(temp_path)
                        logger.info(f"Cleaned up PowerPoint temp file: {temp_file}")
                    except Exception as e:
                        logger.warning(f"Failed to clean up temp file {temp_file}: {str(e)}")
        
        # Use aiofiles for async file operations
        async with aiofiles.open(file_path, 'wb') as f:
            # Read file in chunks to handle large files
            while chunk := await file.read(8192):
                await f.write(chunk)
        logger.info(f"Saved uploaded file to {file_path}")

        try:
            # Process document with agent-specific collection name
            await document_service.process_document(file_path, f"agent_{agent_id}")
            logger.info(f"Successfully processed document for agent {agent_id}")
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

        return {"message": "Document processed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        # Clean up uploaded file only if it exists and is not a PowerPoint file
        if file_path and os.path.exists(file_path):
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in ['.ppt', '.pptx']:
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")

@router.post("/{agent_id}/query", response_model=AgentResponse)
async def query_agent(
    agent_id: str, 
    query: str = Form(...),
    language: Optional[str] = Form(None),
    mode: Optional[str] = Form(None)
):
    """Query the agent with a prompt."""
    try:
        # Get agent to verify it exists
        db_agent = agent_service.get_agent(int(agent_id))
        if not db_agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        # Verify agent is active
        if db_agent.status != AgentStatus.ACTIVE:
            raise HTTPException(status_code=400, detail=f"Agent {agent_id} is not active")

        # Add context for coding agent
        additional_context = {}
        if db_agent.type == AgentType.CODING:
            if not language:
                language = "python"  # Default to Python
            if not mode:
                mode = "generate"  # Default to code generation
            
            # Verify language is supported
            supported_languages = db_agent.configuration.get("supported_languages", [])
            if language not in supported_languages:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported language. Supported languages: {', '.join(supported_languages)}"
                )
            
            # Get prompt template based on mode
            prompt_templates = db_agent.configuration.get("prompt_templates", {})
            template = prompt_templates.get(mode)
            if template:
                query = template.format(language=language, input=query)
            
            additional_context = {
                "language": language,
                "mode": mode
            }

        response = await agent_service.query_agent(agent_id, query, additional_context)
        return AgentResponse(
            response=response["response"],
            metadata=response.get("metadata")
        )
    except Exception as e:
        logger.error(f"Error querying agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent and its associated data."""
    try:
        # Delete agent from database
        success = agent_service.delete_agent(int(agent_id))
        if not success:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        # Delete associated vector store collection
        await document_service.delete_collection(f"agent_{agent_id}")
        
        # Clean up any remaining files in uploads directory
        for file in os.listdir(settings.UPLOAD_DIR):
            if file.startswith(f"agent_{agent_id}_") or file.startswith("~$"):
                try:
                    os.remove(os.path.join(settings.UPLOAD_DIR, file))
                    logger.info(f"Cleaned up file: {file}")
                except Exception as e:
                    logger.warning(f"Failed to clean up file {file}: {str(e)}")
                
        return {"message": "Agent deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
