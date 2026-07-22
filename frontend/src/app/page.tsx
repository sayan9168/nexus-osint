"use client";

import dynamic from "next/dynamic";
import { Sidebar } from "@/components/Sidebar";
import { AgentPanel } from "@/components/AgentPanel";
import { useGraphStore } from "@/store/graphStore";

// Dynamically import 3D graph (SSR incompatible)
const Graph3D = dynamic(() => import("@/components/Graph3D"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-screen bg-nexus-900">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-cyan-400 mx-auto mb-4" />
        <p className="text-cyan-400 text-lg">Initializing 3D Graph Engine...</p>
      </div>
    </div>
  ),
});

export default function Home() {
  const { sidebarOpen, agentPanelOpen } = useGraphStore();

  return (
    <main className="relative h-screen w-screen overflow-hidden bg-nexus-900">
      {/* 3D Graph (full screen background) */}
      <div className="absolute inset-0 z-0">
        <Graph3D />
      </div>

      {/* Sidebar (left) */}
      {sidebarOpen && (
        <div className="absolute left-0 top-0 h-full z-20">
          <Sidebar />
        </div>
      )}

      {/* Agent Panel (right) */}
      {agentPanelOpen && (
        <div className="absolute right-0 top-0 h-full z-20">
          <AgentPanel />
        </div>
      )}

      {/* Top Bar */}
      <header className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between px-6 py-3 bg-gradient-to-b from-nexus-900/95 to-transparent">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center">
            <span className="text-cyan-400 font-bold text-sm">N</span>
          </div>
          <h1 className="text-lg font-semibold text-white">
            NEXUS<span className="text-cyan-400">-OSINT</span>
          </h1>
          <span className="text-xs text-gray-500 ml-2">v1.0.0</span>
        </div>

        <div className="flex items-center gap-4">
          <ConnectionStatus />
        </div>
      </header>
    </main>
  );
}

function ConnectionStatus() {
  const { wsConnected } = useGraphStore();
  return (
    <div className="flex items-center gap-2">
      <div
        className={`w-2 h-2 rounded-full ${
          wsConnected ? "bg-green-400 animate-pulse" : "bg-red-400"
        }`}
      />
      <span className="text-xs text-gray-400">
        {wsConnected ? "Live" : "Disconnected"}
      </span>
    </div>
  );
}
