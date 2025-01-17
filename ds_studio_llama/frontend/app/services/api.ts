export interface Agent {
  id: number;
  name: string;
  type: 'conversational' | 'rag' | 'tool_calling' | 'coding';
  status: 'active' | 'inactive';
  configuration?: Record<string, any>;
}

export interface Tool {
  name: string;
  description: string;
  created_by: string;
  created_at: string;
  code?: string;
  is_sample?: boolean;
}

export interface CreateToolRequest {
  description: string;
  code?: string;
  created_by: string;
}

export interface CreateToolFromCodeRequest {
  name: string;
  code: string;
  created_by: string;
}

export interface AgentInteractionResponse {
  response: string;
  message: string;
  created_at: string;
  metadata?: Record<string, any>;
}

const API_BASE_URL = 'https://silver-space-succotash-4g7r45pq64rfjv7-8000.app.github.dev';

export const api = {
  // Agent operations
  listAgents,
  createAgent,
  uploadDocument,
  queryAgent,
  deleteAgent,
  interactWithAgent,
  
  // Tool operations
  listTools,
  createTool,
  createToolFromCode,
  getTool,
  deleteTool,
  executeToolDirectly,
};

// Tool-related functions
export async function listTools(): Promise<Tool[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/tools`);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to list tools');
    }

    // Ensure is_sample is properly set for sample tools
    return data.map((tool: Tool) => ({
      ...tool,
      is_sample: tool.is_sample || ['multiply', 'add'].includes(tool.name)
    }));
  } catch (error) {
    console.error('Error listing tools:', error);
    throw error;
  }
}

export async function getTool(name: string): Promise<Tool> {
  try {
    const response = await fetch(`${API_BASE_URL}/tools/${name}`);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to get tool');
    }

    // Ensure is_sample is properly set for sample tools
    return {
      ...data,
      is_sample: data.is_sample || ['multiply', 'add'].includes(data.name)
    };
  } catch (error) {
    console.error('Error getting tool:', error);
    throw error;
  }
}

export async function createTool(request: CreateToolRequest): Promise<Tool> {
  try {
    const response = await fetch(`${API_BASE_URL}/tools`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to create tool');
    }

    return {
      ...data,
      is_sample: false
    };
  } catch (error) {
    console.error('Error creating tool:', error);
    throw error;
  }
}

export async function createToolFromCode(request: CreateToolFromCodeRequest): Promise<Tool> {
  try {
    const response = await fetch(`${API_BASE_URL}/tools/code`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to create tool from code');
    }

    return {
      ...data,
      is_sample: false
    };
  } catch (error) {
    console.error('Error creating tool from code:', error);
    throw error;
  }
}

export async function deleteTool(name: string): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/tools/${name}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || 'Failed to delete tool');
    }
  } catch (error) {
    console.error('Error deleting tool:', error);
    throw error;
  }
}

export async function executeToolDirectly(name: string, params: Record<string, any>): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/tools/${name}/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ parameters: params }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to execute tool');
    }

    return data;
  } catch (error) {
    console.error('Error executing tool:', error);
    throw error;
  }
}

// Agent-related functions
export async function listAgents(): Promise<Agent[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/agents/`);
    console.log('Attempting to connect to:', API_BASE_URL);
    
    console.log('Response status:', response.status);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to list agents');
    }

    // Convert agent types to lowercase
    return data.map((agent: Agent) => ({
      ...agent,
      type: agent.type.toLowerCase() as Agent['type']
    }));
  } catch (error) {
    console.error('Error listing agents:', error);
    throw error;
  }
}

export async function createAgent(agent: Partial<Agent>): Promise<Agent> {
  try {
    // Ensure required fields are present
    if (!agent.name || !agent.type) {
      throw new Error('Agent name and type are required');
    }

    // Set default status if not provided
    const agentData = {
      ...agent,
      status: agent.status || 'active',
      configuration: agent.configuration || {}
    };

    const response = await fetch(`${API_BASE_URL}/agents/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(agentData),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to create agent');
    }

    // Convert agent type to lowercase
    return {
      ...data,
      type: data.type.toLowerCase() as Agent['type']
    };
  } catch (error) {
    console.error('Error creating agent:', error);
    throw error;
  }
}

export async function uploadDocument(agentId: number, file: File) {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/agents/${agentId}/upload`, {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to upload document');
    }

    return data;
  } catch (error) {
    console.error('Error uploading document:', error);
    throw error;
  }
}

export async function queryAgent(
  agentId: number, 
  query: string, 
  context?: Record<string, any>
): Promise<AgentInteractionResponse> {
  try {
    const formData = new FormData();
    formData.append('query', query);
    
    // Add context parameters to formData if provided
    if (context) {
      Object.entries(context).forEach(([key, value]) => {
        formData.append(key, value.toString());
      });
    }

    const response = await fetch(`${API_BASE_URL}/agents/${agentId}/query`, {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to query agent');
    }

    return {
      response: data.response,
      message: query,
      created_at: new Date().toISOString(),
      metadata: data.metadata
    };
  } catch (error) {
    console.error('Error querying agent:', error);
    throw error;
  }
}

export async function deleteAgent(agentId: number) {
  try {
    const response = await fetch(`${API_BASE_URL}/agents/${agentId}`, {
      method: 'DELETE',
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to delete agent');
    }

    return data;
  } catch (error) {
    console.error('Error deleting agent:', error);
    throw error;
  }
}

export async function interactWithAgent(agentId: number, message: string): Promise<AgentInteractionResponse> {
  try {
    const formData = new FormData();
    formData.append('message', message);

    const response = await fetch(`${API_BASE_URL}/agents/${agentId}/interact`, {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to interact with agent');
    }

    return {
      response: data.response,
      message: message,
      created_at: new Date().toISOString(),
      metadata: data.metadata
    };
  } catch (error) {
    console.error('Error interacting with agent:', error);
    throw error;
  }
}
