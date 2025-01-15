from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Any
from app.services.tools_service import ToolsService
from app.services.agent_service import AgentService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Get services
def get_tools_service():
    return ToolsService()

def get_agent_service():
    return AgentService()

class ToolCreate(BaseModel):
    description: str
    created_by: str
    code: str = None

class ToolFromCode(BaseModel):
    name: str
    code: str
    created_by: str

class ToolExecute(BaseModel):
    parameters: Dict[str, Any]

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_tool(
    tool_data: ToolCreate,
    tools_service: ToolsService = Depends(get_tools_service)
):
    """Create a new tool from description using LLM."""
    try:
        if tool_data.code:
            # If code is provided, create tool from code
            tool = await tools_service.create_tool_from_code(
                name=tool_data.description.lower().replace(" ", "_"),
                code=tool_data.code,
                created_by=tool_data.created_by
            )
        else:
            # Otherwise create from description
            tool = await tools_service.create_tool(
                description=tool_data.description,
                created_by=tool_data.created_by
            )
        return {
            "name": tool.name,
            "description": tool.description,
            "created_by": tool.created_by,
            "created_at": tool.created_at.isoformat(),
            "code": tool.code,
            "is_sample": False
        }
    except Exception as e:
        logger.error(f"Error creating tool: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/code", status_code=status.HTTP_201_CREATED)
async def create_tool_from_code(
    tool_data: ToolFromCode,
    tools_service: ToolsService = Depends(get_tools_service)
):
    """Create a new tool from code."""
    try:
        tool = await tools_service.create_tool_from_code(
            name=tool_data.name,
            code=tool_data.code,
            created_by=tool_data.created_by
        )
        return {
            "name": tool.name,
            "description": tool.description,
            "created_by": tool.created_by,
            "created_at": tool.created_at.isoformat(),
            "code": tool.code,
            "is_sample": False
        }
    except Exception as e:
        logger.error(f"Error creating tool from code: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/")
async def list_tools(tools_service: ToolsService = Depends(get_tools_service)):
    """List all available tools."""
    try:
        tools = tools_service.list_tools()
        # Ensure sample tools are marked
        for tool in tools:
            if tool["name"] in ["multiply", "add"]:
                tool["is_sample"] = True
        return tools
    except Exception as e:
        logger.error(f"Error listing tools: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{tool_name}")
async def get_tool(
    tool_name: str,
    tools_service: ToolsService = Depends(get_tools_service)
):
    """Get details of a specific tool."""
    try:
        tool = tools_service.get_tool(tool_name)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool '{tool_name}' not found"
            )
        return {
            "name": tool.name,
            "description": tool.description,
            "created_by": tool.created_by,
            "created_at": tool.created_at.isoformat(),
            "code": tool.code,
            "is_sample": tool_name in ["multiply", "add"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{tool_name}/execute")
async def execute_tool(
    tool_name: str,
    data: ToolExecute,
    tools_service: ToolsService = Depends(get_tools_service)
):
    """Execute a specific tool."""
    try:
        result = tools_service.execute_tool(tool_name, **data.parameters)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error executing tool: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
