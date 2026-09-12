export interface GraphNode {
  id: string;
  label: string;
  value: string;
  properties?: Record<string, unknown>;
  x?: number;
  y?: number;
  z?: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  properties?: Record<string, unknown>;
}

export interface TransformInfo {
  name: string;
  input_type: string;
  output_types: string[];
  description?: string;
}

export type WSMessage = {
  type: "graph_snapshot" | "node_added" | "edge_added" | "transform_started" | "transform_completed" | "agent_update" | string;
  data: any;
};

export const NODE_COLORS: Record<string, string> = {
  Domain: "#22d3ee",
  IP: "#60a5fa",
  Email: "#a78bfa",
  Hash: "#f472b6",
  Wallet: "#fbbf24",
  Person: "#fb7185",
  SocialHandle: "#34d399",
  DarknetForumPost: "#f97316",
};

export const NODE_SIZES: Record<string, number> = {
  Domain: 4,
  IP: 4,
  Email: 4,
  Hash: 3.5,
  Wallet: 4,
  Person: 4.5,
  SocialHandle: 3.5,
  DarknetForumPost: 3,
  default: 3.5,
};
