'use client';

import { Agent } from '../services/api';
import { Message, agentTypes } from '../types';
import { LoadingSpinner } from './LoadingSpinner';
import { CodeBlock } from './CodeBlock';

interface ChatInterfaceProps {
  agent: Agent;
  messages: Message[];
  message: string;
  isLoading: boolean;
  isProcessingDocument: boolean;
  selectedLanguage: string;
  codingMode: 'generate' | 'troubleshoot' | 'explain';
  onMessageChange: (message: string) => void;
  onMessageSend: () => void;
  onLanguageChange: (language: string) => void;
  onCodingModeChange: (mode: 'generate' | 'troubleshoot' | 'explain') => void;
  onFileUpload?: (file: File) => Promise<void>;
}

export function ChatInterface({
  agent,
  messages,
  message,
  isLoading,
  isProcessingDocument,
  selectedLanguage,
  codingMode,
  onMessageChange,
  onMessageSend,
  onLanguageChange,
  onCodingModeChange,
  onFileUpload
}: ChatInterfaceProps) {
  const renderMessage = (msg: Message) => {
    if (msg.code && msg.code.length > 0) {
      return (
        <div className="space-y-4">
          <div className="text-[#CCCCCC]">{msg.content}</div>
          {msg.code.map((code, idx) => (
            <CodeBlock key={idx} code={code} language={msg.language || 'text'} />
          ))}
        </div>
      );
    }
    return msg.content;
  };

  const getInputPlaceholder = () => {
    if (agent.type === 'coding') {
      switch (codingMode) {
        case 'generate':
          return "Describe the code you want to generate...";
        case 'troubleshoot':
          return "Paste your code and describe the error...";
        case 'explain':
          return "Paste the code you want explained...";
        default:
          return "Type your message...";
      }
    } else if (agent.type === 'tool_calling') {
      return "What would you like the tools to help you with?";
    } else if (agent.type === 'rag') {
      return "Ask a question about the document...";
    }
    return "Type your message...";
  };

  const getLoadingMessage = () => {
    if (agent.type === 'coding') {
      const language = selectedLanguage || 'python';
      switch (codingMode) {
        case 'generate':
          return {
            message: `Generating ${language} code...`,
            submessage: "Writing clean, documented code with best practices"
          };
        case 'troubleshoot':
          return {
            message: `Analyzing ${language} code...`,
            submessage: "Identifying issues and preparing solutions"
          };
        case 'explain':
          return {
            message: `Analyzing ${language} code...`,
            submessage: "Preparing detailed explanation and improvements"
          };
        default:
          return {
            message: `Processing ${language} code...`,
            submessage: "This may take a few moments"
          };
      }
    } else if (agent.type === 'tool_calling') {
      return {
        message: "Processing with tools...",
        submessage: "Executing tools to complete your request"
      };
    } else if (agent.type === 'rag') {
      return {
        message: "Searching document...",
        submessage: "Finding relevant information"
      };
    }
    return {
      message: "Processing...",
      submessage: "This may take a few moments"
    };
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 mb-4 overflow-y-auto">
        {isLoading ? (
          <div className="h-full flex items-center justify-center">
            <LoadingSpinner {...getLoadingMessage()} />
          </div>
        ) : messages.length > 0 ? (
          <div className="space-y-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    msg.role === 'user'
                      ? msg.error 
                        ? 'bg-red-600 text-white'
                        : 'bg-blue-600 text-white'
                      : 'bg-[#2D2D30] text-[#CCCCCC]'
                  }`}
                >
                  {renderMessage(msg)}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center text-[#8E8E8E]">
            <h3 className="text-2xl mb-4">Start interacting with {agent.name}</h3>
            <p className="text-sm">{agent.configuration?.description || `This agent is configured for ${agent.type} interactions`}</p>
            {agent.type === 'tool_calling' && agent.configuration?.tools && (
              <div className="mt-4 text-sm">
                <p className="mb-2">Available tools:</p>
                <ul className="list-disc list-inside">
                  {agent.configuration.tools.map((tool: string) => (
                    <li key={tool}>{tool}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Input Area */}
      <div className="border-t border-[#3E3E42] pt-4">
        <div className="max-w-4xl mx-auto relative">
          {agent.type === 'coding' && (
            <div className="mb-4 flex space-x-4">
              <select
                value={selectedLanguage}
                onChange={(e) => onLanguageChange(e.target.value)}
                className="bg-[#2D2D30] text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {agentTypes.find(t => t.id === 'coding')?.supportedLanguages?.map(lang => (
                  <option key={lang} value={lang}>{lang}</option>
                ))}
              </select>
              <div className="flex rounded-lg overflow-hidden">
                <button
                  onClick={() => onCodingModeChange('generate')}
                  className={`px-4 py-2 ${
                    codingMode === 'generate'
                      ? 'bg-blue-600 text-white'
                      : 'bg-[#2D2D30] text-[#CCCCCC] hover:bg-[#3E3E42]'
                  }`}
                >
                  Generate
                </button>
                <button
                  onClick={() => onCodingModeChange('troubleshoot')}
                  className={`px-4 py-2 ${
                    codingMode === 'troubleshoot'
                      ? 'bg-blue-600 text-white'
                      : 'bg-[#2D2D30] text-[#CCCCCC] hover:bg-[#3E3E42]'
                  }`}
                >
                  Troubleshoot
                </button>
                <button
                  onClick={() => onCodingModeChange('explain')}
                  className={`px-4 py-2 ${
                    codingMode === 'explain'
                      ? 'bg-blue-600 text-white'
                      : 'bg-[#2D2D30] text-[#CCCCCC] hover:bg-[#3E3E42]'
                  }`}
                >
                  Explain
                </button>
              </div>
            </div>
          )}
          <input
            type="text"
            value={message}
            onChange={(e) => onMessageChange(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && onMessageSend()}
            placeholder={getInputPlaceholder()}
            className="w-full bg-[#2D2D30] text-white rounded-lg pl-4 pr-32 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading || isProcessingDocument}
          />
          <div className="absolute right-2 top-2 flex space-x-2">
            {agent.type === 'rag' && onFileUpload && (
              <label className="p-2 hover:bg-[#3E3E42] rounded-lg transition-colors cursor-pointer">
                <input
                  type="file"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      onFileUpload(e.target.files[0]);
                    }
                  }}
                  accept={agentTypes.find(t => t.id === 'rag')?.supportedFormats?.join(',')}
                  disabled={isProcessingDocument}
                />
                <span role="img" aria-label="attach">📎</span>
              </label>
            )}
            <button 
              onClick={onMessageSend}
              className="bg-blue-600 text-white px-4 py-1 rounded-lg hover:bg-blue-700 transition-colors"
              disabled={isLoading || isProcessingDocument}
            >
              {isLoading ? '...' : 'Send'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
