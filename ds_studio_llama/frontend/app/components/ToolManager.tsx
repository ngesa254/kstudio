'use client';

import React, { useState, useEffect } from 'react';
import { Tool, api } from '../services/api';
import { CodeBlock } from './CodeBlock';

interface ToolManagerProps {
  onToolSelect: (tool: Tool) => void;
  onToolCreate: (tool: Tool) => void;
  onShowToolManagerChange: (show: boolean) => void;
}

type CreationMode = 'description' | 'code';

export default function ToolManager({ onToolSelect, onToolCreate, onShowToolManagerChange }: ToolManagerProps) {
  const [tools, setTools] = useState<Tool[]>([]);
  const [isCreating, setIsCreating] = useState(false);
  const [creationMode, setCreationMode] = useState<CreationMode>('description');
  const [description, setDescription] = useState('');
  const [toolName, setToolName] = useState('');
  const [code, setCode] = useState(`def run(**kwargs) -> Dict[str, Any]:
    """
    Tool implementation.
    
    Args:
        kwargs: Tool parameters
        
    Returns:
        Dict containing results
    """
    # Your code here
    return {"result": "Not implemented"}
`);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    loadTools();
  }, []);

  // Clear success message and return to agent creation after delay
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => {
        setSuccessMessage('');
        onShowToolManagerChange(false);
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [successMessage, onShowToolManagerChange]);

  const loadTools = async () => {
    try {
      setLoading(true);
      const toolsList = await api.listTools();
      setTools(toolsList);
    } catch (err) {
      setError('Failed to load tools');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTool = async () => {
    try {
      setLoading(true);
      setError('');

      let newTool: Tool;

      if (creationMode === 'code') {
        newTool = await api.createToolFromCode({
          name: toolName,
          code,
          created_by: 'user', // TODO: Add user management
        });
      } else {
        newTool = await api.createTool({
          description,
          code: undefined,
          created_by: 'user', // TODO: Add user management
        });
      }

      setTools([...tools, newTool]);
      onToolCreate(newTool);
      setIsCreating(false);
      resetForm();
      setSuccessMessage('Tool created successfully! Returning to agent creation...');
    } catch (err) {
      setError('Failed to create tool');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleToolSelect = (tool: Tool) => {
    onToolSelect(tool);
    setSuccessMessage('Tool selected successfully! Returning to agent creation...');
  };

  const resetForm = () => {
    setDescription('');
    setToolName('');
    setCode(`def run(**kwargs) -> Dict[str, Any]:
    """
    Tool implementation.
    
    Args:
        kwargs: Tool parameters
        
    Returns:
        Dict containing results
    """
    # Your code here
    return {"result": "Not implemented"}
`);
  };

  const getSampleTools = () => {
    return tools.filter(tool => tool.is_sample);
  };

  const getCustomTools = () => {
    return tools.filter(tool => !tool.is_sample);
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-white">Tools</h2>
        <div className="flex items-center space-x-4">
          <button
            onClick={() => onShowToolManagerChange(false)}
            className="text-[#CCCCCC] hover:text-white"
          >
            Back to Agent Creation
          </button>
          <button
            onClick={() => setIsCreating(!isCreating)}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
          >
            {isCreating ? 'Cancel' : 'Create Tool'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-400 text-red-500 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="bg-green-500/10 border border-green-400 text-green-500 px-4 py-3 rounded mb-4">
          {successMessage}
        </div>
      )}

      {isCreating ? (
        <div className="bg-[#2D2D30] rounded-lg p-6 mb-4">
          <div className="mb-4">
            <label className="block text-sm font-medium text-[#CCCCCC] mb-2">
              Creation Mode
            </label>
            <div className="flex space-x-4">
              <button
                onClick={() => setCreationMode('description')}
                className={`px-4 py-2 rounded ${
                  creationMode === 'description'
                    ? 'bg-blue-600 text-white'
                    : 'bg-[#3E3E42] text-[#CCCCCC] hover:bg-[#4E4E52]'
                }`}
              >
                From Description
              </button>
              <button
                onClick={() => setCreationMode('code')}
                className={`px-4 py-2 rounded ${
                  creationMode === 'code'
                    ? 'bg-blue-600 text-white'
                    : 'bg-[#3E3E42] text-[#CCCCCC] hover:bg-[#4E4E52]'
                }`}
              >
                Custom Code
              </button>
            </div>
          </div>

          {creationMode === 'description' && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-[#CCCCCC] mb-2">
                Description
              </label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full px-3 py-2 bg-[#1E1E1E] text-white border border-[#3E3E42] rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Tool description"
              />
            </div>
          )}

          {creationMode === 'code' && (
            <>
              <div className="mb-4">
                <label className="block text-sm font-medium text-[#CCCCCC] mb-2">
                  Tool Name
                </label>
                <input
                  type="text"
                  value={toolName}
                  onChange={(e) => setToolName(e.target.value)}
                  className="w-full px-3 py-2 bg-[#1E1E1E] text-white border border-[#3E3E42] rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Tool name"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-[#CCCCCC] mb-2">
                  Implementation
                </label>
                <CodeBlock
                  code={code}
                  onChange={(value: string) => setCode(value)}
                  language="python"
                  editable={true}
                />
              </div>
            </>
          )}

          <button
            onClick={handleCreateTool}
            disabled={loading || (!description && !toolName) || (creationMode === 'code' && !code)}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {loading ? 'Creating...' : 'Create'}
          </button>
        </div>
      ) : (
        <>
          <h3 className="text-lg font-medium mb-4 text-white">Sample Tools</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            {getSampleTools().map((tool) => (
              <div
                key={tool.name}
                onClick={() => handleToolSelect(tool)}
                className="bg-[#2D2D30] rounded-lg p-4 cursor-pointer hover:bg-[#3E3E42] transition-shadow border-l-4 border-blue-500"
              >
                <h3 className="font-medium mb-2 text-white">{tool.name}</h3>
                <p className="text-sm text-[#CCCCCC] mb-2">{tool.description}</p>
                <div className="flex justify-between items-center text-xs text-[#8E8E8E]">
                  <span>Sample Tool</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleToolSelect(tool);
                    }}
                    className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition-colors text-sm"
                  >
                    Select
                  </button>
                </div>
              </div>
            ))}
          </div>

          <h3 className="text-lg font-medium mb-4 text-white">Custom Tools</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {getCustomTools().map((tool) => (
              <div
                key={tool.name}
                onClick={() => handleToolSelect(tool)}
                className="bg-[#2D2D30] rounded-lg p-4 cursor-pointer hover:bg-[#3E3E42] transition-shadow"
              >
                <h3 className="font-medium mb-2 text-white">{tool.name}</h3>
                <p className="text-sm text-[#CCCCCC] mb-2">{tool.description}</p>
                <div className="flex justify-between items-center text-xs text-[#8E8E8E]">
                  <span>Custom Tool</span>
                  <div className="flex items-center space-x-2">
                    {tool.created_at && (
                      <span>
                        Created: {new Date(tool.created_at).toLocaleDateString()}
                      </span>
                    )}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleToolSelect(tool);
                      }}
                      className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition-colors text-sm"
                    >
                      Select
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
