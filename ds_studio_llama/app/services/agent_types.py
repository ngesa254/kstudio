from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
import boto3
import os
from app.core.config import settings
from llama_index.core import VectorStoreIndex, Settings as LlamaSettings, StorageContext, load_index_from_storage
from llama_index.core.prompts import PromptTemplate
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import FunctionCallingAgentWorker, AgentRunner
import logging
import json
from dotenv import load_dotenv
import black
import autopep8
import yapf
import isort
from app.services.tools_service import ToolsService
from llama_index.llms.bedrock_converse import BedrockConverse

# Configure logging
log_file = "/workspaces/kstudio/ds_studio_llama/logs/agent_types_logs.log"
os.makedirs(os.path.dirname(log_file), exist_ok=True)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Get logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Ensure AWS SDK logging is captured
boto3_logger = logging.getLogger('boto3')
boto3_logger.setLevel(logging.INFO)
botocore_logger = logging.getLogger('botocore')
botocore_logger.setLevel(logging.INFO)

class BaseAgent(ABC):
    def __init__(self):
        logger.info("Initializing BaseAgent")
        load_dotenv()
        
        # Initialize AWS session
        logger.info("Setting up AWS session")
        self.session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
            region_name=os.getenv('AWS_REGION')
        )
        
        # Create Bedrock client
        logger.info("Creating Bedrock client")
        self.bedrock = self.session.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION')
        )

        
        
        # Use the correct model ID for AWS Bedrock
        self.model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
        self.max_tokens = 100000

        self.tool_llm=BedrockConverse(
                    model=self.model_id,
                    # NOTE replace with your own AWS credentials
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                    aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
                    region_name=os.getenv('AWS_REGION'),
                )
        
        logger.info(f"Using model: {self.model_id} with max_tokens: {self.max_tokens}")

    def _format_multimodal_message(self, text: str, images: List[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Format a multimodal message for Claude 3."""
        logger.info("Formatting multimodal message")
        content = []
        
        # Add text content
        if text:
            content.append({
                "type": "text",
                "text": text
            })
            logger.info("Added text content to message")
        
        # Add image content
        if images:
            for i, img in enumerate(images):
                if img["type"] == "image" and img["data"]:
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": img["data"]
                        }
                    })
            logger.info(f"Added {len(images)} images to message")
        
        return content

    async def _get_completion(self, content: Union[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Get completion from Claude via AWS Bedrock."""
        try:
            # Format content for the request
            if isinstance(content, str):
                logger.info("Formatting text-only message")
                messages = [{
                    "role": "user",
                    "content": [{"type": "text", "text": content}]
                }]
            else:
                logger.info("Formatting multimodal message")
                messages = [{
                    "role": "user",
                    "content": content
                }]

            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "messages": messages
            }
            
            logger.debug(f"Sending request to Bedrock with content type: {'multimodal' if isinstance(content, list) else 'text'}")
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            logger.debug(f"Received response: {json.dumps(response_body, indent=2)}")
            
            return {
                "response": response_body['content'][0]['text'],
                "metadata": {"model": self.model_id}
            }
        except Exception as e:
            logger.error(f"Error getting completion: {str(e)}")
            raise

    @abstractmethod
    async def process(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        pass

class CodingAgent(BaseAgent):
    def _format_code(self, code: str, language: str) -> str:
        """Format code based on language."""
        try:
            if language.lower() == "python":
                # Try black first
                try:
                    return black.format_str(code, mode=black.FileMode())
                except:
                    # Fall back to autopep8
                    try:
                        return autopep8.fix_code(code)
                    except:
                        # Last resort: yapf
                        try:
                            return yapf.yapf_api.FormatCode(code)[0]
                        except:
                            return code
            # Add more language formatters here
            return code
        except Exception as e:
            logger.error(f"Error formatting code: {str(e)}")
            return code

    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from markdown-style text."""
        blocks = []
        lines = text.split('\n')
        in_block = False
        current_block = []
        
        for line in lines:
            if line.startswith('```'):
                if in_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []
                in_block = not in_block
            elif in_block:
                current_block.append(line)
        
        return blocks

    async def process(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            logger.info("Processing coding prompt")
            if not prompt.strip():
                raise ValueError("Prompt cannot be empty")
            
            language = context.get("language", "python")
            
            # Construct prompt based on request type
            if "error" in prompt.lower():
                formatted_prompt = (
                    f"You are an expert {language} developer helping to troubleshoot code. "
                    f"Please analyze the following error and provide a detailed explanation "
                    f"and solution with corrected code:\n\n{prompt}"
                )
            else:
                formatted_prompt = (
                    f"You are an expert {language} developer. Please write clean, well-documented "
                    f"{language} code in response to the following request. Include comments explaining "
                    f"key parts of the code and best practices used:\n\n{prompt}"
                )
            
            # Get initial response
            response = await self._get_completion(formatted_prompt)
            
            # Extract and format code blocks
            code_blocks = self._extract_code_blocks(response["response"])
            formatted_blocks = []
            
            for block in code_blocks:
                formatted_blocks.append(self._format_code(block, language))
            
            # Update response with formatted code
            response["metadata"]["language"] = language
            response["metadata"]["formatted_code"] = formatted_blocks
            
            return response
        except Exception as e:
            logger.error(f"Coding agent error: {str(e)}")
            raise

class RAGAgent(BaseAgent):
    def __init__(self):
        logger.info("Initializing RAGAgent")
        super().__init__()
        model_path = "/Users/hmwangila/Documents/Documents/datascience_projects/2024/ds_studio_llama/ds_studio_llama/all-MiniLM-L6-v2"
        self.embed_model = HuggingFaceEmbedding(
            model_name=model_path,
            trust_remote_code=True
        )
        LlamaSettings.embed_model = self.embed_model
        logger.info("Embedding model initialized")

        # Customize prompt template for better responses
        self.qa_prompt_tmpl = PromptTemplate(
            template=(
                "Here are relevant excerpts and/or images from the document:\n"
                "---------------------\n"
                "{context_str}\n"
                "---------------------\n"
                "Based on these excerpts and images, please provide a detailed answer to the following question. "
                "If the answer cannot be found in the provided content, say 'I don't have enough information to answer that question.'\n"
                "Question: {query_str}\n"
                "Answer: "
            )
        )
        logger.info("Prompt template configured")

    def _load_index(self, collection_path: str) -> Optional[VectorStoreIndex]:
        """Load the vector store index from the given path."""
        try:
            if not os.path.exists(collection_path):
                logger.warning(f"Collection path does not exist: {collection_path}")
                return None

            logger.info(f"Loading index from: {collection_path}")
            storage_context = StorageContext.from_defaults(persist_dir=collection_path)
            index = load_index_from_storage(storage_context)
            logger.info("Successfully loaded index")
            return index
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            return None

    async def process(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a query using the RAG system."""
        try:
            collection_name = context.get("collection_name", "default")
            collection_path = os.path.join(settings.VECTOR_STORE_PATH, collection_name)
            logger.info(f"Processing query for collection: {collection_path}")
            
            # Load the index
            index = self._load_index(collection_path)
            if not index:
                logger.warning("No index found")
                return {
                    "response": "Please upload a document first. I need a document to answer questions from.",
                    "metadata": {"model": self.model_id}
                }
            
            try:
                # Create query engine with custom prompt
                logger.info("Creating query engine")
                query_engine = index.as_query_engine(
                    similarity_top_k=3,  # Get top 3 most relevant chunks
                    response_mode="compact"  # Get concise responses
                )
                query_engine.update_prompts(
                    {"response_synthesizer:text_qa_template": self.qa_prompt_tmpl}
                )
                
                # Get response
                logger.info(f"Querying index with prompt: {prompt}")
                response = query_engine.query(prompt)
                logger.debug(f"Query response: {response}")
                
                if not response or not response.response:
                    logger.warning("No response from query engine")
                    return {
                        "response": "I couldn't find any relevant information in the uploaded document. Please try rephrasing your question or upload a different document.",
                        "metadata": {"model": self.model_id}
                    }
                
                # Collect text and images from source nodes
                text_content = []
                images = []
                
                if hasattr(response, 'source_nodes'):
                    logger.info("Processing source nodes")
                    for i, node in enumerate(response.source_nodes, 1):
                        # Add text content
                        excerpt = node.text[:500] + "..." if len(node.text) > 500 else node.text
                        text_content.append(f"[{i}] {excerpt}")
                        
                        # Add images if available
                        if hasattr(node, 'metadata') and 'images' in node.metadata:
                            images.extend(node.metadata['images'])
                            logger.info(f"Added {len(node.metadata['images'])} images from node {i}")
                
                # Format text content
                formatted_text = "Here are the relevant excerpts I found:\n\n" + "\n\n".join(text_content)
                formatted_text += f"\n\nBased on these excerpts, please answer: {prompt}"
                
                # Get multimodal response from Claude 3
                logger.info("Getting multimodal response from Claude 3")
                multimodal_content = self._format_multimodal_message(formatted_text, images)
                response = await self._get_completion(multimodal_content)
                
                # Add source information to metadata
                response["metadata"]["sources"] = [{
                    "text": node.text,
                    "score": node.score if hasattr(node, 'score') else None,
                    "has_images": bool(node.metadata.get("images")) if hasattr(node, "metadata") else False
                } for node in response.source_nodes] if hasattr(response, 'source_nodes') else []
                
                logger.info("Successfully processed query")
                return response
                
            except Exception as e:
                logger.error(f"Error querying index: {str(e)}")
                raise ValueError(f"Failed to query document: {str(e)}")
            
        except Exception as e:
            logger.error(f"RAG agent error: {str(e)}", exc_info=True)
            raise

class ConversationalAgent(BaseAgent):
    async def process(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            logger.info("Processing conversational prompt")
            if not prompt.strip():
                raise ValueError("Prompt cannot be empty")
                
            # Use default prompt if no template is provided
            if context and "prompt_template" in context:
                formatted_prompt = context["prompt_template"].format(input=prompt)
            else:
                formatted_prompt = (
                    "You are a helpful AI assistant. Please respond to the following message:\n\n"
                    f"{prompt}"
                )
            
            logger.info(f"Using formatted prompt: {formatted_prompt}")
            return await self._get_completion(formatted_prompt)
        except Exception as e:
            logger.error(f"Conversational agent error: {str(e)}")
            raise

class ToolCallingAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.tools_service = ToolsService()
        logger.info("ToolCallingAgent initialized with ToolsService")

    def _get_function_tools(self, tool_names: List[str] = None) -> List[FunctionTool]:
        """Get FunctionTools for the specified tools or all tools if none specified."""
        try:
            tools = []
            available_tools = self.tools_service.list_tools()
            logger.info(f"Available tools: {[t['name'] for t in available_tools]}")
            
            # If no specific tools requested, include sample tools by default
            if not tool_names:
                tool_names = ['multiply', 'add']
                logger.info(f"No tools specified, using sample tools: {tool_names}")
            
            for tool_info in available_tools:
                if tool_names is None or tool_info["name"] in tool_names:
                    tool = self.tools_service.get_tool(tool_info["name"])
                    if tool:
                        logger.info(f"Adding tool: {tool.name}")
                        tools.append(tool.to_function_tool())
                    else:
                        logger.warning(f"Tool not found: {tool_info['name']}")
            
            if not tools:
                logger.warning("No tools were loaded")
                # Ensure sample tools are always available
                multiply_tool = self.tools_service.get_tool('multiply')
                add_tool = self.tools_service.get_tool('add')
                if multiply_tool:
                    tools.append(multiply_tool.to_function_tool())
                if add_tool:
                    tools.append(add_tool.to_function_tool())
                logger.info(f"Added sample tools. Total tools: {len(tools)}")
            
            return tools
        except Exception as e:
            logger.error(f"Error getting function tools: {str(e)}")
            raise

    async def process(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            logger.info("Processing tool-calling prompt")
            context = context or {}
            
            # Get tools from context or use sample tools
            tool_names = context.get("configuration", {}).get("tools")
            logger.info(f"Requested tools: {tool_names}")
            
            function_tools = self._get_function_tools(tool_names)
            
            if not function_tools:
                logger.warning("No tools available")
                return {
                    "response": "No tools are available. Please create some tools first.",
                    "metadata": {"model": self.model_id}
                }
            logger.info(f"Using tools: {[tool for tool in function_tools]}")
            # logger.info(f"Using tools: {[tool.name for tool in function_tools]}")
            
            # Create agent worker with tools
            agent_worker = FunctionCallingAgentWorker.from_tools(
                function_tools,
                llm=self.tool_llm,  # Use Bedrock LLM
                verbose=True,
                allow_parallel_tool_calls=False,
            )
            
            # Create agent runner
            agent = AgentRunner(agent_worker)
            
            # Run agent
            response = agent.chat(prompt)
            
            # Format response with tool execution steps
            steps = []
            if hasattr(response, 'sources'):
                for i, step in enumerate(response.sources):
                    steps.append({
                        'step': i + 1,
                        'tool': step.tool_name,
                        'input': step.raw_input,
                        'output': step.content
                    })
                    logger.info(f"Step {i+1}: Used tool {step.tool_name}")
            
            return {
                "response": f'Using the steps {steps}, {response.response}',
                "metadata": {
                    "model": self.model_id,
                    # "tools_used": [tool for tool in function_tools],
                    "execution_steps": steps
                }
            }
            
        except Exception as e:
            logger.error(f"Tool-calling agent error: {str(e)}")
            raise

class AgentFactory:
    @staticmethod
    def create_agent(agent_type: str) -> BaseAgent:
        logger.info(f"Creating agent of type: {agent_type}")
        
        agents = {
            "RAG": RAGAgent,
            "CONVERSATIONAL": ConversationalAgent,
            "TOOL_CALLING": ToolCallingAgent,
            "CODING": CodingAgent
        }
        
        agent_class = agents.get(agent_type)
        if not agent_class:
            logger.error(f"Unsupported agent type: {agent_type}")
            raise ValueError(f"Unsupported agent type: {agent_type}")
        
        return agent_class()
    