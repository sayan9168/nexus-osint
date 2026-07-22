"use client";

import { useEffect, useRef, useCallback, useMemo } from "react";
import ForceGraph3D from "react-force-graph-3d";
import * as THREE from "three";
import { useGraphStore } from "@/store/graphStore";
import { useWebSocket } from "@/hooks/useWebSocket";
import { NODE_COLORS, NODE_SIZES } from "@/lib/types";
import type { GraphNode } from "@/lib/types";

export default function Graph3D() {
  const fgRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { nodes, edges, activeFilters, selectedNode, setSelectedNode } = useGraphStore();

  // Initialize WebSocket connection
  useWebSocket();

  // Filter nodes based on active filters
  const filteredData = useMemo(() => {
    const filteredNodes = nodes.filter((n) => activeFilters.has(n.label));
    const nodeIds = new Set(filteredNodes.map((n) => n.id));
    const filteredEdges = edges.filter(
      (e) => nodeIds.has(e.source) && nodeIds.has(e.target)
    );
    return { nodes: filteredNodes, links: filteredEdges };
  }, [nodes, edges, activeFilters]);

  // Handle node click
  const handleNodeClick = useCallback(
    (node: any) => {
      setSelectedNode(node as GraphNode);
      // Focus camera on node
      if (fgRef.current) {
        const distance = 120;
        const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);
        fgRef.current.cameraPosition(
          { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio },
          { x: node.x, y: node.y, z: node.z },
          1000
        );
      }
    },
    [setSelectedNode]
  );

  // Custom node rendering (3D spheres with labels)
  const nodeThreeObject = useCallback((node: any) => {
    const color = NODE_COLORS[node.label] || "#6b7280";
    const size = NODE_SIZES[node.label] || 5;

    const group = new THREE.Group();

    // Sphere
    const geometry = new THREE.SphereGeometry(size, 16, 16);
    const material = new THREE.MeshPhongMaterial({
      color: new THREE.Color(color),
      emissive: new THREE.Color(color),
      emissiveIntensity: 0.3,
      transparent: true,
      opacity: 0.9,
    });
    const sphere = new THREE.Mesh(geometry, material);
    group.add(sphere);

    // Glow ring for selected node
    if (selectedNode?.id === node.id) {
      const ringGeo = new THREE.RingGeometry(size + 2, size + 4, 32);
      const ringMat = new THREE.MeshBasicMaterial({
        color: 0xffffff,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.6,
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      group.add(ring);
    }

    return group;
  }, [selectedNode]);

  // Node label sprite
  const nodeLabel = useCallback((node: any) => {
    return `<div style="
      background: rgba(0,0,0,0.8);
      color: ${NODE_COLORS[node.label] || '#fff'};
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-family: monospace;
      border: 1px solid ${NODE_COLORS[node.label] || '#333'};
    ">
      <strong>${node.label}</strong><br/>
      ${node.value}
    </div>`;
  }, []);

  // Link styling
  const linkColor = useCallback((link: any) => {
    const typeColors: Record<string, string> = {
      RESOLVES_TO: "#06b6d4",
      OWNS: "#ec4899",
      LINKED_TO: "#6b7280",
      COMMUNICATES_WITH: "#f59e0b",
      TRANSACTED_WITH: "#8b5cf6",
    };
    return typeColors[link.type] || "#374151";
  }, []);

  // Configure force engine for 100k+ nodes
  useEffect(() => {
    if (fgRef.current) {
      fgRef.current.d3Force("charge")?.strength(-50);
      fgRef.current.d3Force("link")?.distance(30);
      fgRef.current.d3Force("center")?.strength(0.05);

      // Performance: reduce iterations for large graphs
      if (filteredData.nodes.length > 10000) {
        fgRef.current.d3AlphaDecay(0.05);
        fgRef.current.d3VelocityDecay(0.4);
      }
    }
  }, [filteredData.nodes.length]);

  return (
    <div ref={containerRef} className="w-full h-full">
      <ForceGraph3D
        ref={fgRef}
        graphData={filteredData}
        backgroundColor="#0a0e1a"
        nodeThreeObject={nodeThreeObject}
        nodeThreeObjectExtend={false}
        nodeLabel={nodeLabel}
        nodeOpacity={0.9}
        nodeResolution={16}
        linkColor={linkColor}
        linkWidth={1.5}
        linkOpacity={0.4}
        linkDirectionalParticles={2}
        linkDirectionalParticleWidth={2}
        linkDirectionalParticleSpeed={0.005}
        onNodeClick={handleNodeClick}
        onNodeHover={(node: any) => {
          if (containerRef.current) {
            containerRef.current.style.cursor = node ? "pointer" : "default";
          }
        }}
        // Performance settings for 100k+ nodes
        numDimensions={3}
        warmupTicks={50}
        cooldownTicks={100}
        d3AlphaDecay={0.02}
        d3VelocityDecay={0.3}
        // Camera
        showNavInfo={false}
        enableNodeDrag={true}
        enableNavigationControls={true}
      />
    </div>
  );
}
