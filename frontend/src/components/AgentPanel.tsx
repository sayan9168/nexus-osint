"use client";

import { useState } from "react";
import { useGraphStore } from "@/store/graphStore";
import { triggerInvestigation } from "@/lib/api";

export function AgentPanel() {
  const {
    toggleAgentPanel,
    agentStatus,
    agentReport,
    setAgentStatus,
    setAgentReport,
    addTransformLog,
  } = useGraphStore();

  const [target, setTarget] = useState("");
  const [goal, setGoal] = useState("Conduct comprehensive OSINT investigation");
  const [maxIterations, setMaxIterations] = useState(10);
  const [isRunning, setIsRunning] = useState(false);

  const handleInvestigate = async () => {
    if (!target) return;

    setIsRunning(true);
    setAgentStatus("Investigating...");
    setAgentReport("");
    addTransformLog(`[AGENT] Starting investigation: ${target}`);

    try {
      const result = await triggerInvestigation(target, goal, maxIterations);
      setAgentStatus(result.status);
      setAgentReport(result.report);
      addTransformLog(
        `[AGENT] Complete: ${result.entities_found} entities, ${result.correlations_found} correlations`
      );
    } catch (err: any) {
      setAgentStatus("error");
      setAgentReport(`Investigation failed: ${err.message}`);
      addTransformLog(`[AGENT] Error: ${err.message}`);
    }
    setIsRunning(false);
  };

  return (
    <div className="w-96 h-full bg-nexus-800/95 backdrop-blur-sm border-l border-nexus-700 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-nexus-700 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-purple-500/20 flex items-center justify-center">
            <span className="text-purple-400 text-xs">🤖</span>
          </div>
          <h2 className="text-sm font-semibold text-gray-300">AI Recon Agent</h2>
        </div>
        <button
          onClick={toggleAgentPanel}
          className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded hover:bg-gray-600"
        >
          ✕
        </button>
      </div>

      {/* Input */}
      <div className="p-4 space-y-3 border-b border-nexus-700">
        <div>
          <label className="text-xs text-gray-500 mb-1 block">Investigation Target</label>
          <input
            type="text"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="e.g., malicious-domain.com"
            className="w-full bg-nexus-900 border border-nexus-600 rounded px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:border-purple-500 focus:outline-none"
          />
        </div>

        <div>
          <label className="text-xs text-gray-500 mb-1 block">Investigation Goal</label>
          <textarea
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            rows={2}
            className="w-full bg-nexus-900 border border-nexus-600 rounded px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:border-purple-500 focus:outline-none resize-none"
          />
        </div>

        <div className="flex items-center gap-3">
          <label className="text-xs text-gray-500">Max Iterations:</label>
          <input
            type="number"
            value={maxIterations}
            onChange={(e) => setMaxIterations(Number(e.target.value))}
            min={1}
            max={20}
            className="w-16 bg-nexus-900 border border-nexus-600 rounded px-2 py-1 text-sm text-gray-200 focus:border-purple-500 focus:outline-none"
          />
        </div>

        <button
          onClick={handleInvestigate}
          disabled={isRunning || !target}
          className="w-full py-2.5 px-4 bg-purple-600 hover:bg-purple-500 disabled:bg-gray-700 disabled:text-gray-500 text-white text-sm font-medium rounded-lg transition flex items-center justify-center gap-2"
        >
          {isRunning ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Investigating...
            </>
          ) : (
            "🔍 Launch Investigation"
          )}
        </button>
      </div>

      {/* Status */}
      {agentStatus !== "idle" && (
        <div className="px-4 py-2 border-b border-nexus-700">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${
              agentStatus === "completed" ? "bg-green-400" :
              agentStatus === "error" ? "bg-red-400" :
              "bg-yellow-400 animate-pulse"
            }`} />
            <span className="text-xs text-gray-400">{agentStatus}</span>
          </div>
        </div>
      )}

      {/* Report */}
      <div className="flex-1 overflow-y-auto p-4">
        {agentReport ? (
          <div className="prose prose-invert prose-sm max-w-none">
            <pre className="whitespace-pre-wrap text-xs text-gray-300 font-mono leading-relaxed">
              {agentReport}
            </pre>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-gray-600">
            <span className="text-3xl mb-3">🕵️</span>
            <p className="text-sm text-center">
              Launch an investigation to see the AI agent's findings here.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
