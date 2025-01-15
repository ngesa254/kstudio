export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  language?: string;
  code?: string[];
  error?: boolean;
}

export type AgentType = 'conversational' | 'rag' | 'tool_calling' | 'coding';

export interface AgentTypeInfo {
  id: AgentType;
  name: string;
  icon: string;
  description: string;
  supportedFormats?: readonly string[];
  supportedLanguages?: readonly string[];
  features?: readonly string[];
}

export interface SelectedTool {
  name: string;
  description: string;
}

export const agentTypes: readonly AgentTypeInfo[] = [
  { 
    id: 'conversational', 
    name: 'Conversational Agent', 
    icon: '💬',
    description: 'General purpose chat agent for natural conversations'
  },
  { 
    id: 'rag', 
    name: 'RAG Agent', 
    icon: '📚',
    description: 'Retrieval-Augmented Generation for document-based Q&A',
    supportedFormats: [
      '.pdf', '.txt', '.doc', '.docx', 
      '.xlsx', '.xls', '.csv',
      '.pptx', '.ppt',
      '.png', '.jpg', '.jpeg', '.gif', '.bmp',
      '.md', '.json'
    ] as const
  },
  { 
    id: 'tool_calling', 
    name: 'Tool Agent', 
    icon: '🛠️',
    description: 'Agent that can use external tools and APIs',
    features: [
      'Sample Tools (multiply, add)',
      'Custom Tool Creation',
      'Python Code Tools',
      'Tool Execution Tracking'
    ] as const
  },
  {
    id: 'coding',
    name: 'Coding Agent',
    icon: '👨‍💻',
    description: 'Expert coding assistant that generates clean, formatted code',
    supportedLanguages: [
      'python',
      'javascript',
      'typescript',
      'java',
      'c++',
      'go',
      'rust'
    ] as const,
    features: [
      'Code Generation',
      'Error Troubleshooting',
      'Code Explanation',
      'Best Practices',
      'Code Review',
      'Performance Tips'
    ] as const
  }
] as const;
