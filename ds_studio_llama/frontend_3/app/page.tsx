// // app/page.tsx
// export default function HomePage() {
//     return (
//       <div>
//         <h1>Welcome to my Next.js app!</h1>
//         <p>This is the root page.</p>
//       </div>
//     );
//   }


// app/page.tsx

import Sidebar from "@/components/Sidebar";
import KazuriChat from "@/components/Chat/kazuriChat";
import AgentTest from "@/components/AgentTest";

export default function HomePage() {
  return (
    <div className="h-screen flex flex-row">
      {/* Sidebar on the left */}
      <Sidebar />

      {/* Main content area */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="flex flex-col h-full w-full">
          <h1 className="text-2xl font-bold mb-2">KAZURI Studio</h1>
          <p className="mb-4 text-gray-600">Create your Own AI Agent with no code</p>

          <div className="flex flex-row h-[600px] space-x-4">
            {/* Left panel: KazuriChat */}
            <div className="flex-1 border rounded p-2 bg-gray-50 overflow-auto">
              <KazuriChat />
            </div>

            {/* Right panel: AgentTest */}
            <div className="w-1/2 border rounded p-2 bg-white shadow-lg overflow-auto">
              <AgentTest />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
