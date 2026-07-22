"use client";

import { useState } from "react";
import { useGraphStore } from "@/store/graphStore";
import { executeTransform } from "@/lib/api";
import { NODE_COLORS } from "@/lib/types";

export function TransformControls() {
  const { transforms, addTransformLog, addNode, addEdge } = useGraphStore();
  const [selectedTransform, setSelectedTransform] = useState("");
  const [entityValue, setEntityValue] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleExecute = async () => {
    if (!selectedTransform || !entityValue) return;

    setIsRunning(true);
    setResult(null);
    addTransformLog(`[RUN] ${selectedTransform} → ${entityValue}`);

    try {
      const res = await executeTransform(selectedTransform, "Domain", entityValue);
      setResult(res);
      addTransformLog(
        `[OK] ${res.transform_name}: +${res.new_nodes?.length || 0} nodes, +${res.new_edges?.length || 0} edges`
      );

      // Add new nodes/edges to graph
      (res.new_nodes || []).forEach((n: any) => {
        addNode({
          id: `${n.label}:${n.value}:${Date.now()}`,
          label: n.label,
          value: n.value,
          properties: n,
        });
      });
      (res.new_edges || []).forEach((e: any) => {
        addEdge({
          source: e.source_value,
          target: e.target_value,
          type: e.edge_type,
          properties: e.properties || {},
        });
      });
    } catch (err: any) {
      addTransformLog(`[ERR] ${err.message}`);
      setResult({ status: "error", error_message: err.message });
    }
    setIsRunning(false);
  };

  return (
    <div className="space-y-4">
      <h3 className="text-xs font-semibold text-gray-400 uppercase">Run Transform</h3>

      {/* Transform selector */}
      <div>
        <label className="text-xs text-gray-500 mb-1 block">Transform</label>
        <select
          value={selectedTransform}
          onChange={(e) => setSelectedTransform(e.target.value)}
          className="w-full bg-nexus-900 border border-nexus-600 rounded px-3 py-2 text-sm text-gray-200 focus:border-cyan-500 focus:outline-none"
        >
          <option value="">Select transform...</option>
          {transforms.map((t) => (
            <option key={t.name} value={t.name}>
              {t.name} ({t.input_type} → {t.output_types.join(", ")})
            </option>
          ))}
        </select>
      </div>

      {/* Entity input */}
      <div>
        <label className="text-xs text-gray-500 mb-1 block">Target Entity</label>
        <input
          type="text"
          value={entityValue}
          onChange={(e) => setEntityValue(e.target.value)}
          placeholder="e.g., example.com"
          className="w-full bg-nexus-900 border border-nexus-600 rounded px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:border-cyan-500 focus:outline-none"
          onKeyDown={(e) => e.key === "Enter" && handleExecute()}
        />
      </div>

      {/* Execute button */}
      <button
        onClick={handleExecute}
        disabled={isRunning || !selectedTransform || !entityValue}
        className="w-full py-2 px-4 bg-cyan-600 hover:bg-cyan-500 disabled:bg-gray-700 disabled:text-gray-500 text-white text-sm font-medium rounded transition flex items-center justify-center gap-2"
      >
        {isRunning ? (
          <>
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Executing...
          </>
        ) : (
          "▶ Execute Transform"
        )}
      </button>

      {/* Result */}
      {result && (
        <div className={`p-3 rounded text-xs ${
          result.status === "success"
            ? "bg-green-500/10 border border-green-500/30 text-green-400"
            : "bg-red-500/10 border border-red-500/30 text-red-400"
        }`}>
          <p className="font-medium mb-1">
            {result.status === "success" ? "✓ Success" : "✗ Error"}
          </p>
          {result.new_nodes && (
            <p>Nodes discovered: {result.new_nodes.length}</p>
          )}
          {result.new_edges && (
            <p>Edges discovered: {result.new_edges.length}</p>
          )}
          {result.execution_time_ms && (
            <p>Time: {result.execution_time_ms.toFixed(0)}ms</p>
          )}
          {result.error_message && (
            <p className="mt-1">{result.error_message}</p>
          )}
        </div>
      )}

      {/* Transform log */}
      <TransformLog />
    </div>
  );
}

function TransformLog() {
  const { transformLog } = useGraphStore();

  if (transformLog.length === 0) return null;

  return (
    <div className="mt-4">
      <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">Activity Log</h4>
      <div className="space-y-1 max-h-40 overflow-y-auto font-mono text-[10px]">
        {transformLog.slice().reverse().map((log, i) => (
          <div key={i} className="text-gray-500 py-0.5 border-b border-nexus-700/50">
            {log}
          </div>
        ))}
      </div>
    </div>
  );
}
