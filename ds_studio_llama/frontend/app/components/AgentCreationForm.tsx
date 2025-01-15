'use client';

import { AgentType, SelectedTool, agentTypes } from '../types';
import { Tool } from '../services/api';
import ToolManager from './ToolManager';

interface AgentCreationFormProps {
  newAgent: {
    name: string;
    type: AgentType;
    configuration: Record<string, any>;
  };
  selectedTools: SelectedTool[];
  showToolManager: boolean;
  isLoading: boolean;
  onAgentChange: (agent: { name: string; type: AgentType; configuration: Record<string, any> }) => void;
  onToolsChange: (tools: SelectedTool[]) => void;
  onShowToolManagerChange: (show: boolean) => void;
  onCancel: () => void;
  onSubmit: () => void;
}

export function AgentCreationForm({
  newAgent,
  selectedTools,
  showToolManager,
  isLoading,
  onAgentChange,
  onToolsChange,
  onShowToolManagerChange,
  onCancel,
  onSubmit
}: AgentCreationFormProps) {
  const removeSelectedTool = (toolName: string) => {
    onToolsChange(selectedTools.filter(t => t.name !== toolName));
  };

  const handleTypeChange = (type: AgentType) => {
    // Reset configuration when changing type
    const defaultConfig = type === 'conversational' ? {
      prompt_template: "You are a helpful AI assistant. Please respond to the following message:\n\n{input}"
    } : {};

    onAgentChange({
      ...newAgent,
      type,
      configuration: defaultConfig
    });

    if (type === 'tool_calling') {
      onShowToolManagerChange(true);
    } else {
      onShowToolManagerChange(false);
      onToolsChange([]);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      {showToolManager && newAgent.type === 'tool_calling' ? (
        // Tool Manager View
        <div className="bg-[#2D2D30] rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-white font-medium">Manage Tools</h3>
            <button
              onClick={() => onShowToolManagerChange(false)}
              className="text-[#CCCCCC] hover:text-white"
            >
              Back to Agent Creation
            </button>
          </div>
          <ToolManager
            onToolSelect={(tool: Tool) => {
              const exists = selectedTools.find(t => t.name === tool.name);
              if (!exists) {
                onToolsChange([...selectedTools, { name: tool.name, description: tool.description }]);
              }
            }}
            onToolCreate={(tool: Tool) => {
              onToolsChange([...selectedTools, { name: tool.name, description: tool.description }]);
            }}
            onShowToolManagerChange={onShowToolManagerChange}
          />
        </div>
      ) : (
        // Agent Creation View
        <div className="bg-[#2D2D30] rounded-lg p-6">
          <div className="mb-6">
            <label className="block text-[#CCCCCC] mb-2">Agent Name</label>
            <input
              type="text"
              value={newAgent.name}
              onChange={(e) => onAgentChange({...newAgent, name: e.target.value})}
              className="w-full bg-[#1E1E1E] text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter agent name..."
              disabled={isLoading}
            />
          </div>
          <div className="mb-6">
            <label className="block text-[#CCCCCC] mb-2">Agent Type</label>
            <select
              value={newAgent.type}
              onChange={(e) => handleTypeChange(e.target.value as AgentType)}
              className="w-full bg-[#1E1E1E] text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            >
              {agentTypes.map(type => (
                <option key={type.id} value={type.id}>{type.name}</option>
              ))}
            </select>
            <div className="mt-2 text-xs text-[#8E8E8E]">
              {agentTypes.find(t => t.id === newAgent.type)?.description}
            </div>
            {newAgent.type === 'rag' && (
              <div className="mt-2 text-xs text-[#8E8E8E]">
                Supported formats: {agentTypes.find(t => t.id === 'rag')?.supportedFormats?.join(', ')}
              </div>
            )}
            {newAgent.type === 'coding' && (
              <div className="mt-2 text-xs text-[#8E8E8E]">
                Supported languages: {agentTypes.find(t => t.id === 'coding')?.supportedLanguages?.join(', ')}
              </div>
            )}
            {newAgent.type === 'conversational' && (
              <div className="mt-4">
                <label className="block text-[#CCCCCC] mb-2">Prompt Template</label>
                <textarea
                  value={newAgent.configuration?.prompt_template || "You are a helpful AI assistant. Please respond to the following message:\n\n{input}"}
                  onChange={(e) => onAgentChange({
                    ...newAgent,
                    configuration: {
                      ...newAgent.configuration,
                      prompt_template: e.target.value
                    }
                  })}
                  className="w-full bg-[#1E1E1E] text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 h-32"
                  placeholder="Enter prompt template..."
                  disabled={isLoading}
                />
                <div className="mt-1 text-xs text-[#8E8E8E]">
                  Use {"{input}"} as a placeholder for the user's message
                </div>
              </div>
            )}
            {newAgent.type === 'tool_calling' && (
              <div className="mt-4">
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-[#CCCCCC]">Selected Tools</label>
                  <button
                    onClick={() => onShowToolManagerChange(true)}
                    className="text-blue-500 hover:text-blue-400 text-sm"
                  >
                    Manage Tools
                  </button>
                </div>
                {selectedTools.length > 0 ? (
                  <div className="space-y-2">
                    {selectedTools.map((tool) => (
                      <div
                        key={tool.name}
                        className="flex items-center justify-between bg-[#1E1E1E] rounded-lg p-2"
                      >
                        <div>
                          <div className="text-white">{tool.name}</div>
                          <div className="text-xs text-[#8E8E8E]">{tool.description}</div>
                        </div>
                        <button
                          onClick={() => removeSelectedTool(tool.name)}
                          className="text-red-500 hover:text-red-400 ml-2"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-[#8E8E8E] text-sm">
                    No tools selected. Click "Manage Tools" to add tools.
                  </div>
                )}
              </div>
            )}
          </div>
          <div className="flex justify-end space-x-4">
            <button
              onClick={onCancel}
              className="px-4 py-2 bg-[#3E3E42] text-white rounded-lg hover:bg-[#4E4E52] transition-colors"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              onClick={onSubmit}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              disabled={isLoading || !newAgent.name || (newAgent.type === 'tool_calling' && selectedTools.length === 0)}
            >
              {isLoading ? 'Creating...' : 'Create Agent'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
