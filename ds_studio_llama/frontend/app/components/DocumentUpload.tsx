'use client';

import { LoadingSpinner } from './LoadingSpinner';
import { agentTypes } from '../types';

interface DocumentUploadProps {
  isProcessingDocument: boolean;
  onFileUpload: (file: File) => Promise<void>;
}

export function DocumentUpload({ isProcessingDocument, onFileUpload }: DocumentUploadProps) {
  const supportedFormats = agentTypes.find(t => t.id === 'rag')?.supportedFormats || [];

  return (
    <div className="flex flex-col items-center justify-center h-full text-center text-[#8E8E8E]">
      {isProcessingDocument ? (
        <LoadingSpinner />
      ) : (
        <>
          <h3 className="text-2xl mb-4 text-white">Upload a Document</h3>
          <p className="text-sm mb-2">Please upload a document to start asking questions</p>
          <p className="text-xs mb-4">
            Supported formats: {supportedFormats.join(', ')}
          </p>
          <div className="text-sm font-bold text-yellow-500 mb-8 max-w-md">
            ⚠️ Important: For PowerPoint files, please ensure they are closed before uploading. 
          </div>
          <label className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors cursor-pointer">
            <input
              type="file"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  onFileUpload(e.target.files[0]);
                }
              }}
              accept={supportedFormats.join(',')}
            />
            Upload Document
          </label>
        </>
      )}
    </div>
  );
}
