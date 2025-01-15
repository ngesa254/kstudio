from typing import Dict, Any, List, Optional, Callable
import logging
import importlib.util
import sys
from datetime import datetime
import re
import os
import json
import inspect
from llama_index.core.tools import FunctionTool
from llama_index.llms.bedrock_converse import BedrockConverse

logger = logging.getLogger(__name__)

# Sample tools
def multiply(a: int, b: int) -> int:
    """Multiply two integers and returns the result integer"""
    return a * b

def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b

SAMPLE_TOOLS = {
    "multiply": multiply,
    "add": add
}

class DynamicTool:
    def __init__(self, name: str, description: str, code: str, created_by: str):
        self.name = name
        self.description = description
        self.code = code
        self.created_by = created_by
        self.created_at = datetime.utcnow()
        self._function = None

    @classmethod
    def from_function(cls, func: Callable, created_by: str) -> 'DynamicTool':
        """Create a DynamicTool from a Python function"""
        name = func.__name__
        description = func.__doc__ or f"Function {name}"
        code = inspect.getsource(func)
        return cls(name, description, code, created_by)

    def to_function_tool(self) -> FunctionTool:
        """Convert to llama_index FunctionTool"""
        if not self._function:
            self.load()
        return FunctionTool.from_defaults(
            fn=self._function,
            name=self.name,
            description=self.description
        )

    def load(self):
        """Dynamically load the tool's code."""
        try:
            # Create a module spec
            spec = importlib.util.spec_from_loader(
                self.name,
                loader=None,
                origin=f"<dynamic>/{self.name}"
            )
            module = importlib.util.module_from_spec(spec)
            
            # Add required imports to the code
            imports = """
import requests
from bs4 import BeautifulSoup
import json
import re
import math
from datetime import datetime
from typing import Dict, Any, List, Optional
"""
            
            # Execute the code in the module's namespace
            exec(imports + "\n" + self.code, module.__dict__)
            
            # Get the main function
            # For sample tools and custom code, we look for the function name matching the tool name
            self._function = module.__dict__.get(self.name) or module.__dict__.get('run')
            if not self._function:
                raise ValueError("Tool code must define either a function matching the tool name or a 'run' function")
            
        except Exception as e:
            logger.error(f"Error loading tool {self.name}: {str(e)}", exc_info=True)
            raise

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        if not self._function:
            self.load()
        try:
            result = self._function(**kwargs)
            return {
                "success": True,
                "result": result,
                "tool": self.name,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "tool": self.name,
                "timestamp": datetime.utcnow().isoformat()
            }

class ToolsService:
    def __init__(self):
        self.tools: Dict[str, DynamicTool] = {}
        # Load sample tools
        for name, func in SAMPLE_TOOLS.items():
            tool = DynamicTool.from_function(func, created_by="system")
            self.tools[name] = tool
            logger.info(f"Loaded sample tool: {name}")
        # Load custom tools
        self.load_tools()

    def load_tools(self):
        """Load tools from the database."""
        tools_dir = "db/tools"
        os.makedirs(tools_dir, exist_ok=True)
        
        for filename in os.listdir(tools_dir):
            if filename.endswith('.json'):
                with open(os.path.join(tools_dir, filename), 'r') as f:
                    tool_data = json.load(f)
                    # Skip if tool name conflicts with sample tools
                    if tool_data['name'] not in SAMPLE_TOOLS:
                        tool = DynamicTool(
                            name=tool_data['name'],
                            description=tool_data['description'],
                            code=tool_data['code'],
                            created_by=tool_data['created_by']
                        )
                        self.tools[tool.name] = tool
                        logger.info(f"Loaded custom tool: {tool.name}")

    def save_tool(self, tool: DynamicTool):
        """Save a tool to the database."""
        # Don't save sample tools
        if tool.name in SAMPLE_TOOLS:
            return

        tools_dir = "db/tools"
        os.makedirs(tools_dir, exist_ok=True)
        
        tool_data = {
            "name": tool.name,
            "description": tool.description,
            "code": tool.code,
            "created_by": tool.created_by,
            "created_at": tool.created_at.isoformat()
        }
        
        with open(os.path.join(tools_dir, f"{tool.name}.json"), 'w') as f:
            json.dump(tool_data, f, indent=2)
        logger.info(f"Saved tool: {tool.name}")

    async def create_tool_from_code(self, name: str, code: str, created_by: str) -> DynamicTool:
        """Create a new tool from Python code."""
        try:
            # Create and validate tool
            tool = DynamicTool(name, f"Custom tool: {name}", code, created_by)
            tool.load()  # This will validate the code
            
            # Save if validation passes
            self.tools[name] = tool
            self.save_tool(tool)
            logger.info(f"Created tool from code: {name}")
            
            return tool
            
        except Exception as e:
            logger.error(f"Error creating tool from code: {str(e)}", exc_info=True)
            raise

    async def create_tool(self, description: str, created_by: str) -> DynamicTool:
        """Create a new tool from a description."""
        try:
            # Generate tool name from description
            name = re.sub(r'[^a-z0-9_]', '_', description.lower())
            name = re.sub(r'_+', '_', name)
            name = name[:30]  # Limit length
            
            # For testing, create a simple URL extractor tool
            if "url" in description.lower():
                code = """
def run(text: str) -> Dict[str, Any]:
    '''
    Extract URLs from text.
    
    Args:
        text (str): Text containing URLs
    
    Returns:
        Dict containing list of URLs
    '''
    import re
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    return {"urls": urls}
"""
            else:
                code = """
def run(**kwargs) -> Dict[str, Any]:
    '''
    Generic tool.
    
    Args:
        kwargs: Tool parameters
    
    Returns:
        Dict containing results
    '''
    return {"result": "Tool functionality not implemented"}
"""
            
            # Create and save tool
            tool = DynamicTool(name, description, code, created_by)
            
            # Test the tool
            tool.load()  # This will validate the code
            
            # Save if validation passes
            self.tools[name] = tool
            self.save_tool(tool)
            logger.info(f"Created tool from description: {name}")
            
            return tool
            
        except Exception as e:
            logger.error(f"Error creating tool: {str(e)}", exc_info=True)
            raise

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "created_by": tool.created_by,
                "created_at": tool.created_at.isoformat(),
                "is_sample": tool.name in SAMPLE_TOOLS
            }
            for tool in self.tools.values()
        ]

    def get_tool(self, name: str) -> Optional[DynamicTool]:
        """Get a specific tool by name."""
        return self.tools.get(name)

    def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        return tool.execute(**kwargs)
