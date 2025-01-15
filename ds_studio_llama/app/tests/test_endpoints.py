import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
import os

client = TestClient(app)
API_PREFIX = settings.API_V1_STR

def test_conversational_agent_workflow():
    # Create conversational agent
    response = client.post(
        f"{API_PREFIX}/agents/",
        json={
            "name": "Summarizer",
            "description": "An agent that summarizes text in less than 5 words",
            "type": "conversational",
            "prompt_template": "Summarize the following text in less than 5 words:\n\n{input}\n\nSummary:",
            "configuration": {}
        }
    )
    print("Response:", response.json())  # Debug print
    assert response.status_code == 201
    agent_id = response.json()["id"]
    
    # Test interaction with specific text
    response = client.post(
        f"{API_PREFIX}/agents/{agent_id}/interact/",
        json={
            "content": "Create, deploy, and manage your agents at scale with Letta Cloud. Build production applications backed by agent microservices with REST APIs."
        }
    )
    print("Interaction Response:", response.json())  # Debug print
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "metadata" in data
    print(f"Conversational Agent Response: {data['message']}")

def test_rag_agent_workflow():
    # Create RAG agent
    response = client.post(
        f"{API_PREFIX}/agents/",
        json={
            "name": "QBR Assistant",
            "description": "An agent that provides insights from QBR documents",
            "type": "rag",
            "prompt_template": "Based on the following context, please provide a summary:\n\nContext: {context}\nQuestion: {question}\n\nAnswer:",
            "configuration": {
                "collection_name": "test_collection"
            }
        }
    )
    print("Response:", response.json())  # Debug print
    assert response.status_code == 201
    agent_id = response.json()["id"]
    
    # Test document upload with specific QBR file
    qbr_file_path = "/Users/hmwangila/Documents/Documents/datascience_projects/2024/ds_studio_llama/Q2'25 QBR Pack Presentation Summary 28072024.pdf"
    
    # Check if file exists
    if not os.path.exists(qbr_file_path):
        pytest.skip(f"QBR file not found at {qbr_file_path}")
    
    # Pass the file location in the request
    response = client.post(
        f"{API_PREFIX}/agents/{agent_id}/documents/",
        json={
            "file_path": qbr_file_path,
            "collection_name": "test_collection"
        }
    )
    print("Document Upload Response:", response.json())  # Debug print
    assert response.status_code == 201
    
    # Test interaction
    response = client.post(
        f"{API_PREFIX}/agents/{agent_id}/interact/",
        json={
            "content": "Please provide a summary of the QBR presentation."
        }
    )
    print("Interaction Response:", response.json())  # Debug print
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "metadata" in data
    print(f"RAG Agent Response: {data['message']}")

def test_tool_agent_workflow():
    # Create tool agent
    response = client.post(
        f"{API_PREFIX}/agents/",
        json={
            "name": "Tool Assistant",
            "description": "An agent that uses tools to help with tasks",
            "type": "tool_calling",
            "prompt_template": "You have access to the following tools:\n{tools}\n\nUser request: {input}\n\nPlease select and use the appropriate tool to help with this request.",
            "configuration": {
                "tools": [
                    {
                        "name": "calculator",
                        "description": "Performs mathematical calculations"
                    },
                    {
                        "name": "weather",
                        "description": "Gets current weather information"
                    }
                ]
            }
        }
    )
    print("Response:", response.json())  # Debug print
    assert response.status_code == 201
    agent_id = response.json()["id"]
    
    # Test interaction
    response = client.post(
        f"{API_PREFIX}/agents/{agent_id}/interact/",
        json={
            "content": "What is 25 multiplied by 16?"
        }
    )
    print("Interaction Response:", response.json())  # Debug print
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "metadata" in data
    print(f"Tool Agent Response: {data['message']}")

if __name__ == "__main__":
    pytest.main([__file__])
