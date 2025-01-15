'use client';

import { useState, useEffect } from 'react';
import { Agent, api } from './services/api';
import { AgentType, Message } from './types';
import { Sidebar } from './components/Sidebar';
import { ChatInterface } from './components/ChatInterface';
import { DocumentUpload } from './components/DocumentUpload';
import { WelcomeScreen } from './components/WelcomeScreen';
import { AgentCreationForm } from './components/AgentCreationForm';

export default function Home() {
  // Core state
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [selectedType, setSelectedType] = useState<AgentType>('conversational');
  const [isCreating, setIsCreating] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Agent creation state
  const [newAgent, setNewAgent] = useState<{
    name: string;
    type: AgentType;
    configuration: Record<string, any>;
  }>({
    name: '',
    type: 'conversational',
    configuration: {}
  });
  const [selectedTools, setSelectedTools] = useState<Array<{ name: string; description: string }>>([]);
  const [showToolManager, setShowToolManager] = useState(false);

  // Chat state
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedLanguage, setSelectedLanguage] = useState<string>('python');
  const [codingMode, setCodingMode] = useState<'generate' | 'troubleshoot' | 'explain'>('generate');

  // Document state
  const [isProcessingDocument, setIsProcessingDocument] = useState(false);
  const [hasDocument, setHasDocument] = useState(false);
  const [currentDocument, setCurrentDocument] = useState<string | null>(null);

  // UI state
  const [hoveredAgent, setHoveredAgent] = useState<number | null>(null);

  const loadAgents = async () => {
    try {
      setIsLoading(true);
      const fetchedAgents = await api.listAgents();
      setAgents(fetchedAgents);
    } catch (err) {
      setError('Failed to load agents');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Load agents on mount
  useEffect(() => {
    loadAgents();
  }, []);

  // Reset states when switching agents
  useEffect(() => {
    if (selectedAgent) {
      setHasDocument(false);
      setCurrentDocument(null);
      setMessages([]);
      if (selectedAgent.type === 'coding') {
        setCodingMode('generate');
      }
    }
  }, [selectedAgent]);

  // Update newAgent type when selectedType changes
  useEffect(() => {
    setNewAgent(prev => ({
      ...prev,
      type: selectedType,
      configuration: {} // Reset configuration when type changes
    }));
  }, [selectedType]);

  const handleMessageSend = async () => {
    if (!selectedAgent || !message.trim()) return;

    try {
      setIsLoading(true);
      const userMessage: Message = {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString(),
        language: selectedAgent.type === 'coding' ? selectedLanguage : undefined,
        error: selectedAgent.type === 'coding' && codingMode === 'troubleshoot'
      };
      setMessages([...messages, userMessage]);
      setMessage('');

      // Format last 5 messages into chat history
      const lastFiveMessages = messages.slice(-5).map(msg => 
        `${msg.role === 'user' ? 'User' : 'Assistant'}: ${msg.content}`
      ).join('\n');

      // Combine history with new message
      const messageWithHistory = lastFiveMessages 
        ? `Chat history:\n${lastFiveMessages}\n\nNew message:\n${message}`
        : message;

      const response = await api.queryAgent(
        selectedAgent.id,
        messageWithHistory,
        selectedAgent.type === 'coding'
          ? {
              language: selectedLanguage,
              mode: codingMode
            }
          : undefined
      );

      const agentMessage: Message = {
        role: 'assistant',
        content: response.response,
        timestamp: response.created_at,
        language: response.metadata?.language || selectedLanguage,
        code: response.metadata?.formatted_code
      };
      setMessages(prev => [...prev, agentMessage]);
    } catch (err) {
      setError('Failed to send message');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    setIsProcessingDocument(true);
    try {
      await api.uploadDocument(selectedAgent!.id, file);
      const response = await api.queryAgent(selectedAgent!.id, "Please provide a brief summary of this document.");
      
      setHasDocument(true);
      setCurrentDocument(file.name);
      setMessages([{
        role: 'assistant',
        content: response.response,
        timestamp: response.created_at
      }]);
    } catch (err) {
      setError('Failed to process document');
      console.error(err);
    } finally {
      setIsProcessingDocument(false);
    }
  };

  const handleCreateAgent = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Validate tool selection for tool calling agents
      if (newAgent.type === 'tool_calling' && selectedTools.length === 0) {
        setError('Please select at least one tool for the Tool Agent');
        setIsLoading(false);
        return;
      }

      // Add selected tools to agent configuration for tool calling agents
      const agentData = {
        ...newAgent,
        configuration: {
          ...newAgent.configuration,
          ...(newAgent.type === 'tool_calling' ? {
            tools: selectedTools.map(tool => tool.name),
            prompt_template: `You are an AI assistant with access to the following tools:
${selectedTools.map(tool => `- ${tool.name}: ${tool.description}`).join('\n')}

Please help with the following request:
{input}`
          } : {})
        }
      };

      const agent = await api.createAgent(agentData);
      setAgents([...agents, agent]);
      setIsCreating(false);
      setSelectedAgent(agent);
      setNewAgent({ name: '', type: selectedType, configuration: {} });
      setSelectedTools([]);
      setShowToolManager(false);
    } catch (err) {
      setError('Failed to create agent');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartCreating = () => {
    setIsCreating(true);
    setNewAgent({ name: '', type: selectedType, configuration: {} });
  };

  return (
    <div className="flex h-screen bg-[#1E1E1E]">
      <Sidebar
        agents={agents}
        selectedAgent={selectedAgent}
        selectedType={selectedType}
        currentDocument={currentDocument}
        hoveredAgent={hoveredAgent}
        isLoading={isLoading}
        onCreateClick={handleStartCreating}
        onTypeSelect={setSelectedType}
        onAgentSelect={setSelectedAgent}
        onAgentHover={setHoveredAgent}
      />

      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="h-14 border-b border-[#3E3E42] flex items-center px-6">
          <h2 className="text-white font-medium">
            {isCreating ? 'Create New Agent' : selectedAgent ? selectedAgent.name : 'Select or Create an Agent'}
          </h2>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-500/10 text-red-500 px-4 py-2 text-sm">
            {error}
            <button 
              onClick={() => setError(null)}
              className="ml-2 hover:text-red-400"
            >
              ✕
            </button>
          </div>
        )}

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6">
          {isCreating ? (
            <AgentCreationForm
              newAgent={newAgent}
              selectedTools={selectedTools}
              showToolManager={showToolManager}
              isLoading={isLoading}
              onAgentChange={setNewAgent}
              onToolsChange={setSelectedTools}
              onShowToolManagerChange={setShowToolManager}
              onCancel={() => {
                setIsCreating(false);
                setNewAgent({ name: '', type: selectedType, configuration: {} });
                setSelectedTools([]);
                setShowToolManager(false);
              }}
              onSubmit={handleCreateAgent}
            />
          ) : selectedAgent ? (
            selectedAgent.type === 'rag' && !hasDocument ? (
              <DocumentUpload
                isProcessingDocument={isProcessingDocument}
                onFileUpload={handleFileUpload}
              />
            ) : (
              <ChatInterface
                agent={selectedAgent}
                messages={messages}
                message={message}
                isLoading={isLoading}
                isProcessingDocument={isProcessingDocument}
                selectedLanguage={selectedLanguage}
                codingMode={codingMode}
                onMessageChange={setMessage}
                onMessageSend={handleMessageSend}
                onLanguageChange={setSelectedLanguage}
                onCodingModeChange={setCodingMode}
                onFileUpload={handleFileUpload}
              />
            )
          ) : (
            <WelcomeScreen
              isLoading={isLoading}
              onCreateClick={handleStartCreating}
            />
          )}
        </div>
      </div>
    </div>
  );
}
