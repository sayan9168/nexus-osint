"use client";

import { useEffect, useRef, useCallback } from "react";
import { useGraphStore } from "@/store/graphStore";
import type { WSMessage, GraphNode, GraphEdge } from "@/lib/types";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout>();
  const {
    setGraphData,
    addNode,
    addEdge,
    setWsConnected,
    addTransformLog,
    setAgentStatus,
  } = useGraphStore();

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(`${WS_URL}/ws/graph`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("[WS] Connected to NEXUS graph stream");
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const msg: WSMessage = JSON.parse(event.data);
        handleMessage(msg);
      } catch (e) {
        console.error("[WS] Parse error:", e);
      }
    };

    ws.onclose = () => {
      console.log("[WS] Disconnected. Reconnecting in 3s...");
      setWsConnected(false);
      reconnectTimeout.current = setTimeout(connect, 3000);
    };

    ws.onerror = (err) => {
      console.error("[WS] Error:", err);
      ws.close();
    };
  }, []);

  const handleMessage = (msg: WSMessage) => {
    switch (msg.type) {
      case "graph_snapshot":
        const { nodes, edges } = msg.data;
        setGraphData(
          (nodes || []).map((n: any) => ({
            id: n.id,
            label: n.labels?.[0] || "Unknown",
            value: n.props?.value || "",
            properties: n.props || {},
          })),
          (edges || []).map((e: any) => ({
            source: e.source,
            target: e.target,
            type: e.type,
            properties: e.props || {},
          }))
        );
        break;

      case "node_added":
        addNode(msg.data as GraphNode);
        addTransformLog(`[NODE] ${msg.data.label}: ${msg.data.value}`);
        break;

      case "edge_added":
        addEdge(msg.data as GraphEdge);
        break;

      case "transform_started":
        addTransformLog(`[START] ${msg.data.transform} → ${msg.data.entity}`);
        break;

      case "transform_completed":
        addTransformLog(
          `[DONE] ${msg.data.transform_name}: ${msg.data.new_nodes?.length || 0} nodes, ${msg.data.new_edges?.length || 0} edges (${msg.data.execution_time_ms?.toFixed(0)}ms)`
        );
        break;

      case "agent_update":
        setAgentStatus(msg.data.message);
        break;
    }
  };

  const sendMessage = useCallback((msg: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg));
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { sendMessage };
}
