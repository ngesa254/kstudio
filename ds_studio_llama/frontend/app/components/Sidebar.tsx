'use client';

import { Agent } from '../services/api';
import { AgentType, agentTypes } from '../types';

interface SidebarProps {
  agents: Agent[];
  selectedAgent: Agent | null;
  selectedType: AgentType;
  currentDocument: string | null;
  hoveredAgent: number | null;
  isLoading: boolean;
  onCreateClick: () => void;
  onTypeSelect: (type: AgentType) => void;
  onAgentSelect: (agent: Agent) => void;
  onAgentHover: (id: number | null) => void;
}

export function Sidebar({
  agents,
  selectedAgent,
  selectedType,
  currentDocument,
  hoveredAgent,
  isLoading,
  onCreateClick,
  onTypeSelect,
  onAgentSelect,
  onAgentHover
}: SidebarProps) {
  return (
    <div className="w-64 bg-[#252526] border-r border-[#3E3E42] flex flex-col">
      {/* Logo Area */}
      <div className="p-4 border-b border-[#3E3E42] flex items-center space-x-2">
        <div className="text-2xl">🤖</div>
        <h1 className="text-white font-semibold text-xl">Kazuri Studio</h1>
      </div>

      {/* New Agent Button */}
      <button 
        onClick={onCreateClick}
        className="mx-4 mt-4 mb-6 py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center justify-center space-x-2 transition-colors"
        disabled={isLoading}
      >
        <span>+</span>
        <span>Create New Agent</span>
      </button>

      {/* Agent Types */}
      <div className="flex-1 overflow-y-auto">
        <div className="px-2">
          <h2 className="text-[#8E8E8E] text-sm font-medium mb-2 px-2">Agent Types</h2>
          {agentTypes.map((type) => (
            <button
              key={type.id}
              onClick={() => onTypeSelect(type.id)}
              className={`w-full text-left px-3 py-2 rounded-lg mb-1 flex items-center space-x-3 ${
                selectedType === type.id
                  ? 'bg-[#37373D] text-white'
                  : 'text-[#CCCCCC] hover:bg-[#2D2D30]'
              }`}
            >
              <span>{type.icon}</span>
              <div className="flex flex-col">
                <span>{type.name}</span>
                <span className="text-xs text-[#8E8E8E]">{type.description}</span>
                {type.id === 'rag' && type.supportedFormats && (
                  <span className="text-xs text-[#8E8E8E] mt-1">
                    Supported formats: {type.supportedFormats.join(', ')}
                  </span>
                )}
                {type.id === 'coding' && (
                  <>
                    {type.supportedLanguages && (
                      <span className="text-xs text-[#8E8E8E] mt-1">
                        Supported languages: {type.supportedLanguages.join(', ')}
                      </span>
                    )}
                    {type.features && (
                      <span className="text-xs text-[#8E8E8E] mt-1">
                        Features: {type.features.join(', ')}
                      </span>
                    )}
                  </>
                )}
                {type.id === 'tool_calling' && type.features && (
                  <span className="text-xs text-[#8E8E8E] mt-1">
                    Features: {type.features.join(', ')}
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>

        {/* Deployed Agents */}
        <div className="px-2 mt-6">
          <h2 className="text-[#8E8E8E] text-sm font-medium mb-2 px-2">Deployed Agents</h2>
          {agents.map((agent) => (
            <div
              key={agent.id}
              className="relative"
              onMouseEnter={() => onAgentHover(agent.id)}
              onMouseLeave={() => onAgentHover(null)}
            >
              <button
                onClick={() => onAgentSelect(agent)}
                className={`w-full text-left px-3 py-2 rounded-lg mb-1 flex items-center space-x-3 ${
                  selectedAgent?.id === agent.id
                    ? 'bg-[#37373D] text-white'
                    : 'text-[#CCCCCC] hover:bg-[#2D2D30]'
                }`}
              >
                <span>{agent.type === 'rag' ? '📚' : agent.type === 'tool_calling' ? '🛠️' : agent.type === 'coding' ? '👨‍💻' : '💬'}</span>
                <div className="flex flex-col">
                  <span>{agent.name}</span>
                  {agent.type === 'rag' && currentDocument && selectedAgent?.id === agent.id && (
                    <span className="text-xs text-[#8E8E8E]">
                      Current document: {currentDocument}
                    </span>
                  )}
                </div>
              </button>
              {/* Tooltip */}
              {hoveredAgent === agent.id && agent.configuration?.description && (
                <div className="absolute left-full ml-2 top-0 z-50 bg-[#2D2D30] text-[#CCCCCC] p-2 rounded-lg shadow-lg text-sm max-w-xs">
                  {agent.configuration.description}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
