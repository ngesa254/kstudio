

"use client";
import React, { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  ChevronRight,
  Code,
  User,
  HelpCircle,
  Mail,
  Users,
  Briefcase,
  Slack,
  Blocks,
  Diamond,
  X,
  FileText,
  Github,
  MessageCircle,
  Edit2,
  Mic,
  Send,
  Settings,
} from "lucide-react";



// Types for chat messages
interface Message {
  type: "user" | "assistant";
  content: string;
}

export default function KazuriChat() {
  // ------------------
  // 1) TABS: "Describe" or "Configure"
  // ------------------
  const [currentTab, setCurrentTab] = useState<"Describe" | "Configure">("Describe");

  // ------------------
  // 2) DESCRIBE (CHAT) STATES & LOGIC
  // ------------------
  const [chatMessages, setChatMessages] = useState<Message[]>([
    {
      type: "user",
      content: "Hello! I'd like to create an AI agent for iot sim management.",
    },
    {
      type: "assistant",
      content: "Great! Let's get started. Describe your agent’s main function.",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when chatMessages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatMessages]);

  // Send a user message
  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    const userMsg: Message = { type: "user", content: inputValue.trim() };
    setChatMessages((prev) => [...prev, userMsg]);
    setInputValue("");

    // Simulate an AI reply (or call an API)
    setTimeout(() => {
      const aiMsg: Message = {
        type: "assistant",
        content: `AI response for: "${userMsg.content}"`,
      };
      setChatMessages((prev) => [...prev, aiMsg]);
    }, 800);
  };

  // ------------------
  // 3) CONFIGURE (COLLAPSIBLE SECTIONS) STATES & LOGIC
  // ------------------
  const [activeSection, setActiveSection] = useState<string>("");
  const [basicInfo, setBasicInfo] = useState({
    name: "Engineering Agent",
    description: "Helps debug code errors and onboard to our systems faster",
  });

  // Sections to show in "Configure" tab
  const sections = [
    { id: "basic", title: "Basic info" },
    { id: "knowledge", title: "Knowledge" },
    { id: "instruction", title: "Instruction" },
    { id: "actions", title: "Actions" },
    { id: "function", title: "Company functions" },
    { id: "triggering", title: "Triggering" },
    { id: "publish", title: "Publish" },
  ];

  // Render content for each collapsible section
  const renderSectionContent = (sectionId: string) => {
    switch (sectionId) {
      case "basic":
        return (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center">
                <Code className="w-4 h-4 text-blue-600" />
              </div>
              <input
                type="text"
                value={basicInfo.name}
                onChange={(e) => setBasicInfo({ ...basicInfo, name: e.target.value })}
                className="flex-1 p-2 border rounded-md"
                placeholder="Engineering Agent"
              />
            </div>
            <textarea
              value={basicInfo.description}
              onChange={(e) =>
                setBasicInfo({ ...basicInfo, description: e.target.value })
              }
              className="w-full p-3 border rounded-md min-h-[100px]"
              placeholder="Helps debug code errors and onboard to our systems faster"
            />
          </div>
        );

      case "knowledge":
        return (
          <div className="mt-4 flex items-center gap-3 justify-center">
            <Diamond className="w-6 h-6 text-blue-500" />
            <div className="h-px w-16 bg-gray-200" />
            <X className="w-6 h-6 text-gray-400" />
            <div className="h-px w-16 bg-gray-200" />
            <FileText className="w-6 h-6 text-green-500" />
            <div className="h-px w-16 bg-gray-200" />
            <Code className="w-6 h-6 text-blue-500" />
            <div className="h-px w-16 bg-gray-200" />
            <Mail className="w-6 h-6 text-gray-400" />
            <div className="h-px w-16 bg-gray-200" />
            <Github className="w-6 h-6 text-gray-600" />
          </div>
        );

      case "instruction":
        return (
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-gray-600">
              Follow the user's requirements carefully &amp; to the letter.
            </p>
            <p className="text-gray-600 mt-2">
              When asked to write code, follow these instructions:
            </p>
            <p className="text-gray-600 mt-1">
              1. Directly write code and skip any guidance.
            </p>
          </div>
        );

      case "actions":
        return (
          <div className="flex items-center gap-6 justify-center py-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-orange-50 rounded-lg flex items-center justify-center">
                <Code className="w-4 h-4 text-orange-600" />
              </div>
              <span className="text-sm">Code Search</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center">
                <User className="w-4 h-4 text-blue-600" />
              </div>
              <span className="text-sm">Expert Search</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center">
                <HelpCircle className="w-4 h-4 text-blue-600" />
              </div>
              <span className="text-sm">Create Jira</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-red-50 rounded-lg flex items-center justify-center">
                <Mail className="w-4 h-4 text-red-600" />
              </div>
              <span className="text-sm">Create email</span>
            </div>
          </div>
        );

        case "function":
          return (
            <div className="flex items-center gap-6 justify-center py-4">
              {/* TES - Technical Enterprise Services */}
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-orange-50 rounded-lg flex items-center justify-center">
                  <Settings className="w-4 h-4 text-green-600" />
                </div>
                <span className="text-sm">TES</span>
              </div>

              {/* EBU - Enterprise Business Unit */}
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center">
                <Briefcase className="w-4 h-4 text-blue-600" />
                </div>
                <span className="text-sm">EBU</span>
              </div>

                {/* DIT - Digital IT */}
              <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-orange-50 rounded-lg flex items-center justify-center">
              <Code className="w-4 h-4 text-orange-600" />
              </div>
                <span className="text-sm">DIT</span>
              </div>

                  {/* HR - Human Resources */}
              <div className="flex items-center gap-2">
                                <div className="w-8 h-8 bg-purple-50 rounded-lg flex items-center justify-center">
          <Users className="w-4 h-4 text-purple-600" />
        </div>
                <span className="text-sm">HR</span>

              </div>
            </div>
          );

      case "triggering":
        return (
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-gray-600">
              Auto-trigger this app when a user asks a question about the
              company's codebase, or questions relating to engineering practices
              and software development lifecycle.
            </p>
          </div>
        );

      case "publish":
        return (
          <div>
            <div className="flex items-center gap-8 justify-center py-4">
              <div className="flex flex-col items-center gap-2">
                <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center cursor-pointer hover:bg-blue-100">
                  <MessageCircle className="w-6 h-6 text-blue-600" />
                </div>
                <span className="text-sm text-gray-600">Chat</span>
              </div>
              <div className="flex flex-col items-center gap-2">
                <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center cursor-pointer hover:bg-green-100">
                  <Slack className="w-6 h-6 text-green-600" />
                </div>
                <span className="text-sm text-gray-600">Slack</span>
              </div>
              <div className="flex flex-col items-center gap-2">
                <div className="w-12 h-12 bg-indigo-50 rounded-lg flex items-center justify-center cursor-pointer hover:bg-indigo-100">
                  <Blocks className="w-6 h-6 text-indigo-600" />
                </div>
                <span className="text-sm text-gray-600">API</span>
              </div>
            </div>
            <div className="flex justify-center mt-8">
              <button className="px-8 py-2.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium text-sm">
                Configure Agent
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  // ------------------
  // 4) RENDER
  // ------------------
  return (
    <div className="flex flex-col h-full w-full">
      {/* TAB SWITCH (Describe / Configure) */}
      <div className="mb-2 flex space-x-4">
        <button
          onClick={() => setCurrentTab("Describe")}
          className={`px-4 py-2 rounded ${
            currentTab === "Describe"
              ? "bg-blue-500 text-white"
              : "bg-gray-200 text-gray-700"
          }`}
        >
          Describe
        </button>

        
        <button
          onClick={() => setCurrentTab("Configure")}
          className={`px-4 py-2 rounded ${
            currentTab === "Configure"
              ? "bg-blue-500 text-white"
              : "bg-gray-200 text-gray-700"
          }`}
        >
          Configure
        </button>

{/* <button
  onClick={() => setCurrentTab("Describe")}
  className={`px-4 py-2 rounded font-medium transition-colors duration-200 ease-in-out ${
    currentTab === "Describe"
      ? "bg-red-400 hover:bg-red-500 text-white"
      : "bg-gray-200 hover:bg-gray-300 text-gray-700"
  }`}
>
  Describe
</button>

<button
  onClick={() => setCurrentTab("Configure")}
  className={`px-4 py-2 rounded font-medium transition-colors duration-200 ease-in-out ${
    currentTab === "Configure"
      ? "bg-red-400 hover:bg-red-500 text-white"
      : "bg-gray-200 hover:bg-gray-300 text-gray-700"
  }`}
>
  Configure
</button> */}

      </div>

      {currentTab === "Describe" && (
        <div className="flex flex-col h-full">
          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto mb-2">
            {chatMessages.map((msg, index) => {
              const isUser = msg.type === "user";
              return (
                <div
                  key={index}
                  className={`mb-4 p-2 rounded ${
                    isUser ? "bg-green-100 self-end" : "bg-white"
                  }`}
                >
                  {/* Icon + Label */}
                  <div className="flex items-start gap-2 mb-1">
                    <img
                      src={isUser ? "/african.svg" : "/zuri-icon.svg"}
                      alt={isUser ? "User Icon" : "AI Icon"}
                      className="w-6 h-6 object-cover"
                    />
                    <p className="font-bold text-sm">
                      {isUser ? "User" : "Kazuri Agent (AI)"}
                    </p>
                  </div>
                  {/* Message content */}
                  <pre className="text-sm whitespace-pre-wrap">{msg.content}</pre>
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Bar */}
          <div className="relative">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSendMessage();
              }}
              placeholder="Type your message..."
              className="pr-24"
            />
            <div className="absolute right-2 top-2 flex gap-2">
              <Button variant="ghost" size="icon">
                <Edit2 size={16} />
              </Button>
              <Button variant="ghost" size="icon">
                <Mic size={16} />
              </Button>
              <Button variant="ghost" size="icon" onClick={handleSendMessage}>
                <Send size={16} />
              </Button>
            </div>
          </div>
        </div>
      )}

      {currentTab === "Configure" && (
        <div className="h-full w-full overflow-y-auto">
          <div className="space-y-4 mt-2">
            {sections.map((section) => (
              <div
                key={section.id}
                className="bg-white rounded-lg border shadow-sm p-4"
              >
                <div
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() =>
                    setActiveSection(activeSection === section.id ? "" : section.id)
                  }
                >
                  <span className="text-gray-700 font-medium">{section.title}</span>
                  <ChevronRight
                    className={`w-5 h-5 text-gray-400 transition-transform ${
                      activeSection === section.id ? "rotate-90" : ""
                    }`}
                  />
                </div>
                {activeSection === section.id && (
                  <div className="mt-4">{renderSectionContent(section.id)}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
