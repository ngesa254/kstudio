import os
import json
import traceback
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llama_cpp import Llama
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="LLM API Service",
    description="API service for LLM inference using llamadeploy",
    version="1.0.0"
)

# Pydantic models for request/response
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    max_tokens: Optional[int] = 4096
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False

class ChatResponse(BaseModel):
    response: str
    usage: dict

# Initialize Llama model
model_path = os.getenv("MODEL_PATH", "models/llama-2-7b-chat.gguf")
llm = None

try:
    llm = Llama(
        model_path=model_path,
        n_ctx=4096,  # Context window
        n_threads=4   # CPU threads
    )
    logger.info(f"Loaded LLM model from {model_path}")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    logger.error(f"Traceback: {traceback.format_exc()}")

def format_prompt(messages: List[Message]) -> str:
    """Format messages into a prompt for Llama."""
    prompt = ""
    for msg in messages:
        if msg.role == "system":
            prompt += f"System: {msg.content}\n"
        elif msg.role == "user":
            prompt += f"User: {msg.content}\n"
        elif msg.role == "assistant":
            prompt += f"Assistant: {msg.content}\n"
    prompt += "Assistant: "
    return prompt

@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    Generate a chat completion response using Llama.
    """
    if llm is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Format messages into prompt
        prompt = format_prompt(request.messages)

        # Generate response
        output = llm(
            prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stop=["User:", "System:"],  # Stop tokens
            echo=False  # Don't include prompt in output
        )

        return ChatResponse(
            response=output["choices"][0]["text"].strip(),
            usage={
                "prompt_tokens": output["usage"]["prompt_tokens"],
                "completion_tokens": output["usage"]["completion_tokens"],
                "total_tokens": output["usage"]["total_tokens"]
            }
        )

    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    if llm is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model": model_path}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
