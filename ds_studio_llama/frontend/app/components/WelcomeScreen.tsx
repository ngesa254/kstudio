'use client';

interface WelcomeScreenProps {
  isLoading: boolean;
  onCreateClick: () => void;
}

export function WelcomeScreen({ isLoading, onCreateClick }: WelcomeScreenProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center text-[#8E8E8E]">
      <h3 className="text-2xl mb-4 text-white">Welcome to Kazuri Studio</h3>
      <p className="text-sm mb-8">Create or select an agent to get started</p>
      <button
        onClick={onCreateClick}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        disabled={isLoading}
      >
        Create Your First Agent
      </button>
    </div>
  );
}
