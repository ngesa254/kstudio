# API Usage Guide

This guide demonstrates how to use the API endpoints for agents, dynamic tools, and document management.

## Base URL
All endpoints are prefixed with `/api/v1`

## Authentication

Currently, the API does not require authentication. For production deployment, implement appropriate authentication mechanisms.

## Agents

### Create an Agent

```bash
POST /api/v1/agents/
Content-Type: application/json

# Conversational Agent
{
  "name": "Summarizer",
  "description": "An agent that summarizes text",
  "type": "conversational",
  "prompt_template": "Summarize the following text:\n\n{input}\n\nSummary:",
  "configuration": {}
}

# RAG Agent
{
  "name": "Document Assistant",
  "description": "An agent that answers questions about documents",
  "type": "rag",
  "prompt_template": "Context: {context}\nQuestion: {input}\n\nAnswer:",
  "configuration": {
    "collection_name": "my_documents"
  }
}

# Tool-calling Agent
{
  "name": "URL Extractor",
  "description": "An agent that extracts URLs from text",
  "type": "tool_calling",
  "prompt_template": "Tools available:\n{tools}\n\nRequest: {input}",
  "configuration": {
    "tools": [
      {
        "name": "extract_urls",
        "description": "Extracts URLs from text"
      }
    ]
  }
}
```

### List Agents

```bash
GET /api/v1/agents/

# Response
[
  {
    "id": 1,
    "name": "Summarizer",
    "type": "conversational",
    "description": "An agent that summarizes text",
    "status": "active",
    "created_at": "2024-03-17T10:00:00Z"
  }
]
```

### Get Agent Details

```bash
GET /api/v1/agents/{agent_id}

# Response
{
  "id": 1,
  "name": "Summarizer",
  "type": "conversational",
  "description": "An agent that summarizes text",
  "prompt_template": "Summarize the following text:\n\n{input}\n\nSummary:",
  "configuration": {},
  "status": "active",
  "created_at": "2024-03-17T10:00:00Z"
}
```

### Interact with Agent

```bash
POST /api/v1/agents/{agent_id}/interact
Content-Type: application/json

{
  "content": "Your message here"
}

# Response
{
  "agent_id": 1,
  "message": "Agent's response",
  "conversation_id": "123",
  "metadata": {
    "model": "claude-3-opus-20240229",
    "tokens_used": 150
  }
}
```

## Document Management (RAG)

### Upload Document

```bash
POST /api/v1/agents/{agent_id}/documents
Content-Type: multipart/form-data

file: <document_file>
collection_name: "my_documents"

# Response
{
  "success": true,
  "message": "Document processed successfully",
  "collection_name": "my_documents"
}
```

### Delete Collection

```bash
DELETE /api/v1/agents/{agent_id}/documents/{collection_name}

# Response
{
  "success": true,
  "message": "Collection deleted successfully"
}
```

## Dynamic Tools

### Create Tool

```bash
POST /api/v1/tools/
Content-Type: application/json

{
  "description": "A tool that extracts all URLs from a given text",
  "created_by": "user123"
}

# Response
{
  "name": "extract_urls_from_text",
  "description": "A tool that extracts all URLs from a given text",
  "created_by": "user123",
  "created_at": "2024-03-17T10:00:00Z",
  "code": "def run(text: str) -> Dict[str, Any]: ..."
}
```

### List Tools

```bash
GET /api/v1/tools/

# Response
[
  {
    "name": "extract_urls_from_text",
    "description": "A tool that extracts all URLs from a given text",
    "created_by": "user123",
    "created_at": "2024-03-17T10:00:00Z"
  }
]
```

### Execute Tool

```bash
POST /api/v1/tools/{tool_name}/execute
Content-Type: application/json

{
  "parameters": {
    "text": "Check out https://example.com"
  }
}

# Response
{
  "success": true,
  "result": {
    "urls": ["https://example.com"]
  },
  "tool": "extract_urls_from_text",
  "timestamp": "2024-03-17T10:05:00Z"
}
```

## Frontend API Integration

The frontend uses the `api.ts` service to interact with these endpoints:

```typescript
// frontend/app/services/api.ts
export const api = {
  // Agents
  createAgent: (data: AgentCreationData) => 
    fetch('/api/v1/agents/', {...}),
  
  listAgents: () => 
    fetch('/api/v1/agents/'),
  
  interactWithAgent: (agentId: number, content: string) =>
    fetch(`/api/v1/agents/${agentId}/interact`, {...}),

  // Tools  
  createTool: (data: ToolCreationData) =>
    fetch('/api/v1/tools/', {...}),
    
  listTools: () =>
    fetch('/api/v1/tools/'),
    
  // Documents
  uploadDocument: (agentId: number, file: File, collectionName: string) =>
    fetch(`/api/v1/agents/${agentId}/documents`, {...})
}
```

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

Error Response Format:
```json
{
  "detail": "Error message here"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. For production, consider adding rate limiting based on:
- IP address
- API key
- Endpoint-specific limits

## Websocket Support

Real-time chat functionality uses WebSocket connections:

```typescript
const ws = new WebSocket(`ws://localhost:8000/ws/chat/${agentId}`);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  // Handle streaming response
};
```

## Notes

1. All endpoints use trailing slashes
2. JSON is the primary data format
3. Dates are in ISO 8601 format
4. File uploads use multipart/form-data
5. WebSocket is used for streaming responses
