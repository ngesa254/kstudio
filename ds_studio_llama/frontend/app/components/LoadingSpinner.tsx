'use client';

interface LoadingSpinnerProps {
  message?: string;
  submessage?: string;
}

export const LoadingSpinner = ({ 
  message = "Processing document...", 
  submessage = "This may take a few moments" 
}: LoadingSpinnerProps) => {
  return (
    <div className="flex flex-col items-center justify-center">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      <div className="mt-4 text-[#8E8E8E] text-sm">
        {message}
      </div>
      <div className="mt-2 text-[#8E8E8E] text-xs">
        {submessage}
      </div>
    </div>
  );
};
