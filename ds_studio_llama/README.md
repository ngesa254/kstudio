# DS Studio Llama

A full-stack DIY Agent Builder Platform using llama-agents, FastAPI, and Next.js.

## Project Structure

```
ds_studio_llama/
├── app/                    # Backend (FastAPI)
│   ├── api/               # API endpoints
│   ├── core/              # Core configurations
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   └── services/          # Business logic
├── frontend/              # Frontend (Next.js)
│   ├── app/              
│   │   ├── components/    # React components
│   │   ├── services/     # API services
│   │   └── types/        # TypeScript types
│   └── public/           # Static assets
├── db/                    # Database files
│   └── tools/            # Stored tools
├── uploads/              # Document uploads
└── vectorstore/          # Vector embeddings
```

## Quick Start

1. Install backend dependencies:
```bash
pip install -r requirements.txt
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
```

3. Start the backend server:
```bash
python -m uvicorn app.main:app --reload
```

4. Start the frontend development server:
```bash
cd frontend
npm run dev
```

5. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Features

### 1. Agent Types

- **Conversational Agent**: Basic chat agent with customizable prompt templates
- **RAG Agent**: Document-aware agent with vector storage capabilities
- **Tool-calling Agent**: Agent that can use custom-generated tools

### 2. Frontend Components

- **WelcomeScreen**: Initial landing page with agent creation options
- **AgentCreationForm**: Interface for creating new agents
- **ChatInterface**: Real-time chat interface with agents
- **DocumentUpload**: File upload for RAG agents
- **ToolManager**: Interface for creating and managing tools
- **Sidebar**: Navigation and agent selection
- **CodeBlock**: Code snippet display with syntax highlighting

### 3. Custom Tool Creation

- Natural language tool description
- Automatic code generation using Claude
- Support for common Python packages
- Tool storage and reusability

## API Reference

See [API_USAGE.md](API_USAGE.md) for detailed API documentation.

## Environment Variables

Required environment variables in `.env`:

```
# Backend
DATABASE_URL=sqlite:///./db/app.db
ANTHROPIC_API_KEY=your_anthropic_api_key
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Error Handling

The application includes comprehensive error handling:

### Backend
- HTTP status codes with detailed error messages
- Exception middleware for consistent error responses
- Input validation using Pydantic schemas

### Frontend
- API error handling with user-friendly messages
- Loading states for async operations
- Form validation and error display

## Development

### Backend Development

```bash
# Run tests
pytest app/tests/

# Generate OpenAPI schema
python -m app.main
```

### Frontend Development

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build
```

## Production Deployment

1. Build the frontend:
```bash
cd frontend
npm run build
```

2. Start the production server:
```bash
python run.py
```

The application will serve the frontend static files and API endpoints from a single server.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
