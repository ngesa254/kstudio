import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
import os
import shutil
import time
import json

client = TestClient(app)
API_PREFIX = settings.API_V1_STR

def setup_module():
    """Setup test environment."""
    # Create tools directory if it doesn't exist
    os.makedirs("db/tools", exist_ok=True)
    
    # Clear the agents database
    if os.path.exists("db/agents.json"):
        with open("db/agents.json", "w") as f:
            json.dump({"agents": []}, f)

def teardown_module():
    """Cleanup test environment."""
    # Remove test tools
    if os.path.exists("db/tools"):
        shutil.rmtree("db/tools")
    
    # Clear the agents database
    if os.path.exists("db/agents.json"):
        with open("db/agents.json", "w") as f:
            json.dump({"agents": []}, f)

def test_create_url_extractor_tool():
    """Test creating a URL extractor tool."""
    response = client.post(
        f"{API_PREFIX}/tools/",
        json={
            "description": "A tool that extracts all URLs from a given text",
            "created_by": "test_user"
        }
    )
    print("Create Tool Response:", response.json())
    assert response.status_code == 201
    data = response.json()
    assert "name" in data
    assert "code" in data
    return data["name"]

def test_list_tools():
    """Test listing available tools."""
    response = client.get(f"{API_PREFIX}/tools/")
    print("List Tools Response:", response.json())
    assert response.status_code == 200
    tools = response.json()
    assert isinstance(tools, list)
    assert len(tools) > 0

def test_get_tool():
    """Test getting a specific tool."""
    # First create a tool
    tool_name = test_create_url_extractor_tool()
    
    # Then get its details
    response = client.get(f"{API_PREFIX}/tools/{tool_name}")
    print("Get Tool Response:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == tool_name
    assert "code" in data

def test_execute_tool():
    """Test executing a tool."""
    # First create a tool
    tool_name = test_create_url_extractor_tool()
    
    # Then execute it
    response = client.post(
        f"{API_PREFIX}/tools/{tool_name}/execute",
        json={
            "parameters": {
                "text": "Check out https://example.com and http://test.com"
            }
        }
    )
    print("Execute Tool Response:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "result" in data

def test_list_available_agents():
    """Test listing available agents."""
    # First create a tool
    tool_name = test_create_url_extractor_tool()
    
    # Create an agent that uses our tool
    agent_data = {
        "name": "URL Extractor Agent",
        "description": "An agent that extracts URLs from text",
        "type": "tool_calling",
        "prompt_template": "You have access to the following tools:\n{tools}\n\nUser request: {input}\n\nPlease select and use the appropriate tool to help with this request.",
        "configuration": {
            "tools": [
                {
                    "name": tool_name,
                    "description": "A tool that extracts all URLs from a given text"
                }
            ]
        }
    }
    
    response = client.post(
        f"{API_PREFIX}/agents/",
        json=agent_data
    )
    print("Create Agent Response:", response.json())
    assert response.status_code == 201
    created_agent = response.json()
    
    # Give the system a moment to process
    time.sleep(1)
    
    # Then list all agents
    response = client.get(f"{API_PREFIX}/tools/agents/available")
    print("List Agents Response:", response.json())
    assert response.status_code == 200
    agents = response.json()
    assert isinstance(agents, list)
    
    # Find our agent by ID
    url_extractor = next(
        (a for a in agents if a["id"] == created_agent["id"]),
        None
    )
    assert url_extractor is not None
    assert url_extractor["name"] == "URL Extractor Agent"
    assert len(url_extractor["tools"]) == 1
    assert url_extractor["tools"][0]["name"] == tool_name

def test_create_and_use_custom_tool():
    """Test creating a custom tool and using it with an agent."""
    # Create a tool
    tool_name = test_create_url_extractor_tool()
    
    # Create an agent that uses the tool
    agent_data = {
        "name": "URL Extractor Agent 2",
        "description": "An agent that extracts URLs from text",
        "type": "tool_calling",
        "prompt_template": "You have access to the following tools:\n{tools}\n\nUser request: {input}\n\nPlease select and use the appropriate tool to help with this request.",
        "configuration": {
            "tools": [
                {
                    "name": tool_name,
                    "description": "A tool that extracts all URLs from a given text"
                }
            ]
        }
    }
    
    response = client.post(
        f"{API_PREFIX}/agents/",
        json=agent_data
    )
    assert response.status_code == 201
    agent_id = response.json()["id"]
    
    # Use the agent
    response = client.post(
        f"{API_PREFIX}/agents/{agent_id}/interact/",
        json={
            "content": "Find all URLs in this text: Check out https://example.com and http://test.com"
        }
    )
    print("Agent Interaction Response:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "metadata" in data

if __name__ == "__main__":
    pytest.main([__file__])
