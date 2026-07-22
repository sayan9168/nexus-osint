"use client";

import { useState, useEffect } from "react";
import { useGraphStore } from "@/store/graphStore";
import { TransformControls } from "./TransformControls";
import { EntityFilter } from "./EntityFilter";
import { NodeInspector } from "./NodeInspector";
import { listTransforms, fetchFullGraph } from "@/lib/api";

export function Sidebar() {
  const {
    toggleSidebar,
    toggleAgentPanel,
    setTransforms,
    setGraphData,
    setLoading,
    nodes,
    edges,
  } = useGraphStore();

  const [activeTab, setActiveTab] = useState<"transforms" | "filters" | "inspector">("transforms");

  useEffect(() => {
    // Load transforms and initial graph
    async function init() {
      setLoading(true);
      try {
        const [transforms, graph] = await Promise.all([
          listTransforms(),
          fetchFullGraph(),
        ]);
        setTransforms(transforms);
        setGraphData(graph.nodes, graph.edges);
      } catch (e) {
        console.error("Init error:", e);
      }
      setLoading(false);
    }
    init();
  }, []);

  return (
    <div className="w-80 h-full bg-nexus-800/95 backdrop-blur-sm border-r border-nexus-700 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-nexus-700">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">
            Control Panel
          </h2>
          <div className="flex gap-2">
            <button
              onClick={toggleAgentPanel}
              className="px-2 py-1 text-xs bg-cyan-500/20 text-cyan-400 rounded hover:bg-cyan-500/30 transition"
            >
              AI Agent
            </button>
            <button
              onClick={toggleSidebar}
              className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded hover:bg-gray-600 transition"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="mt-3 flex gap-4 text-xs text-gray-500">
          <span>Nodes: <span className="text-cyan-400">{nodes.length}</span></span>
          <span>Edges: <span className="text-amber-400">{edges.length}</span></span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-nexus-700">
        {(["transforms", "filters", "inspector"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 px-3 py-2 text-xs font-medium capitalize transition ${
              activeTab === tab
                ? "text-cyan-400 border-b-2 border-cyan-400 bg-cyan-500/5"
                : "text-gray-500 hover:text-gray-300"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === "transforms" && <TransformControls />}
        {activeTab === "filters" && <EntityFilter />}
        {activeTab === "inspector" && <NodeInspector />}
      </div>
    </div>
  );
}
