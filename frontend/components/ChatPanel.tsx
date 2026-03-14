"use client";
import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2 } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

function formatMessage(content: string): string {
  return content
    .replace(/### (.*?)(\n|$)/g, '<p class="font-bold text-blue-400 mt-3 mb-1 text-sm">$1</p>')
    .replace(/## (.*?)(\n|$)/g, '<p class="font-bold text-white mt-3 mb-1">$1</p>')
    .replace(/# (.*?)(\n|$)/g, '<p class="font-bold text-white text-base mt-3 mb-1">$1</p>')
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^- (.*?)(\n|$)/gm, '<li class="ml-4 list-disc text-gray-300">$1</li>')
    .replace(/^\d+\. (.*?)(\n|$)/gm, '<li class="ml-4 list-decimal text-gray-300">$1</li>')
    .replace(/\n/g, '<br/>');
}

export default function ChatPanel({ onChartData }: { onChartData: (data: any) => void }) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "👋 Hi! I'm Skylark's BI Agent. Ask me anything about your work orders, deals, pipeline health, or sector performance!"
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: "user", content: input };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
  const response = await fetch("https://monday-agent-backend.onrender.com/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages: newMessages })
  });

      const data = await response.json();

      setMessages(prev => [...prev, {
        role: "assistant",
        content: data.reply
      }]);

      if (data.chartData) {
        onChartData(data.chartData);
      }

    } catch (error) {
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "Sorry, I couldn't connect to the backend. Make sure the server is running."
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-800 bg-gray-900">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <Bot size={16} />
          </div>
          <div>
            <h1 className="font-bold text-white">Skylark BI Agent</h1>
            <p className="text-xs text-gray-400">Powered by monday.com + Groq</p>
          </div>
          <div className="ml-auto w-2 h-2 bg-green-500 rounded-full"></div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
            <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
              msg.role === "assistant" ? "bg-blue-600" : "bg-gray-600"
            }`}>
              {msg.role === "assistant" ? <Bot size={14} /> : <User size={14} />}
            </div>
            <div className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${
              msg.role === "assistant"
                ? "bg-gray-800 text-gray-100"
                : "bg-blue-600 text-white"
            }`}>
              {msg.role === "assistant" ? (
                <div
                  dangerouslySetInnerHTML={{ __html: formatMessage(msg.content) }}
                />
              ) : (
                msg.content
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center">
              <Bot size={14} />
            </div>
            <div className="bg-gray-800 rounded-2xl px-4 py-2">
              <Loader2 size={16} className="animate-spin text-gray-400" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggested Questions */}
      <div className="px-4 pb-2 flex gap-2 flex-wrap">
        {[
          "How's our pipeline?",
          "Top sectors by revenue",
          "Work order status summary",
          "Prepare leadership update"
        ].map((q) => (
          <button
            key={q}
            onClick={() => setInput(q)}
            className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 px-3 py-1 rounded-full transition"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-800">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask a business question..."
            className="flex-1 bg-gray-800 text-white rounded-xl px-4 py-2 text-sm outline-none focus:ring-1 focus:ring-blue-500"
          />
          <button
            onClick={sendMessage}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-xl px-4 py-2 transition"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}