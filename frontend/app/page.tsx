"use client";
import { useState } from "react";
import ChatPanel from "../components/ChatPanel";
import Dashboard from "../components/Dashboard";

export default function Home() {
  const [chartData, setChartData] = useState(null);

  return (
    <main className="flex h-screen bg-gray-950 text-white overflow-hidden">
      {/* Left - Chat */}
      <div className="w-1/2 border-r border-gray-800">
        <ChatPanel onChartData={setChartData} />
      </div>
      {/* Right - Dashboard */}
      <div className="w-1/2">
        <Dashboard chartData={chartData} />
      </div>
    </main>
  );
}