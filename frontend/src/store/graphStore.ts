import { create } from "zustand";
import type { GraphNode, GraphEdge, TransformInfo } from "@/lib/types";

interface GraphState {
  // Graph data
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedNode: GraphNode | null;

  // UI state
  sidebarOpen: boolean;
  agentPanelOpen: boolean;
  wsConnected: boolean;
  isLoading: boolean;

  // Filters
  activeFilters: Set<string>;
  searchQuery: string;

  // Transforms
  transforms: TransformInfo[];
  transformLog: string[];

  // Agent
  agentStatus: string;
  agentReport: string;

  // Actions
  setGraphData: (nodes: GraphNode[], edges: GraphEdge[]) => void;
  addNode: (node: GraphNode) => void;
  addEdge: (edge: GraphEdge) => void;
  setSelectedNode: (node: GraphNode | null) => void;
  toggleSidebar: () => void;
  toggleAgentPanel: () => void;
  setWsConnected: (connected: boolean) => void;
  setLoading: (loading: boolean) => void;
  toggleFilter: (label: string) => void;
  setSearchQuery: (query: string) => void;
  setTransforms: (transforms: TransformInfo[]) => void;
  addTransformLog: (log: string) => void;
  setAgentStatus: (status: string) => void;
  setAgentReport: (report: string) => void;
}

export const useGraphStore = create<GraphState>((set, get) => ({
  // Initial state
  nodes: [],
  edges: [],
  selectedNode: null,
  sidebarOpen: true,
  agentPanelOpen: false,
  wsConnected: false,
  isLoading: false,
  activeFilters: new Set(["Domain", "IP", "Email", "Hash", "Wallet", "Person", "SocialHandle", "DarknetForumPost"]),
  searchQuery: "",
  transforms: [],
  transformLog: [],
  agentStatus: "idle",
  agentReport: "",

  // Actions
  setGraphData: (nodes, edges) => set({ nodes, edges }),

  addNode: (node) =>
    set((state) => {
      const exists = state.nodes.some((n) => n.id === node.id);
      if (exists) return state;
      return { nodes: [...state.nodes, node] };
    }),

  addEdge: (edge) =>
    set((state) => ({ edges: [...state.edges, edge] })),

  setSelectedNode: (node) => set({ selectedNode: node }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  toggleAgentPanel: () => set((state) => ({ agentPanelOpen: !state.agentPanelOpen })),
  setWsConnected: (connected) => set({ wsConnected: connected }),
  setLoading: (loading) => set({ isLoading: loading }),

  toggleFilter: (label) =>
    set((state) => {
      const newFilters = new Set(state.activeFilters);
      if (newFilters.has(label)) {
        newFilters.delete(label);
      } else {
        newFilters.add(label);
      }
      return { activeFilters: newFilters };
    }),

  setSearchQuery: (query) => set({ searchQuery: query }),
  setTransforms: (transforms) => set({ transforms }),

  addTransformLog: (log) =>
    set((state) => ({
      transformLog: [...state.transformLog.slice(-49), log],
    })),

  setAgentStatus: (status) => set({ agentStatus: status }),
  setAgentReport: (report) => set({ agentReport: report }),
}));
