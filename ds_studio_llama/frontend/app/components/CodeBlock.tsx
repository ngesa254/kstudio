'use client';

import React, { useRef, useEffect } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

export interface CodeBlockProps {
  code: string;
  language: string;
  editable?: boolean;
  onChange?: (value: string) => void;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ 
  code, 
  language, 
  editable = false,
  onChange 
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [code]);

  if (editable) {
    return (
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={code}
          onChange={(e) => onChange?.(e.target.value)}
          className="w-full min-h-[200px] p-4 font-mono text-sm bg-[#1E1E1E] text-[#D4D4D4] border border-[#404040] rounded-lg resize-y"
          style={{
            tabSize: 2,
            whiteSpace: 'pre',
            overflowWrap: 'normal',
            overflowX: 'auto',
          }}
        />
      </div>
    );
  }

  return (
    <div className="relative group">
      <SyntaxHighlighter
        language={language}
        style={vscDarkPlus}
        customStyle={{
          margin: 0,
          borderRadius: '0.5rem',
          padding: '1rem',
        }}
      >
        {code}
      </SyntaxHighlighter>
      <button
        onClick={() => navigator.clipboard.writeText(code)}
        className="absolute top-2 right-2 p-2 bg-[#2D2D30] text-[#CCCCCC] rounded hover:bg-[#3E3E42] opacity-0 group-hover:opacity-100 transition-opacity"
        title="Copy code"
      >
        📋
      </button>
    </div>
  );
};

export default CodeBlock;
