import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app
from app.models.agent import AgentType, AgentStatus

# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_agent():
    response = client.post(
        "/api/v1/agents/",
        json={
            "name": "Test RAG Agent",
            "description": "A test RAG agent",
            "type": AgentType.RAG,
            "configuration": {
                "chunk_size": 1000,
                "chunk_overlap": 200
            },
            "prompt_template": "Context: {context}\nQuestion: {question}\nAnswer:"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test RAG Agent"
    assert data["type"] == AgentType.RAG
    assert data["status"] == AgentStatus.DRAFT

def test_get_agent():
    # First create an agent
    create_response = client.post(
        "/api/v1/agents/",
        json={
            "name": "Test Agent",
            "description": "A test agent",
            "type": AgentType.CONVERSATIONAL,
            "configuration": {},
            "prompt_template": "Question: {input}\nAnswer:"
        }
    )
    agent_id = create_response.json()["id"]

    # Then get the agent
    response = client.get(f"/api/v1/agents/{agent_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Agent"
    assert data["type"] == AgentType.CONVERSATIONAL

def test_interact_with_agent():
    # Create a test agent
    create_response = client.post(
        "/api/v1/agents/",
        json={
            "name": "Test Interactive Agent",
            "description": "A test interactive agent",
            "type": AgentType.CONVERSATIONAL,
            "configuration": {},
            "prompt_template": "Question: {input}\nAnswer:"
        }
    )
    agent_id = create_response.json()["id"]

    # Test interaction
    response = client.post(
        f"/api/v1/agents/{agent_id}/interact",
        json={
            "content": "What is 2+2?",
            "metadata": {}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "conversation_id" in data

def test_list_agents():
    # Create multiple agents
    agent_data = [
        {
            "name": f"Test Agent {i}",
            "description": f"Test agent {i}",
            "type": AgentType.CONVERSATIONAL,
            "configuration": {},
            "prompt_template": "Question: {input}\nAnswer:"
        }
        for i in range(3)
    ]
    
    for data in agent_data:
        client.post("/api/v1/agents/", json=data)

    # Test listing agents
    response = client.get("/api/v1/agents/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3

def test_update_agent():
    # Create an agent
    create_response = client.post(
        "/api/v1/agents/",
        json={
            "name": "Test Update Agent",
            "description": "A test agent for updating",
            "type": AgentType.CONVERSATIONAL,
            "configuration": {},
            "prompt_template": "Question: {input}\nAnswer:"
        }
    )
    agent_id = create_response.json()["id"]

    # Update the agent
    update_data = {
        "name": "Updated Agent Name",
        "description": "Updated description"
    }
    response = client.put(f"/api/v1/agents/{agent_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Agent Name"
    assert data["description"] == "Updated description"

def test_delete_agent():
    # Create an agent
    create_response = client.post(
        "/api/v1/agents/",
        json={
            "name": "Test Delete Agent",
            "description": "A test agent for deletion",
            "type": AgentType.CONVERSATIONAL,
            "configuration": {},
            "prompt_template": "Question: {input}\nAnswer:"
        }
    )
    agent_id = create_response.json()["id"]

    # Delete the agent
    response = client.delete(f"/api/v1/agents/{agent_id}")
    assert response.status_code == 204

    # Verify agent is deleted
    get_response = client.get(f"/api/v1/agents/{agent_id}")
    assert get_response.status_code == 404
