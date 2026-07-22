"use client";

import { useGraphStore } from "@/store/graphStore";
import { NODE_COLORS } from "@/lib/types";

const ALL_TYPES = [
  "Domain", "IP", "Email", "Hash",
  "Wallet", "Person", "SocialHandle", "DarknetForumPost",
];

export function EntityFilter() {
  const { activeFilters, toggleFilter, nodes } = useGraphStore();

  const countByType = (type: string) =>
    nodes.filter((n) => n.label === type).length;

  return (
    <div className="space-y-4">
      <h3 className="text-xs font-semibold text-gray-400 uppercase">Entity Type Filters</h3>
      <p className="text-xs text-gray-600">Toggle visibility of entity types in the 3D graph.</p>

      <div className="space-y-2">
        {ALL_TYPES.map((type) => {
          const isActive = activeFilters.has(type);
          const count = countByType(type);
          const color = NODE_COLORS[type] || "#6b7280";

          return (
            <button
              key={type}
              onClick={() => toggleFilter(type)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg border transition text-left ${
                isActive
                  ? "border-nexus-600 bg-nexus-700/50"
                  : "border-transparent bg-transparent opacity-50"
              }`}
            >
              {/* Color indicator */}
              <div
                className="w-3 h-3 rounded-full flex-shrink-0"
                style={{ backgroundColor: color, opacity: isActive ? 1 : 0.3 }}
              />

              {/* Label */}
              <span className={`text-sm flex-1 ${isActive ? "text-gray-200" : "text-gray-500"}`}>
                {type}
              </span>

              {/* Count */}
              <span className="text-xs text-gray-500 font-mono">{count}</span>

              {/* Toggle indicator */}
              <div className={`w-8 h-4 rounded-full relative transition ${
                isActive ? "bg-cyan-500/30" : "bg-gray-700"
              }`}>
                <div className={`absolute top-0.5 w-3 h-3 rounded-full transition-all ${
                  isActive ? "left-4 bg-cyan-400" : "left-0.5 bg-gray-500"
                }`} />
              </div>
            </button>
          );
        })}
      </div>

      {/* Quick actions */}
      <div className="flex gap-2 pt-2">
        <button
          onClick={() => ALL_TYPES.forEach((t) => { if (!activeFilters.has(t)) toggleFilter(t); })}
          className="flex-1 py-1.5 text-xs bg-nexus-700 text-gray-300 rounded hover:bg-nexus-600 transition"
        >
          Show All
        </button>
        <button
          onClick={() => ALL_TYPES.forEach((t) => { if (activeFilters.has(t)) toggleFilter(t); })}
          className="flex-1 py-1.5 text-xs bg-nexus-700 text-gray-300 rounded hover:bg-nexus-600 transition"
        >
          Hide All
        </button>
      </div>
    </div>
  );
}
