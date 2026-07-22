"use client";

import { useGraphStore } from "@/store/graphStore";
import { NODE_COLORS } from "@/lib/types";
import { deleteEntity } from "@/lib/api";

export function NodeInspector() {
  const { selectedNode, setSelectedNode, edges } = useGraphStore();

  if (!selectedNode) {
    return (
      <div className="flex flex-col items-center justify-center h-40 text-gray-600">
        <div className="w-12 h-12 rounded-full border-2 border-dashed border-gray-700 flex items-center justify-center mb-3">
          <span className="text-lg">◎</span>
        </div>
        <p className="text-sm">Click a node in the 3D graph to inspect</p>
      </div>
    );
  }

  const color = NODE_COLORS[selectedNode.label] || "#6b7280";
  const connections = edges.filter(
    (e) => e.source === selectedNode.id || e.target === selectedNode.id
  );

  const handleDelete = async () => {
    if (confirm(`Delete ${selectedNode.value}?`)) {
      try {
        await deleteEntity(selectedNode.id);
        setSelectedNode(null);
      } catch (e) {
        console.error("Delete failed:", e);
      }
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div
          className="w-4 h-4 rounded-full"
          style={{ backgroundColor: color }}
        />
        <div>
          <h3 className="text-sm font-semibold text-white">{selectedNode.label}</h3>
          <p className="text-xs text-gray-500 font-mono">{selectedNode.value}</p>
        </div>
      </div>

      {/* Properties */}
      <div className="bg-nexus-900 rounded-lg p-3 space-y-2">
        <h4 className="text-xs font-semibold text-gray-400 uppercase">Properties</h4>
        {Object.entries(selectedNode.properties || {}).map(([key, value]) => (
          <div key={key} className="flex justify-between text-xs">
            <span className="text-gray-500">{key}</span>
            <span className="text-gray-300 font-mono truncate max-w-[150px]">
              {typeof value === "object" ? JSON.stringify(value) : String(value)}
            </span>
          </div>
        ))}
      </div>

      {/* Connections */}
      <div className="bg-nexus-900 rounded-lg p-3">
        <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">
          Connections ({connections.length})
        </h4>
        <div className="space-y-1 max-h-32 overflow-y-auto">
          {connections.map((edge, i) => (
            <div key={i} className="text-xs text-gray-500 flex items-center gap-2">
              <span className="text-cyan-400">{edge.type}</span>
              <span>→</span>
              <span className="font-mono truncate">
                {edge.source === selectedNode.id ? edge.target : edge.source}
              </span>
            </div>
          ))}
          {connections.length === 0 && (
            <p className="text-xs text-gray-600">No connections</p>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button
          onClick={handleDelete}
          className="flex-1 py-2 text-xs bg-red-500/10 text-red-400 border border-red-500/30 rounded hover:bg-red-500/20 transition"
        >
          Delete Node
        </button>
        <button
          onClick={() => setSelectedNode(null)}
          className="flex-1 py-2 text-xs bg-nexus-700 text-gray-300 rounded hover:bg-nexus-600 transition"
        >
          Deselect
        </button>
      </div>
    </div>
  );
}
