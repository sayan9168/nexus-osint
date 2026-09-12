"use client";

import { useEffect, useMemo, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

type Signal = { id?: string; kind?: string; label?: string; source?: string; lat?: number; lon?: number; confidence?: number; time?: number; observed_at?: string };

async function api(path: string, token: string, options: RequestInit = {}) {
  const response = await fetch(API + path, {
    ...options,
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}`, ...(options.headers || {}) },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `HTTP ${response.status}`);
  return data;
}

export default function IntelligenceCommandCenter() {
  const [token, setToken] = useState("");
  const [signals, setSignals] = useState<Signal[]>([]);
  const [health, setHealth] = useState<any>(null);
  const [correlation, setCorrelation] = useState<any>(null);
  const [density, setDensity] = useState<any>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [graph, setGraph] = useState<any>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [caseId, setCaseId] = useState("");

  useEffect(() => {
    const t = localStorage.getItem("nexus_token") || "";
    setToken(t);
    setCaseId(new URLSearchParams(location.search).get("case") || "");
  }, []);

  async function refresh() {
    if (!token) { setError("Sign in to use the Intelligence Command Center."); return; }
    setLoading(true); setError("");
    try {
      const fused = await api("/v3/spatial/fusion", token);
      const items = fused.signals || [];
      setSignals(items);
      const [h, c, d] = await Promise.all([
        api("/v3/nextgen/health", token),
        api("/v3/nextgen/correlation", token, { method: "POST", body: JSON.stringify({ signals: items, grid_deg: 5 }) }),
        api("/v3/nextgen/density", token, { method: "POST", body: JSON.stringify({ signals: items, grid_deg: 5 }) }),
      ]);
      setHealth(h); setCorrelation(c); setDensity(d);
      if (caseId) {
        const cased = await api(`/v3/nextgen/case/${caseId}/timeline`, token);
        setTimeline(cased.timeline || []); setGraph(cased.graph || null);
      } else {
        const t = await api("/v3/nextgen/timeline", token, { method: "POST", body: JSON.stringify({ signals: items, evidence: [] }) });
        setTimeline(t.timeline || []);
        const g = await api("/v3/nextgen/graph", token, { method: "POST", body: JSON.stringify({ signals: items, entities: [], relationships: [] }) });
        setGraph(g);
      }
    } catch (e: any) { setError(e.message || "Unable to refresh intelligence data."); }
    finally { setLoading(false); }
  }

  useEffect(() => { if (token) refresh(); }, [token, caseId]);

  const topCells = useMemo(() => (density?.cells || []).slice(0, 12), [density]);
  const sourceRows = health?.sources || [];
  const graphNodes = graph?.nodes || [];
  const graphEdges = graph?.edges || [];

  return (
    <main style={{ minHeight: "100vh", background: "#03070d", color: "#dceeff", fontFamily: "Inter,system-ui", padding: 18 }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap", borderBottom: "1px solid #183246", paddingBottom: 14 }}>
        <div><b style={{ letterSpacing: 2, fontSize: 20 }}>NEXUS<span style={{ color: "#49ddff" }}>OSINT</span></b><div style={{ color: "#6f899b", fontSize: 11, marginTop: 5 }}>INTELLIGENCE COMMAND CENTER · PUBLIC SIGNAL FUSION</div></div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}><input value={caseId} onChange={e => setCaseId(e.target.value)} placeholder="Optional case ID" style={{ background: "#07131d", color: "#dceeff", border: "1px solid #1c4054", borderRadius: 6, padding: "8px 10px" }} /><button onClick={refresh} disabled={loading} style={{ background: "#0b516b", color: "white", border: 0, borderRadius: 6, padding: "8px 14px" }}>{loading ? "Refreshing…" : "Refresh Fusion"}</button></div>
      </header>
      {error && <div style={{ marginTop: 12, padding: 10, border: "1px solid #713746", background: "#241018", color: "#ffb7c3", borderRadius: 7 }}>{error}</div>}

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: 10, marginTop: 14 }}>
        {[['Signals', signals.length], ['Sources', health?.total ?? sourceRows.length], ['Clusters', correlation?.clusters?.length ?? 0], ['Heat cells', density?.cells?.length ?? 0], ['Graph nodes', graphNodes.length], ['Timeline events', timeline.length]].map(([label,value]) => <div key={String(label)} style={{ background: "#07111a", border: "1px solid #173447", borderRadius: 9, padding: 13 }}><div style={{ color: "#6e899b", fontSize: 10 }}>{label}</div><strong style={{ display: "block", fontSize: 23, marginTop: 5 }}>{value}</strong></div>)}
      </section>

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(330px,1fr))", gap: 14, marginTop: 14 }}>
        <Panel title="SOURCE HEALTH DASHBOARD"><div style={{ display: "grid", gap: 7 }}>{sourceRows.slice(0, 16).map((s: any) => <div key={s.id || s.name} style={{ display: "flex", justifyContent: "space-between", gap: 8, padding: 8, background: "#06101a", borderRadius: 6 }}><span>{s.name || s.id}</span><span style={{ color: s.status === "live" || s.status === "healthy" ? "#71f2b2" : "#ffc66d" }}>{s.status || s.access || "unknown"}</span></div>)}</div></Panel>
        <Panel title="CORRELATION ENGINE"><div style={{ display: "grid", gap: 7 }}>{(correlation?.clusters || []).slice(0, 10).map((c: any, i: number) => <div key={c.id || i} style={{ padding: 8, background: "#06101a", borderRadius: 6 }}><b>{c.id || `cluster-${i + 1}`}</b><span style={{ marginLeft: 8, color: "#7fdaef" }}>{c.signal_count || c.count || 0} signals</span><small style={{ display: "block", color: "#7893a5", marginTop: 3 }}>{(c.sources || []).join(" · ")} · confidence {Number(c.confidence || 0).toFixed(2)}</small></div>)}</div></Panel>
        <Panel title="DENSITY HEATMAP"><div style={{ display: "grid", gap: 7 }}>{topCells.map((c: any, i: number) => <div key={c.key || i} style={{ padding: 8, background: `linear-gradient(90deg, #0b516b ${Math.min(100, Number(c.weight || 0) * 100)}%, #06101a 0%)`, borderRadius: 6 }}><b>{Number(c.lat || 0).toFixed(1)}°, {Number(c.lon || 0).toFixed(1)}°</b><span style={{ float: "right" }}>{Number(c.weight || 0).toFixed(2)}</span></div>)}</div></Panel>
        <Panel title="TIMELINE FUSION"><div style={{ maxHeight: 320, overflow: "auto" }}>{timeline.slice(0, 60).map((e: any, i: number) => <div key={e.id || i} style={{ borderLeft: "2px solid #2d9fbe", padding: "6px 0 6px 10px", marginBottom: 5 }}><b style={{ fontSize: 11 }}>{e.title || e.label || e.kind || "Event"}</b><small style={{ display: "block", color: "#718b9c" }}>{e.timestamp || e.observed_at || "unknown time"} · {e.source || "derived"}</small></div>)}</div></Panel>
      </section>

      <section style={{ marginTop: 14 }}><Panel title="EVIDENCE GRAPH"><div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}><div><h4 style={{ margin: "0 0 8px" }}>Nodes ({graphNodes.length})</h4>{graphNodes.slice(0, 80).map((n: any, i: number) => <div key={n.id || i} style={{ fontSize: 10, padding: 5, borderBottom: "1px solid #102533" }}>{n.label || n.id} <span style={{ color: "#6e899b" }}>· {n.type || n.kind || "entity"}</span></div>)}</div><div><h4 style={{ margin: "0 0 8px" }}>Relationships ({graphEdges.length})</h4>{graphEdges.slice(0, 80).map((e: any, i: number) => <div key={i} style={{ fontSize: 10, padding: 5, borderBottom: "1px solid #102533" }}>{String(e.source)} <span style={{ color: "#50cce9" }}>→ {e.type || "related"} →</span> {String(e.target)}</div>)}</div></div></Panel></section>
      <footer style={{ marginTop: 14, color: "#60798b", fontSize: 10 }}>Public-source intelligence only. Correlation and propagation are analytical/derived signals, not proof of identity or ground truth. No private-account access, credential collection, face recognition, or named-person tracking.</footer>
    </main>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return <div style={{ background: "#050d15", border: "1px solid #173447", borderRadius: 9, padding: 13 }}><h3 style={{ margin: "0 0 10px", fontSize: 11, letterSpacing: 1.5, color: "#7fdcf2" }}>{title}</h3>{children}</div>;
}
