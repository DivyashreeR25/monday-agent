"use client";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  PieChart, Pie, Cell, ResponsiveContainer, Legend
} from "recharts";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#f97316"];

export default function Dashboard({ chartData }: { chartData: any }) {
  return (
    <div className="flex flex-col h-full bg-gray-950 p-4 overflow-y-auto">
      {/* Header */}
      <div className="mb-4">
        <h2 className="text-white font-bold text-lg">📊 Live Dashboard</h2>
        <p className="text-gray-400 text-xs">Updates automatically when you ask questions</p>
      </div>

      {!chartData ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center">
          <div className="text-5xl mb-4">🚁</div>
          <p className="text-gray-400 text-sm">Ask a question in the chat to see live charts here</p>
          <div className="mt-6 grid grid-cols-2 gap-3 w-full max-w-sm">
            {["Total Work Orders", "Total Deals", "Active Pipeline", "Sectors"].map((label) => (
              <div key={label} className="bg-gray-800 rounded-xl p-3 text-center">
                <div className="text-2xl font-bold text-blue-400">—</div>
                <div className="text-xs text-gray-400 mt-1">{label}</div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Sector Breakdown */}
          {chartData.sectorData?.length > 0 && (
            <div className="bg-gray-900 rounded-xl p-4">
              <h3 className="text-white font-semibold text-sm mb-3">Sector Distribution</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={chartData.sectorData}>
                  <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#9ca3af" }} />
                  <YAxis tick={{ fontSize: 10, fill: "#9ca3af" }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1f2937", border: "none", borderRadius: "8px" }}
                    labelStyle={{ color: "#fff" }}
                  />
                  <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Status Breakdown */}
          {chartData.statusData?.length > 0 && (
            <div className="bg-gray-900 rounded-xl p-4">
              <h3 className="text-white font-semibold text-sm mb-3">Status Breakdown</h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={chartData.statusData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, percent = 0 }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    labelLine={false}
                  >
                    {chartData.statusData.map((_: any, index: number) => (
                      <Cell key={index} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1f2937", border: "none", borderRadius: "8px" }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}
    </div>
  );
}