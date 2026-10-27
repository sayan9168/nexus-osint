"use client";
import {useEffect,useMemo,useRef,useState} from "react";
import {useRouter} from "next/navigation";
const API=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000/api/v1";
type Case={id:string,name:string,description:string,status:string,workflow:string,authorized:boolean,tags:string[],targets:string[],evidence:any[],notes:any[]};
async function api(path:string,token:string,options:RequestInit={}){const r=await fetch(API+path,{...options,headers:{"Content-Type":"application/json",Authorization:`Bearer ${token}`,...(options.headers||{})}});const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.detail||`HTTP ${r.status}`);return d}
const TABS=[{id:"overview",label:"Overview",icon:"◈"},{id:"evidence",label:"Evidence",icon:"⬢"},{id:"lab",label:"NEXUS LAB",icon:"⬣",badge:"NEW"},{id:"omni",label:"OMNI",icon:"⬔",badge:"45+"},{id:"entities",label:"Entities",icon:"⬡"},{id:"jobs",label:"Jobs",icon:"⚡"},{id:"graph",label:"Graph",icon:"◎"},{id:"timeline",label:"Timeline",icon:"◷"},{id:"score",label:"Score",icon:"◆"},{id:"reports",label:"Reports",icon:"▭"},{id:"audit",label:"Audit",icon:"⬔"},{id:"intel",label:"Intel",icon:"⬢"},{id:"workflow",label:"Workflow",icon:"✦"}] as const;
const LABS=[{id:"prism",label:"Prism Vault",icon:"◆",desc:"Holographic evidence"},{id:"neural",label:"Neural Mesh",icon:"⟁",desc:"Inferred correlations"},{id:"shadow",label:"Shadow 360",icon:"⬢",desc:"6-axis profile"},{id:"prophet",label:"Prophet",icon:"◈",desc:"Causality + forecast"},{id:"quantum",label:"Quantum",icon:"⌖",desc:"NL → graph"}] as const;

export default function Home(){
 const router=useRouter();
 const [token,setToken]=useState("");const [user,setUser]=useState<any>(null);const [login,setLogin]=useState(true);const [username,setUsername]=useState("");const [password,setPassword]=useState("");
 const [cases,setCases]=useState<Case[]>([]);const [selected,setSelected]=useState<Case|null>(null);
 const [target,setTarget]=useState("");const [tab,setTab]=useState("overview");
 const [jobs,setJobs]=useState<any[]>([]);const [intel,setIntel]=useState<any>(null);const [audit,setAudit]=useState<any[]>([]);const [entities,setEntities]=useState<any[]>([]);const [meta,setMeta]=useState<any>(null);const [tags,setTags]=useState("");const [busy,setBusy]=useState(false);const [error,setError]=useState("");const [q,setQ]=useState("");const [sideOpen,setSideOpen]=useState(false);
 // LAB states
 const [labTab,setLabTab]=useState("prism");
 const [prism,setPrism]=useState<any>(null); const [neural,setNeural]=useState<any>(null); const [neuralThr,setNeuralThr]=useState(0.52);
 const [shadowId,setShadowId]=useState(""); const [shadow,setShadow]=useState<any>(null);
 const [prophet,setProphet]=useState<any>(null);
 const [quantumQ,setQuantumQ]=useState("who owns this domain and what else is linked?"); const [quantum,setQuantum]=useState<any>(null);
 const [copilotOpen,setCopilotOpen]=useState(false); const [copilotQ,setCopilotQ]=useState("summarize this case"); const [copilotMsgs,setCopilotMsgs]=useState<{q:string,a:string}[]>([]);
 // OMNI states
 const [omniCat,setOmniCat]=useState<any>(null); const [omniFilter,setOmniFilter]=useState("all"); const [omniTarget,setOmniTarget]=useState(""); const [omniType,setOmniType]=useState("domain"); const [omniRes,setOmniRes]=useState<any>(null); const [omniBusy,setOmniBusy]=useState(false);
 const targetType=useMemo(()=> target.includes("@")?"email": target.startsWith("http")?"url": /^([0-9]{1,3}\.){3}[0-9]{1,3}$/.test(target.trim())?"ip": target.trim().includes(".")?"domain": "target",[target]);
 const score= useMemo(()=> selected?.evidence?.length? Math.round(selected.evidence.reduce((a:any,e:any)=>a+Number(e.confidence||0),0)/selected.evidence.length*100):0,[selected]);
 useEffect(()=>{const t=localStorage.getItem("nexus_token");if(t){setToken(t);api("/auth/me",t).then(x=>{setUser(x.user);loadCases(t)}).catch(()=>localStorage.removeItem("nexus_token"))}},[]);
 async function loadCases(t=token){try{const c=await api("/cases/",t);setCases(c);setSelected(s=>s&&c.find((x:Case)=>x.id===s.id)||c[0]||null)}catch(e:any){setError(e.message)}}
 async function auth(){setBusy(true);setError("");try{const d=await api(`/auth/${login?"login":"register"}`,"",{method:"POST",body:JSON.stringify({username,password})});setToken(d.token);setUser(d.user);localStorage.setItem("nexus_token",d.token);await loadCases(d.token)}catch(e:any){setError(e.message)}finally{setBusy(false)}}
 async function createCase(){try{const c=await api("/cases/",token,{method:"POST",body:JSON.stringify({name:`Investigation — ${new Date().toLocaleDateString()}`,description:"Authorized public-source OSINT investigation",authorized:true})});setCases(x=>[c,...x]);setSelected(c)}catch(e:any){setError(e.message)}}
 async function addTarget(){if(!selected||!target.trim())return;try{const c=await api(`/cases/${selected.id}/targets`,token,{method:"POST",body:JSON.stringify({target:target.trim()})});setSelected(c);setCases(x=>x.map(v=>v.id===c.id?c:v));setError("")}catch(e:any){setError(e.message)}}
 async function scan(){if(!selected||!target.trim())return;setBusy(true);try{await api("/platform/jobs",token,{method:"POST",body:JSON.stringify({case_id:selected.id,target:target.trim(),target_type:targetType,authorized:true})});await addTarget();setTab("jobs");await pollJobs()}catch(e:any){setError(e.message)}finally{setBusy(false)}}
 async function pollJobs(){try{const d=await api("/platform/jobs",token);setJobs(d.jobs)}catch(e:any){setError(e.message)}}
 async function loadTab(t:string){setTab(t); try{
   if(t==="omni"){
     try{ setOmniCat(await api(`/v3/omni/catalog`,token)); }catch(e:any){setError(e.message)}
     if(target) setOmniTarget(target);
     return;
   }
   if(!selected) return;
   if(t==="audit")setAudit((await api("/platform/audit",token)).events);if(t==="jobs")await pollJobs();if(t==="intel"&&target)setIntel(await api("/intelligence/dns-rdap",token,{method:"POST",body:JSON.stringify({domain:target.replace(/^https?:\/\//,"").split("/")[0]})}));if(t==="entities")setEntities((await api(`/intelligence/entities/${selected.id}`,token)).entities||[]);if(t==="workflow")setMeta(await api(`/workflow/${selected.id}/meta`,token));if(t==="lab"){ // preload prism
   try{ setPrism(await api(`/v3/lab/prism/${selected.id}`,token)); }catch{}
   try{ if(!entities.length) setEntities((await api(`/intelligence/entities/${selected.id}`,token)).entities||[]); }catch{}
 }}catch(e:any){setError(e.message)}}
 async function saveMeta(){if(!selected)return;try{const m=await api(`/workflow/${selected.id}/meta`,token,{method:"PATCH",body:JSON.stringify({tags:tags.split(",").map(x=>x.trim()).filter(Boolean),workflow:meta?.workflow,status:meta?.status})});setMeta(m);await loadCases()}catch(e:any){setError(e.message)}}
 async function closeCase(){if(!selected)return;try{const c=await api(`/cases/${selected.id}/close`,token,{method:"POST"});setSelected(c);await loadCases()}catch(e:any){setError(e.message)}}
 async function downloadReport(kind:"md"|"html"|"json"){if(!selected)return;try{const path=kind==="json"?`/reports/${selected.id}.json`:`/reports/${selected.id}.${kind}`;const r=await fetch(API+path,{headers:{Authorization:`Bearer ${token}`}});if(!r.ok)throw new Error(`Report HTTP ${r.status}`);const blob=await r.blob();const url=URL.createObjectURL(blob);window.open(url,"_blank","noopener,noreferrer");setTimeout(()=>URL.revokeObjectURL(url),60000)}catch(e:any){setError(e.message)}}
 function openSpatial(){if(!selected){setError("Select a case first — spatial layers are case-aware.");return}router.push(`/spatial?case=${encodeURIComponent(selected.id)}`)}

 // LAB fetchers
 async function fetchPrism(){if(!selected)return;try{setPrism(await api(`/v3/lab/prism/${selected.id}`,token))}catch(e:any){setError(e.message)}}
 async function fetchNeural(){if(!selected)return;try{setNeural(await api(`/v3/lab/neural/${selected.id}`,token,{method:"POST",body:JSON.stringify({threshold:neuralThr})}))}catch(e:any){setError(e.message)}}
 async function fetchShadow(){if(!selected||!shadowId) return;try{setShadow(await api(`/v3/lab/shadow/${selected.id}/${encodeURIComponent(shadowId)}`,token))}catch(e:any){setError(e.message)}}
 async function fetchProphet(){if(!selected)return;try{setProphet(await api(`/v3/lab/prophet/${selected.id}?horizon=3`,token))}catch(e:any){setError(e.message)}}
 async function fetchQuantum(){if(!selected||!quantumQ.trim())return;try{setQuantum(await api(`/v3/lab/quantum/${selected.id}`,token,{method:"POST",body:JSON.stringify({query:quantumQ})}))}catch(e:any){setError(e.message)}}
 async function askCopilot(){if(!selected||!copilotQ.trim())return;try{const r=await api(`/v3/lab/copilot/${selected.id}`,token,{method:"POST",body:JSON.stringify({question:copilotQ})}); setCopilotMsgs(m=>[...m,{q:copilotQ,a:r.answer}]); setCopilotQ("")}catch(e:any){setError(e.message)}}
 async function queryOmni(){if(!omniTarget.trim())return; setOmniBusy(true); try{ const r=await api(`/v3/omni/query`,token,{method:"POST",body:JSON.stringify({target:omniTarget.trim(), target_type:omniType})}); setOmniRes(r);}catch(e:any){setError(e.message)}finally{setOmniBusy(false)}}
 async function fetchOmniCatalog(){try{setOmniCat(await api(`/v3/omni/catalog`,token))}catch(e:any){setError(e.message)}}

 const filteredCases=cases.filter(c=>!q|| c.name.toLowerCase().includes(q.toLowerCase()) || c.id.toLowerCase().includes(q.toLowerCase()));
 const evidenceQ=(selected?.evidence||[]).filter(e=> !q || JSON.stringify(e).toLowerCase().includes(q.toLowerCase()));

 if(!user) return (
  <div className="min-h-screen bg-[#02070e] text-[#eaf2ff] flex items-center justify-center p-4 relative overflow-hidden">
    <div className="absolute inset-0 pointer-events-none" style={{background:"radial-gradient(800px 500px at 50% 0%, rgba(0,229,255,.12), transparent 60%), radial-gradient(600px 500px at 90% 90%, rgba(123,44,255,.10), transparent 60%)"}}/>
    <div className="absolute inset-0 opacity-[0.03]" style={{backgroundImage:"linear-gradient(rgba(0,229,255,.6) 1px, transparent 1px),linear-gradient(90deg,rgba(0,229,255,.6) 1px, transparent 1px)",backgroundSize:"56px 56px"}}/>
    <div className="relative w-full max-w-[980px] grid md:grid-cols-[1.05fr_.95fr] gap-6 items-stretch">
      <div className="hidden md:flex flex-col justify-between rounded-[22px] p-8 bg-gradient-to-b from-[#0c1a2e] to-[#08101e] border border-[#142a4a] overflow-hidden relative">
        <div className="absolute -right-10 -top-10 w-[320px] h-[320px] rounded-full blur-[50px] opacity-30" style={{background:"radial-gradient(circle, rgba(0,229,255,.35), transparent 60%)"}}/>
        <div>
          <div className="flex items-center gap-3"><div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00e5ff] to-[#7b2cff] grid place-items-center font-black text-[#02070e] shadow-[0_0_24px_rgba(0,229,255,.3)]">NX</div><div><div className="font-black tracking-widest text-sm">SAYAN<span className="text-[#00e5ff]">OX</span></div><div className="text-[10px] tracking-[2.6px] text-[#5b7590] font-mono">NEXUS OSINT • PRIVATE LTD.</div></div></div>
          <h1 className="mt-7 font-[800] tracking-[-0.03em] leading-[.95] text-[34px]">Investigate<br/><span className="bg-gradient-to-r from-[#00e5ff] via-white to-[#7b2cff] bg-clip-text text-transparent">with provenance.</span></h1>
          <p className="mt-3 text-[13px] leading-6 text-[#8ea6c0]">AI-native OSINT workspace — now with NEXUS LAB: holographic vault, neural mesh & shadow 360.</p>
          <div className="mt-5 grid gap-2 text-[12px] text-[#8ea6c0]">
            <div className="flex gap-2 items-center"><span className="w-6 h-6 rounded-full bg-[#00e5ff]/10 border border-[#00e5ff]/20 grid place-items-center text-[#00e5ff]">✓</span> Bounded collectors • SSRF-guarded</div>
            <div className="flex gap-2 items-center"><span className="w-6 h-6 rounded-full bg-[#7b2cff]/10 border border-[#7b2cff]/20 grid place-items-center text-[#b48cff]">⬢</span> NEXUS LAB — never-seen OSINT</div>
            <div className="flex gap-2 items-center"><span className="w-6 h-6 rounded-full bg-[#00ff9d]/10 border border-[#00ff9d]/20 grid place-items-center text-[#00ff9d]">⬣</span> Tamper-evident + Copilot</div>
          </div>
        </div>
        <div className="mt-8 p-3 rounded-xl bg-black/20 border border-white/5 font-mono text-[11px] leading-5 text-[#8ea6c0]">
          <div className="text-[#00e5ff]">sayanox@nexus:~$ <span className="text-[#eaf2ff]">lab --prism --verify</span></div>
          <div><span className="text-[#00ff9d]">[✓]</span> prism PRISM-A3F9 • ray 0.87 VERIFIED</div>
          <div><span className="text-[#00ff9d]">[✓]</span> neural mesh 6 inferred • thr 0.52</div>
          <div className="text-[#5b7590]"># lab ready — authorized OSINT only</div>
        </div>
      </div>
      <div className="rounded-[22px] p-6 md:p-7 bg-[#0c1a2e]/90 backdrop-blur border border-[#142a4a] shadow-[0_24px_80px_rgba(0,0,0,.5)]">
        <div className="md:hidden flex items-center gap-3 mb-5"><div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00e5ff] to-[#7b2cff] grid place-items-center font-black text-[#02070e]">NX</div><div><div className="font-black tracking-widest text-sm">NEXUS<span className="text-[#00e5ff]">OSINT</span></div><div className="text-[10px] tracking-[2px] text-[#5b7590] font-mono">LAB ENABLED</div></div></div>
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#00e5ff]/10 border border-[#00e5ff]/20 text-[11px] tracking-[1.6px] font-mono text-[#00e5ff]">● SECURE SESSION • AES-256 • LAB</div>
        <h2 className="mt-3 text-[22px] font-bold tracking-[-0.02em]">{login?"Welcome back":"Create your workspace"}</h2>
        <p className="text-[13px] text-[#8ea6c0] mt-1">{login?"Sign in to continue.":"Create account — LAB features are deterministic & auditable."} Password ≥10 chars.</p>
        <div className="mt-5 grid gap-3">
          <label className="grid gap-1.5"><span className="text-[11px] font-semibold tracking-widest text-[#5b7590]">USERNAME</span><input value={username} onChange={e=>setUsername(e.target.value)} placeholder="ada.lovelace" className="w-full px-4 py-3 rounded-xl bg-[#071325] border border-[#1a3560] text-[#eaf2ff] placeholder:text-[#5b7590] outline-none focus:border-[#00e5ff]/40 focus:shadow-[0_0_0_3px_rgba(0,229,255,.12)]" /></label>
          <label className="grid gap-1.5"><span className="text-[11px] font-semibold tracking-widest text-[#5b7590]">PASSWORD</span><input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="••••••••••" className="w-full px-4 py-3 rounded-xl bg-[#071325] border border-[#1a3560] text-[#eaf2ff] placeholder:text-[#5b7590] outline-none focus:border-[#00e5ff]/40 focus:shadow-[0_0_0_3px_rgba(0,229,255,.12)]" /></label>
          <button onClick={auth} disabled={busy || !username || password.length<10} className="mt-1 w-full py-3.5 rounded-xl bg-gradient-to-r from-[#00e5ff] to-[#7b2cff] text-[#02070e] font-extrabold tracking-wide shadow-[0_0_24px_rgba(0,229,255,.24)] disabled:opacity-50 disabled:cursor-not-allowed hover:translate-y-[-1px] transition">{busy?"Working…":login?"Sign in →":"Create account →"}</button>
          <button onClick={()=>setLogin(!login)} className="w-full py-2.5 rounded-xl bg-white/[0.03] border border-white/5 text-[#8ea6c0] text-sm hover:bg-white/[0.06] transition">{login?"Need an account? Register":"Already have an account? Sign in"}</button>
          {error&&<div className="p-3 rounded-xl bg-[#ff2e6b]/10 border border-[#ff2e6b]/20 text-[#ff9eb5] text-sm">{error}</div>}
          <div className="pt-2 flex items-center gap-2 text-[11px] text-[#5b7590] font-mono"><span className="w-2 h-2 rounded-full bg-[#00ff9d] shadow-[0_0_8px_#00ff9d] animate-pulse"/> LAB online • 5 primitives • deterministic</div>
        </div>
      </div>
    </div>
  </div>
 );

 return (
  <div className="min-h-screen bg-[#02070e] text-[#eaf2ff] selection:bg-[#00e5ff]/20">
    <style>{`@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500;600;700;800&display=swap');`}</style>
    <header className="sticky top-0 z-40 backdrop-blur-xl bg-[#02070e]/75 border-b border-[#142a4a]">
      <div className="max-w-[1420px] mx-auto px-3 md:px-4 h-[64px] flex items-center gap-3">
        <button onClick={()=>setSideOpen(v=>!v)} className="md:hidden w-9 h-9 grid place-items-center rounded-xl bg-[#0c1a2e] border border-[#142a4a]">☰</button>
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#00e5ff] to-[#7b2cff] grid place-items-center font-black text-[#02070e] shadow-[0_0_18px_rgba(0,229,255,.25)]">NX</div>
          <div className="hidden sm:block leading-none">
            <div className="font-black tracking-widest text-[13px]">NEXUS<span className="text-[#00e5ff]">OSINT</span></div>
            <div className="text-[10px] tracking-[2px] text-[#5b7590] font-mono">LAB • SPATIAL • 3D • EVIDENCE</div>
          </div>
          <span className="hidden lg:inline-flex ml-2 px-2.5 py-1 rounded-full bg-[#00ff9d]/10 border border-[#00ff9d]/20 text-[10px] tracking-widest font-mono text-[#00ff9d]">● LAB LIVE</span>
        </div>
        <div className="flex-1 max-w-[560px] hidden md:flex items-center gap-2 ml-2">
          <div className="flex-1 relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[#5b7590]">⌕</span>
            <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search cases, evidence, hashes…" className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-[#0a1830] border border-[#1a3560] text-sm placeholder:text-[#5b7590] outline-none focus:border-[#00e5ff]/30 focus:shadow-[0_0_0_3px_rgba(0,229,255,.10)]"/>
          </div>
          <div className="hidden xl:flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white/[0.03] border border-white/5 text-[11px] font-mono text-[#8ea6c0]"><span className="w-2 h-2 rounded-full bg-[#00e5ff] animate-pulse"/> {cases.length} cases • {selected?.evidence?.length||0} evidence</div>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <button onClick={()=>setCopilotOpen(v=>!v)} className="hidden md:inline-flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-gradient-to-r from-[#00e5ff]/15 to-[#7b2cff]/15 border border-[#00e5ff]/20 text-[#7beaff] text-sm font-bold hover:border-[#00e5ff]/30 transition">✦ Copilot</button>
          <button onClick={openSpatial} className="hidden md:inline-flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-[#0c1a2e] border border-[#1a3560] text-[#7beaff] text-sm font-bold hover:border-[#00e5ff]/30 transition">◎ Spatial</button>
          <button onClick={openSpatial} className="md:hidden px-3 py-2 rounded-xl bg-[#0c1a2e] border border-[#1a3560] text-[#7beaff]">◎</button>
          <div className="hidden sm:flex items-center gap-2 pl-2 pr-1 py-1 rounded-full bg-[#0c1a2e] border border-[#142a4a]">
            <span className="w-7 h-7 rounded-full bg-gradient-to-br from-[#00e5ff] to-[#7b2cff] grid place-items-center text-[11px] font-black text-[#02070e]">{user.username.slice(0,1).toUpperCase()}</span>
            <span className="text-sm text-[#8ea6c0] pr-1 hidden lg:inline">{user.username} <b className="text-[#eaf2ff]">· {user.role}</b></span>
            <button onClick={()=>{localStorage.removeItem("nexus_token");location.reload()}} className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs text-[#8ea6c0] hover:text-white transition">Sign out</button>
          </div>
        </div>
      </div>
    </header>

    <div className="max-w-[1420px] mx-auto px-3 md:px-4 py-4 grid grid-cols-1 md:grid-cols-[300px_1fr] gap-4">
      <aside className={`${sideOpen?"flex":"hidden"} md:flex flex-col gap-4 md:sticky md:top-[76px] h-fit`}>
        <div className="rounded-2xl bg-gradient-to-b from-[#0c1a2e] to-[#08111e] border border-[#142a4a] p-3 shadow-[0_12px_40px_rgba(0,0,0,.35)]">
          <button onClick={openSpatial} className="w-full py-3 rounded-xl bg-gradient-to-r from-[#00e5ff] to-[#7b2cff] text-[#02070e] font-extrabold shadow-[0_0_18px_rgba(0,229,255,.22)] hover:translate-y-[-1px] transition">◎ Open Spatial Intelligence</button>
          <button onClick={()=>setTab("lab")} className="mt-2 w-full py-3 rounded-xl bg-[#071325] border border-[#00e5ff]/30 text-[#7beaff] font-bold hover:bg-[#0a1830] transition flex items-center justify-center gap-2">⬣ NEXUS LAB <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-[#00e5ff] text-[#02070e] font-black">NEW</span></button>
          {user.role!=="viewer"&&<button onClick={createCase} className="mt-2 w-full py-3 rounded-xl bg-[#0a1830] border border-[#1a3560] text-[#eaf2ff] font-bold hover:border-[#00e5ff]/30 transition">＋ New Investigation</button>}
          <div className="mt-3 relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[#5b7590] text-sm">⌕</span>
            <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Filter cases…" className="w-full pl-8 pr-3 py-2.5 rounded-xl bg-[#071325] border border-[#1a3560] text-sm placeholder:text-[#5b7590] outline-none"/>
          </div>
          <div className="mt-3 grid gap-2 max-h-[42vh] overflow-auto pr-1">
            {filteredCases.map(c=>(
              <button key={c.id} onClick={()=>setSelected(c)} className={`text-left p-3 rounded-xl border transition ${selected?.id===c.id?"bg-[#0f2340] border-[#1a3560] shadow-[0_0_0_1px_rgba(0,229,255,.08)_inset]":"bg-[#071325]/60 border-transparent hover:bg-[#0a1830] hover:border-[#1a3560]"}`}>
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${c.workflow==="active"?"bg-[#00e5ff] shadow-[0_0_8px_#00e5ff]":c.workflow==="review"?"bg-[#ffd600]":c.workflow==="closed"?"bg-[#5b7590]":"bg-[#7b2cff]"}`}/>
                  <b className="text-[13px] leading-none truncate">{c.name}</b>
                  <span className={`ml-auto text-[10px] px-1.5 py-0.5 rounded-full border font-mono ${c.status==="closed"?"bg-white/5 border-white/10 text-[#8ea6c0]":"bg-[#00e5ff]/10 border-[#00e5ff]/20 text-[#7beaff]"}`}>{c.status}</span>
                </div>
                <div className="mt-1 flex items-center gap-2 text-[11px] text-[#8ea6c0] font-mono"><span>{c.workflow}</span><span>•</span><span>{c.targets?.length||0} targets</span><span>•</span><span className="truncate">{c.id.slice(0,8)}</span></div>
                {c.tags?.length? <div className="mt-2 flex flex-wrap gap-1">{c.tags.slice(0,3).map((t:string)=><span key={t} className="text-[10px] px-1.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-[#8ea6c0]">{t}</span>)}</div>:null}
              </button>
            ))}
            {!filteredCases.length&&<div className="p-6 text-center rounded-xl bg-[#071325] border border-dashed border-[#1a3560] text-sm text-[#5b7590]">No cases match.</div>}
          </div>
          <button onClick={()=>setCopilotOpen(true)} className="mt-3 w-full py-2.5 rounded-xl bg-gradient-to-r from-[#00e5ff]/10 to-[#7b2cff]/10 border border-[#00e5ff]/20 text-[#7beaff] font-bold text-sm">✦ Ask Copilot</button>
        </div>
        <div className="hidden md:block p-3 rounded-2xl bg-[#0c1a2e] border border-[#142a4a] text-[11px] leading-5 text-[#8ea6c0]">
          <b className="text-[#eaf2ff]">NEXUS LAB</b> — 5 primitives never seen in OSINT. All deterministic, bounded, and audit-friendly.
        </div>
      </aside>

      <section className="min-w-0">
        <div className="rounded-2xl bg-gradient-to-b from-[#0c1a2e] to-[#08101e] border border-[#142a4a] p-4 md:p-5 shadow-[0_12px_40px_rgba(0,0,0,.30)]">
          <div className="flex flex-col lg:flex-row gap-4 lg:items-end justify-between">
            <div className="min-w-0">
              <div className="inline-flex items-center gap-2 text-[11px] font-mono tracking-widest text-[#5b7590]"><span className={`w-2 h-2 rounded-full ${selected?"bg-[#00ff9d] shadow-[0_0_8px_#00ff9d]":"bg-[#5b7590]"}`}/> {selected? `${selected.workflow.toUpperCase()} • ${selected.status.toUpperCase()}`:"NO CASE SELECTED"}</div>
              <h1 className="mt-1 text-[22px] md:text-[26px] font-extrabold tracking-[-0.02em] leading-none truncate">{selected?.name||"Investigation Workspace"}</h1>
              <p className="mt-1 text-sm text-[#8ea6c0] truncate">{selected?.description||"Create or select a case to begin. LAB primitives amplify public-source signals."}</p>
              {selected&&<div className="mt-2 flex flex-wrap gap-1.5">{selected.tags?.map((t:string)=><span key={t} className="text-[11px] px-2 py-1 rounded-full bg-[#00e5ff]/10 border border-[#00e5ff]/15 text-[#7beaff] font-mono">{t}</span>)}{!selected.tags?.length&&<span className="text-[11px] text-[#5b7590]">No tags — add via Workflow tab.</span>}</div>}
            </div>
            <div className="w-full lg:w-[520px] shrink-0">
              <div className="flex items-center gap-2 p-1.5 rounded-2xl bg-[#071325] border border-[#1a3560] shadow-inner">
                <span className="hidden sm:inline-flex items-center gap-1.5 pl-2 pr-2.5 py-2 rounded-xl bg-white/5 border border-white/10 text-[11px] font-mono text-[#8ea6c0]"><span className="w-2 h-2 rounded-full bg-[#00e5ff] animate-pulse"/> {targetType.toUpperCase()}</span>
                <input value={target} onChange={e=>setTarget(e.target.value)} placeholder="domain / IP / URL / email — e.g. example.com" className="flex-1 min-w-0 bg-transparent px-2 py-2 outline-none text-sm placeholder:text-[#5b7590]"/>
                <button onClick={addTarget} disabled={user.role==="viewer" || !selected} className="px-4 py-2 rounded-xl bg-white text-[#08101e] font-bold text-sm hover:bg-[#eaf2ff] disabled:opacity-40 transition">Add</button>
                <button onClick={scan} disabled={busy||user.role==="viewer"||!selected} className="px-4 py-2 rounded-xl bg-gradient-to-r from-[#00e5ff] to-[#7b2cff] text-[#02070e] font-extrabold text-sm shadow-[0_0_18px_rgba(0,229,255,.22)] disabled:opacity-50 hover:translate-y-[-1px] transition">{busy?"Scanning…":"Scan"}</button>
              </div>
              <div className="mt-2 flex items-center gap-2 text-[11px] font-mono text-[#5b7590]"><span>ⓘ</span><span className="truncate">Scanning creates a bounded job with SSRF preflight. LAB amplifies with neural inference.</span></div>
            </div>
          </div>
          {selected&&<div className="mt-4 flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between p-3 rounded-xl bg-gradient-to-r from-[#00e5ff]/10 via-[#7b2cff]/10 to-transparent border border-[#00e5ff]/15">
            <div className="flex items-center gap-3"><span className="w-9 h-9 rounded-xl bg-[#00e5ff]/15 border border-[#00e5ff]/20 grid place-items-center text-[#00e5ff]">◎</span><div><div className="text-[13px] font-bold">Spatial Intelligence</div><div className="text-xs text-[#8ea6c0]">Live public signals + case evidence on the 3D globe</div></div></div>
            <button onClick={openSpatial} className="px-4 py-2.5 rounded-xl bg-white text-[#02070e] font-extrabold text-sm hover:bg-[#eaf2ff] transition">Open Globe →</button>
          </div>}
        </div>

        <div className="mt-4 flex gap-1.5 overflow-auto scrollbar-thin pb-1">
          {TABS.map(t=>(
            <button key={t.id} onClick={()=>loadTab(t.id)} className={`shrink-0 inline-flex items-center gap-2 px-3.5 py-2.5 rounded-xl border text-sm font-semibold transition relative ${tab===t.id?"bg-[#0f2340] border-[#1a3560] text-[#eaf2ff] shadow-[0_0_0_1px_rgba(0,229,255,.08)_inset]":"bg-[#0a1830]/60 border-transparent text-[#8ea6c0] hover:bg-[#0a1830] hover:text-[#eaf2ff]"}`}>
              <span className={`w-6 h-6 rounded-full grid place-items-center text-[11px] border ${tab===t.id?"bg-[#00e5ff]/15 border-[#00e5ff]/20 text-[#00e5ff]":"bg-white/5 border-white/10"}`}>{t.icon}</span> {t.label}
              {(t as any).badge && <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-[#00e5ff] text-[#02070e] font-black tracking-widest">{(t as any).badge}</span>}
              {t.id==="evidence"&&selected?.evidence?.length ?<span className="ml-1 text-[11px] px-1.5 py-0.5 rounded-full bg-white/10 border border-white/10 font-mono">{selected.evidence.length}</span>:null}
            </button>
          ))}
        </div>

        {error&&<div className="mt-3 p-3 rounded-xl bg-[#ff2e6b]/10 border border-[#ff2e6b]/20 text-[#ff9eb5] text-sm flex justify-between gap-3"><span>{error}</span><button onClick={()=>setError("")} className="px-2 py-1 rounded-lg bg-white/10 text-white text-xs">Dismiss</button></div>}

        <div className="mt-4 grid gap-4">
          {tab==="overview"&&(
            <>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                {[
                  {k:"Targets",v:selected?.targets?.length||0,sub:"Across this case",icon:"◎",grad:"from-[#00e5ff]/20 to-transparent"},
                  {k:"Evidence",v:selected?.evidence?.length||0,sub:"SHA-256 provenance",icon:"⬢",grad:"from-[#7b2cff]/20 to-transparent"},
                  {k:"Jobs",v:jobs.filter(j=>!selected||j.case_id===selected.id).length,sub:"Persistent + retry",icon:"⚡",grad:"from-[#00ff9d]/15 to-transparent"},
                  {k:"Confidence",v:`${score}`,sub:"Deterministic avg",icon:"◆",grad:"from-[#ffd600]/15 to-transparent"},
                ].map(c=>(
                  <div key={c.k} className={`rounded-2xl p-4 bg-gradient-to-b from-[#0c1a2e] to-[#08101e] border border-[#142a4a] relative overflow-hidden`}>
                    <div className={`absolute inset-0 bg-gradient-to-b ${c.grad} pointer-events-none`}/>
                    <div className="relative flex items-start justify-between gap-3">
                      <div><div className="text-[11px] tracking-widest font-mono text-[#5b7590]">{c.k.toUpperCase()}</div><div className="mt-1 text-[26px] font-black tracking-[-0.02em]">{c.v}{c.k==="Confidence"&&<span className="text-[14px] text-[#8ea6c0] font-bold">/100</span>}</div><div className="text-[11px] text-[#8ea6c0]">{c.sub}</div></div>
                      <span className="w-9 h-9 rounded-xl grid place-items-center bg-white/5 border border-white/10 text-[#7beaff]">{c.icon}</span>
                    </div>
                    <div className="relative mt-3 h-1 rounded-full bg-[#071325] overflow-hidden"><i className="block h-full bg-gradient-to-r from-[#00e5ff] to-[#7b2cff]" style={{width: c.k==="Confidence"? `${score}%` : `${Math.min(100, (Number(String(c.v).replace(/\D/g,""))||1)*18)}%`}}/></div>
                  </div>
                ))}
              </div>
              <div className="rounded-2xl bg-gradient-to-r from-[#00e5ff]/10 via-[#7b2cff]/10 to-transparent border border-[#00e5ff]/15 p-4 flex flex-col md:flex-row gap-4 items-center justify-between">
                <div><div className="text-[11px] tracking-widest font-mono text-[#00e5ff]">⬣ NEXUS LAB — NEVER-SEEN OSINT</div><div className="font-bold">5 primitives that turn public signals into superpowers.</div><div className="text-sm text-[#8ea6c0]">Holographic vault • Neural mesh • Shadow 360 • Prophet • Quantum search — all deterministic.</div></div>
                <button onClick={()=>loadTab("lab")} className="px-5 py-3 rounded-xl bg-gradient-to-r from-[#00e5ff] to-[#7b2cff] text-[#02070e] font-extrabold shadow-[0_0_18px_rgba(0,229,255,.2)]">Enter LAB →</button>
              </div>
              <div className="grid lg:grid-cols-[1.1fr_.9fr] gap-4">
                <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] p-4">
                  <div className="flex items-center justify-between gap-3"><h3 className="font-bold">Investigation controls</h3><span className="text-[11px] font-mono px-2 py-1 rounded-full bg-[#00e5ff]/10 border border-[#00e5ff]/20 text-[#7beaff]">AUTHORIZED ONLY</span></div>
                  <p className="mt-2 text-sm leading-6 text-[#8ea6c0]">Collect only public-source or explicitly authorized information. Every write is audit-logged and hashed.</p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    <button onClick={openSpatial} className="px-4 py-2.5 rounded-xl bg-white text-[#02070e] font-extrabold text-sm">◎ Open Spatial Globe</button>
                    <button onClick={()=>loadTab("lab")} className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-[#00e5ff]/15 to-[#7b2cff]/15 border border-[#00e5ff]/20 text-[#7beaff] font-bold text-sm">⬣ Open LAB</button>
                    <button onClick={closeCase} disabled={user.role==="viewer"||selected?.status==="closed"||!selected} className="px-4 py-2.5 rounded-xl bg-[#ff2e6b]/10 border border-[#ff2e6b]/20 text-[#ff9eb5] font-bold text-sm disabled:opacity-40">Close case</button>
                  </div>
                </div>
                <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] p-4">
                  <h3 className="font-bold">Recent evidence</h3>
                  <div className="mt-3 grid gap-2 max-h-[260px] overflow-auto pr-1">
                    {(selected?.evidence||[]).slice(0,5).map((e:any)=>(
                      <div key={e.id||e.provenance_hash} className="p-3 rounded-xl bg-[#071325] border border-[#1a3560] flex items-center gap-3">
                        <span className="w-8 h-8 rounded-full bg-[#00e5ff]/10 border border-[#00e5ff]/20 grid place-items-center text-[#00e5ff] text-xs">⬢</span>
                        <div className="min-w-0"><div className="text-sm font-semibold truncate">{e.source} <span className="text-[#5b7590]">·</span> {e.target}</div><div className="text-[11px] font-mono text-[#8ea6c0] truncate">{String(e.observed_at)} • {String(e.provenance_hash).slice(0,12)}…</div></div>
                        <span className="ml-auto text-[11px] px-2 py-1 rounded-full bg-white/5 border border-white/10 font-mono text-[#8ea6c0]">{Math.round(Number(e.confidence||0)*100)}%</span>
                      </div>
                    ))}
                    {!(selected?.evidence||[]).length&&<div className="p-8 text-center rounded-xl bg-[#071325] border border-dashed border-[#1a3560] text-sm text-[#5b7590]">No evidence yet — add a target and run a scan.</div>}
                  </div>
                </div>
              </div>
            </>
          )}

          {tab==="lab"&&(
            <div className="grid gap-4">
              {/* lab sub nav */}
              <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] p-3">
                <div className="flex flex-wrap gap-2">
                  {LABS.map(l=>(
                    <button key={l.id} onClick={()=>{setLabTab(l.id); if(l.id==="prism")fetchPrism(); if(l.id==="neural")fetchNeural(); if(l.id==="prophet")fetchProphet();}} className={`flex-1 min-w-[140px] p-3 rounded-xl border text-left transition ${labTab===l.id?"bg-[#0f2340] border-[#00e5ff]/30 shadow-[0_0_18px_rgba(0,229,255,.12)]":"bg-[#071325] border-[#1a3560] hover:border-[#1a3560]/80"}`}>
                      <div className="flex items-center gap-2"><span className={`w-7 h-7 rounded-full grid place-items-center text-xs border ${labTab===l.id?"bg-[#00e5ff]/15 border-[#00e5ff]/30 text-[#00e5ff]":"bg-white/5 border-white/10 text-[#8ea6c0]"}`}>{l.icon}</span><b className="text-sm">{l.label}</b>{labTab===l.id&&<span className="ml-auto w-2 h-2 rounded-full bg-[#00ff9d] shadow-[0_0_8px_#00ff9d] animate-pulse"/>}</div>
                      <div className="text-[11px] text-[#8ea6c0] mt-1">{l.desc}</div>
                    </button>
                  ))}
                </div>
                <div className="mt-3 flex flex-wrap gap-2 text-[11px] font-mono text-[#5b7590]"><span className="px-2 py-1 rounded-full bg-white/5 border border-white/10">deterministic</span><span className="px-2 py-1 rounded-full bg-white/5 border border-white/10">bounded</span><span className="px-2 py-1 rounded-full bg-white/5 border border-white/10">auditable</span><span className="ml-auto text-[#00e5ff]">vault hash {prism?.vault_hash || "—"}</span></div>
              </div>

              {labTab==="prism"&&(
                <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] p-4">
                  <div className="flex flex-wrap gap-3 items-center justify-between"><h3 className="font-bold">◆ Prism Vault — holographic evidence</h3><button onClick={fetchPrism} className="px-3 py-2 rounded-xl bg-[#0a1830] border border-[#1a3560] text-sm">Refresh</button></div>
                  <p className="text-sm text-[#8ea6c0]">Each evidence becomes a prism. Integrity ray = SHA256(provenance+confidence) • hue = source hash • chain_depth = snapshots. Drag to tilt.</p>
                  {!prism ? <div className="mt-4 p-10 text-center rounded-xl bg-[#071325] border border-dashed border-[#1a3560] text-[#8ea6c0]">Click Refresh to materialize prisms.</div> :
                  <div className="mt-4 grid md:grid-cols-2 xl:grid-cols-3 gap-3">
                    {prism.prisms.slice(0,9).map((p:any)=>(
                      <div key={p.id} onMouseMove={e=>{
                        const r=e.currentTarget.getBoundingClientRect(); const x=(e.clientX-r.left)/r.width-.5; const y=(e.clientY-r.top)/r.height-.5;
                        (e.currentTarget as HTMLElement).style.transform=`perspective(700px) rotateY(${x*10}deg) rotateX(${-y*10}deg) translateZ(0)`;
                      }} onMouseLeave={e=> (e.currentTarget as HTMLElement).style.transform=""}
                      className="group relative p-4 rounded-2xl bg-gradient-to-b from-[#0f2340] to-[#071325] border border-[#1a3560] overflow-hidden transition duration-300 hover:border-[#00e5ff]/30 hover:shadow-[0_12px_40px_rgba(0,0,0,.4)]">
                        <div className="absolute inset-0 opacity-20" style={{background:`conic-gradient(from 0deg at 50% 0%, hsl(${p.hue} 100% 60% / .18), transparent 60%)`}}/>
                        <div className="absolute top-0 left-0 right-0 h-[2px]" style={{background:`linear-gradient(90deg, hsl(${p.hue} 100% 60%), #7b2cff)`}}/>
                        <div className="relative flex items-center gap-2 text-[11px] font-mono tracking-widest text-[#5b7590]"><span className={`px-1.5 py-0.5 rounded-full border text-[10px] ${p.status==="VERIFIED"?"bg-[#00ff9d]/10 border-[#00ff9d]/20 text-[#7dffc0]":"bg-[#ffd600]/10 border-[#ffd600]/20 text-[#ffe27a]"}`}>{p.status}</span><span className="ml-auto">{p.depth_label} • {p.chain_depth}</span></div>
                        <div className="relative mt-2 font-mono text-[11px] text-[#7beaff]">{p.prism_id} • ray {p.integrity_ray}</div>
                        <div className="relative mt-1 font-bold text-sm truncate">{p.source} → {p.target}</div>
                        <div className="relative mt-1 font-mono text-[11px] text-[#8ea6c0] truncate">{String(p.provenance_hash).slice(0,24)}…</div>
                        <div className="relative mt-3 h-1.5 rounded-full bg-[#02070e] overflow-hidden border border-white/5"><i className="block h-full" style={{width:`${p.integrity_ray*100}%`, background:`linear-gradient(90deg, hsl(${p.hue} 100% 60%), #00e5ff)`}}/></div>
                        <div className="relative mt-3 flex gap-2"><button onClick={()=>navigator.clipboard.writeText(p.provenance_hash)} className="flex-1 py-1.5 rounded-full bg-white text-[#02070e] text-xs font-bold">Copy hash</button><span className="px-2 py-1 rounded-full bg-white/5 border border-white/10 font-mono text-[10px] text-[#8ea6c0]">{String(p.observed_at).slice(0,19)}</span></div>
                      </div>
                    ))}
                  </div>}
                  {prism && <div className="mt-3 text-[11px] font-mono text-[#5b7590] text-center">Vault hash {prism.vault_hash} • {prism.count} prisms • {String(prism.updated_at).slice(0,19)}</div>}
                </div>
              )}

              {labTab==="neural"&&(
                <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] p-4">
                  <div className="flex flex-wrap gap-3 items-center justify-between"><h3 className="font-bold">⟁ Neural Mesh — inferred correlations</h3><div className="flex items-center gap-2"><span className="text-xs font-mono text-[#8ea6c0]">thr {neuralThr.toFixed(2)}</span><input type="range" min={0.3} max={0.85} step={0.02} value={neuralThr} onChange={e=>setNeuralThr(parseFloat(e.target.value))} className="w-28"/><button onClick={fetchNeural} className="px-3 py-2 rounded-xl bg-gradient-to-r from-[#00e5ff] to-[#7b2cff] text-[#02070e] font-bold text-sm">Re-mesh</button></div></div>
                  <p className="text-sm text-[#8ea6c0]">Matrix = lexical + type + fingerprint mesh + deterministic jitter. Inferred edges are dashed — verify before action.</p>
                  {!neural ? <div className="mt-4 p-10 text-center rounded-xl bg-[#071325] border border-dashed border-[#1a3560] text-[#8ea6c0]">Click Re-mesh to build the mesh. Needs ≥2 entities.</div> :
                  <div className="mt-4 grid gap-4">
                    <div className="overflow-auto rounded-xl border border-[#1a3560] bg-[#071325]">
                      <table className="w-full text-[11px] font-mono">
                        <thead><tr><th className="p-2 text-left text-[#5b7590]"></th>{neural.labels.map((l:string,i:number)=><th key={i} className="p-2 text-left text-[#8ea6c0] truncate max-w-[120px]">{l}<br/><span className="text-[10px] text-[#5b7590]">{neural.types[i]}</span></th>)}</tr></thead>
                        <tbody>{neural.matrix.map((row:number[],i:number)=>(
                          <tr key={i}><td className="p-2 text-[#7beaff] truncate max-w-[100px]">{neural.labels[i]}</td>{row.map((v:number,j:number)=>{
                            const intensity=Math.round(v*255); const bg=`rgba(${Math.round(0+intensity*0.0)}, ${Math.round(229*v)}, ${Math.round(255*v)}, ${0.08+v*0.22})`;
                            return <td key={j} className="p-1"><div className="px-2 py-1 rounded-lg text-center border" style={{background:bg, borderColor:`rgba(0,229,255,${0.08+v*0.18})`, color: v>0.72?"#eaf2ff": v>0.55?"#cfe0f2":"#8ea6c0"}}>{v.toFixed(2)}</div></td>
                          })}</tr>
                        ))}</tbody>
                      </table>
                    </div>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="p-3 rounded-xl bg-[#071325] border border-[#1a3560]"><b className="text-sm">Inferred (dashed) — {neural.inferred.length}</b><div className="mt-2 grid gap-2 max-h-[260px] overflow-auto pr-1">{neural.inferred.map((e:any,i:number)=>(
                        <div key={i} className="p-2 rounded-xl bg-[#0c1a2e] border border-[#1a3560]/80 flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[#ffd600] shadow-[0_0_8px_#ffd600]"/> <span className="font-mono text-xs truncate">{e.source_label} → {e.target_label}</span><span className="ml-auto text-[11px] px-1.5 py-0.5 rounded-full bg-[#ffd600]/10 border border-[#ffd600]/20 font-mono">{e.neural_score}</span></div>
                      ))}{!neural.inferred.length&&<div className="text-xs text-[#5b7590]">No inferred above threshold — lower thr or add more diverse entities.</div>}</div></div>
                      <div className="p-3 rounded-xl bg-[#071325] border border-[#1a3560]"><b className="text-sm">Observed (solid) — {neural.observed.length}</b><div className="mt-2 grid gap-2 max-h-[260px] overflow-auto pr-1">{neural.observed.map((e:any,i:number)=>(
                        <div key={i} className="p-2 rounded-xl bg-[#0c1a2e] border border-[#1a3560] flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[#00e5ff]"/> <span className="font-mono text-xs truncate">{e.source} → {e.target} <span className="text-[#5b7590]">({e.relation||"LINK"})</span></span><span className="ml-auto text-[11px] px-1.5 py-0.5 rounded-full bg-[#00e5ff]/10 border border-[#00e5ff]/20 font-mono">{e.confidence??"—"}</span></div>
                      ))}{!neural.observed.length&&<div className="text-xs text-[#5b7590]">No observed relationships yet.</div>}</div></div>
                    </div>
                    <div className="text-[11px] font-mono text-[#5b7590]">mesh hash {neural.mesh_hash} • top pairs: {neural.top_pairs.map((p:any)=>`${p.a}↔${p.b} (${p.score})`).join(" • ").slice(0,120)}</div>
                  </div>}
                </div>
              )}

              {labTab==="shadow"&&(
                <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] p-4">
                  <div className="flex flex-wrap gap-3 items-center justify-between"><h3 className="font-bold">⬢ Shadow 360 — 6-axis entity profile</h3>
                    <div className="flex gap-2">
                      <select value={shadowId} onChange={e=>setShadowId(e.target.value)} className="px-3 py-2 rounded-xl bg-[#071325] border border-[#1a3560] text-sm min-w-[220px]">
                        <option value="">Select entity…</option>
                        {entities.map((e:any)=><option key={e.id} value={e.id}>{e.entity_type}: {String(e.canonical).slice(0,32)}</option>)}
                      </select>
                      <button onClick={fetchShadow} disabled={!shadowId} className="px-3 py-2 rounded-xl bg-gradient-to-r from-[#00e5ff] to-[#7b2cff] text-[#02070e] font-bold text-sm disabled:opacity-40">Profile</button>
                    </div>
                  </div>
                  <p className="text-sm text-[#8ea6c0]">Axes: infra / identity / temporal / geo / hygiene / exposure. Risk = exposure·0.28 + (1-hygiene)·0.22 + … Variance flags weak provenance.</p>
                  {!shadow ? <div className="mt-4 p-10 text-center rounded-xl bg-[#071325] border border-dashed border-[#1a3560] text-[#8ea6c0]">Pick an entity and hit Profile. Or run Scan to create entities.</div> :
                  <div className="mt-4 grid lg:grid-cols-[360px_1fr] gap-4 items-start">
                    <div className="p-3 rounded-xl bg-[#071325] border border-[#1a3560] grid place-items-center">
                      <Radar axes={shadow.axes}/>
                      <div className="mt-3 text-center"><div className={`inline-flex px-3 py-1 rounded-full border font-mono text-xs font-bold ${shadow.risk_label==="CRITICAL"?"bg-[#ff2e6b]/10 border-[#ff2e6b]/30 text-[#ff9eb5]":shadow.risk_label==="ELEVATED"?"bg-[#ffd600]/10 border-[#ffd600]/30 text-[#ffe27a]":"bg-[#00ff9d]/10 border-[#00ff9d]/20 text-[#7dffc0]"}`}>RISK {shadow.risk_label} • {shadow.risk}</div><div className="text-[11px] font-mono text-[#5b7590] mt-1">shadow {shadow.shadow_hash} • variance {shadow.variance} • {shadow.entity.canonical}</div></div>
                    </div>
                    <div className="grid gap-3">
                      <div className="grid grid-cols-2 gap-2">{Object.entries(shadow.axes).map(([k,v]:any)=>(
                        <div key={k} className="p-3 rounded-xl bg-[#071325] border border-[#1a3560]"><div className="text-[11px] tracking-widest font-mono text-[#5b7590]">{k.toUpperCase()}</div><div className="text-[18px] font-black">{v}</div><div className="mt-1 h-1 rounded-full bg-[#02070e] overflow-hidden"><i className="block h-full bg-gradient-to-r from-[#00e5ff] to-[#7b2cff]" style={{width:`${v*100}%`}}/></div></div>
                      ))}</div>
                      <div className="p-3 rounded-xl bg-[#071325] border border-[#1a3560]"><b className="text-sm">Contradictions — {shadow.contradictions.length||"none"}</b>{shadow.contradictions.length?<div className="mt-2 grid gap-2">{shadow.contradictions.map((c:any,i:number)=><div key={i} className={`p-2 rounded-xl border text-sm ${c.level==="high"?"bg-[#ff2e6b]/10 border-[#ff2e6b]/20 text-[#ff9eb5]":c.level==="medium"?"bg-[#ffd600]/10 border-[#ffd600]/20 text-[#ffe27a]":"bg-white/5 border-white/10 text-[#cfe0f2]"}`}>{c.msg}</div>)}</div>:<div className="text-xs text-[#5b7590] mt-1">No contradictions — provenance looks consistent.</div>}</div>
                      <div className="p-3 rounded-xl bg-[#071325] border border-[#1a3560]"><b className="text-sm">Peers — {shadow.peers.length}</b><div className="mt-2 flex flex-wrap gap-1.5">{shadow.peers.map((p:any)=><span key={p.id} className="px-2 py-1 rounded-full bg-[#0c1a2e] border border-[#1a3560] font-mono text-xs">{p.type}: {String(p.canonical).slice(0,18)} <span className="text-[#5b7590]">· {p.relation}</span></span>)}{!shadow.peers.length&&<span className="text-xs text-[#5b7590]">No peers.</span>}</div></div>
                      <div className="p-3 rounded-xl bg-[#071325] border border-[#1a3560]"><b className="text-sm">Fragments — evidence that shaped this shadow</b><div className="mt-2 grid gap-2">{shadow.fragments.map((f:any,i:number)=><div key={i} className="p-2 rounded-xl bg-[#0c1a2e] border border-[#1a3560] font-mono text-xs flex gap-2"><span className="text-[#7beaff]">{f.source}</span><span className="text-[#5b7590]">→</span><span className="truncate">{f.target}</span><span className="ml-auto text-[#8ea6c0]">{f.confidence}</span></div>)}</div></div>
                    </div>
                  </div>}
                </div>
              )}

              {labTab==="prophet"&&(
                <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] p-4">
                  <div className="flex flex-wrap gap-3 items-center justify-between"><h3 className="font-bold">◈ Prophet — causality + forecast</h3><button onClick={fetchProphet} className="px-3 py-2 rounded-xl bg-[#0a1830] border border-[#1a3560] text-sm">Forecast</button></div>
                  <p className="text-sm text-[#8ea6c0]">Causal edges = temporal order + lexical overlap (bounded). Forecast = cadence + rotation heuristic — predictive, not authoritative.</p>
                  {!prophet ? <div className="mt-4 p-10 text-center rounded-xl bg-[#071325] border border-dashed border-[#1a3560] text-[#8ea6c0]">Click Forecast — needs ≥2 dated evidence.</div> :
                  <div className="mt-4 grid gap-4">
                    <div className="grid md:grid-cols-3 gap-3">{prophet.forecasts.map((f:any)=>(
                      <div key={f.h} className="p-4 rounded-2xl bg-gradient-to-b from-[#0f2340] to-[#071325] border border-[#1a3560] relative overflow-hidden">
                        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-[#00e5ff] to-[#7b2cff]"/>
                        <div className="text-[11px] tracking-widest font-mono text-[#00e5ff]">H+{f.h} • {f.window} • {f.confidence}</div>
                        <div className="mt-1 font-bold">{f.predicted_target}</div>
                        <div className="text-xs px-2 py-1 rounded-full bg-[#ffd600]/10 border border-[#ffd600]/20 inline-flex mt-1 font-mono text-[#ffe27a]">{f.action}</div>
                        <div className="text-xs text-[#8ea6c0] mt-2 leading-5">{f.rationale}</div>
                      </div>
                    ))}</div>
                    <div className="p-3 rounded-xl bg-[#071325] border border-[#1a3560]"><b className="text-sm">Causal edges — {prophet.causal_edges.length}</b><div className="mt-2 grid gap-2 max-h-[260px] overflow-auto pr-1">{prophet.causal_edges.map((c:any,i:number)=>(
                      <div key={i} className="p-2 rounded-xl bg-[#0c1a2e] border border-[#1a3560] flex items-center gap-2 font-mono text-xs"><span className="text-[#7beaff]">{c.from_target}</span><span>→</span><span className="text-[#cfe0f2]">{c.to_target}</span><span className="ml-auto text-[#8ea6c0]">{c.hours}h</span><span className="px-1.5 py-0.5 rounded-full bg-white/5 border border-white/10">{c.causal_score}</span></div>
                    ))}{!prophet.causal_edges.length&&<div className="text-xs text-[#5b7590]">Not enough temporal/lexical overlap to infer causality.</div>}</div></div>
                    <div className="text-[11px] font-mono text-[#5b7590]">prophet {prophet.prophet_hash} • {prophet.evidence_count} evidence • horizon {prophet.horizon}</div>
                  </div>}
                </div>
              )}

              {labTab==="quantum"&&(
                <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] p-4">
                  <div className="flex items-center gap-2"><h3 className="font-bold">⌖ Quantum — natural language → graph</h3><span className="text-[10px] px-2 py-1 rounded-full bg-[#00e5ff]/10 border border-[#00e5ff]/20 font-mono text-[#7beaff]">DETERMINISTIC</span></div>
                  <p className="text-sm text-[#8ea6c0]">Intent detection + token overlap ranking. No external LLM — fully offline, auditable.</p>
                  <div className="mt-3 flex gap-2 p-1.5 rounded-2xl bg-[#071325] border border-[#1a3560]"><input value={quantumQ} onChange={e=>setQuantumQ(e.target.value)} placeholder="e.g. who owns example.com and what else is linked via shared cert?" className="flex-1 bg-transparent px-3 py-2 outline-none text-sm placeholder:text-[#5b7590]"/><button onClick={fetchQuantum} className="px-4 py-2 rounded-xl bg-gradient-to-r from-[#00e5ff] to-[#7b2cff] text-[#02070e] font-bold text-sm">Search</button></div>
                  {!quantum ? <div className="mt-4 p-10 text-center rounded-xl bg-[#071325] border border-dashed border-[#1a3560] text-[#8ea6c0]">Type a question and hit Search. Try presets below.</div> :
                  <div className="mt-4 grid gap-3">
                    <div className="p-3 rounded-xl bg-[#071325] border border-[#1a3560]"><div className="text-[11px] tracking-widest font-mono text-[#00e5ff]">INTENT: {quantum.intent.toUpperCase()} • TOKENS: {quantum.tokens.join(", ")||"—"}</div><div className="mt-2 text-sm leading-6">{quantum.answer}</div><div className="text-[11px] font-mono text-[#5b7590] mt-1">hash {quantum.quantum_hash}</div></div>
                    <div className="grid md:grid-cols-2 gap-3">
                      <div className="p-3 rounded-xl bg-[#071325] border border-[#1a3560]"><b className="text-sm">Entities — {quantum.entities.length}</b><div className="mt-2 grid gap-1.5 max-h-[220px] overflow-auto pr-1">{quantum.entities.map((e:any)=><div key={e.id} className="p-2 rounded-xl bg-[#0c1a2e] border border-[#1a3560] font-mono text-xs flex justify-between"><span>{e.type}: {String(e.canonical).slice(0,22)}</span><span className="text-[#7beaff]">{e.score}</span></div>)}{!quantum.entities.length&&<div className="text-xs text-[#5b7590]">No entity hits.</div>}</div></div>
                      <div className="p-3 rounded-xl bg-[#071325] border border-[#1a3560]"><b className="text-sm">Evidence — {quantum.evidence.length}</b><div className="mt-2 grid gap-1.5 max-h-[220px] overflow-auto pr-1">{quantum.evidence.map((e:any)=><div key={e.id} className="p-2 rounded-xl bg-[#0c1a2e] border border-[#1a3560] font-mono text-xs"><span className="text-[#7beaff]">{e.source}</span> → {e.target} <span className="text-[#5b7590]">×{e.score}</span></div>)}{!quantum.evidence.length&&<div className="text-xs text-[#5b7590]">No evidence hits.</div>}</div></div>
                    </div>
                  </div>}
                  <div className="mt-3 flex flex-wrap gap-1.5">{["who owns this domain?","show all linked infrastructure","timeline of this target","what is the risk exposure?"].map(s=>(
                    <button key={s} onClick={()=>setQuantumQ(s)} className="px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-xs text-[#8ea6c0] hover:text-white">“{s}”</button>
                  ))}</div>
                </div>
              )}
            </div>
          )}

          {tab==="omni"&&(
            <div className="grid gap-4">
              <div className="rounded-2xl bg-gradient-to-r from-[#00e5ff]/10 via-[#7b2cff]/10 to-transparent border border-[#00e5ff]/15 p-4 flex flex-col md:flex-row gap-4 items-center justify-between">
                <div><div className="text-[11px] tracking-widest font-mono text-[#00e5ff]">⬔ OMNI — ALL PUBLIC SOURCES • {omniCat?.count||45}+ ADAPTERS</div><div className="font-bold text-[18px] tracking-[-0.02em]">One query, every public source</div><div className="text-sm text-[#8ea6c0]">Infrastructure • Web • Threat • Blockchain • Social • Geo • Environment • Knowledge — bounded, rate-limited, audited.</div></div>
                <div className="flex gap-2"><button onClick={fetchOmniCatalog} className="px-4 py-2.5 rounded-xl bg-[#0a1830] border border-[#1a3560] text-sm font-bold">Refresh catalog</button><button onClick={()=>{setOmniTarget(target||"8.8.8.8"); setOmniType(targetType)}} className="px-4 py-2.5 rounded-xl bg-white text-[#02070e] font-bold text-sm">Use top bar target →</button></div>
              </div>

              <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] p-4">
                <div className="flex flex-wrap gap-2 p-1.5 rounded-2xl bg-[#071325] border border-[#1a3560] items-center">
                  <select value={omniType} onChange={e=>setOmniType(e.target.value)} className="px-3 py-2 rounded-xl bg-[#0a1830] border border-[#1a3560] text-sm font-mono text-[#7beaff] outline-none">
                    <option value="domain">domain</option><option value="ip">ip</option><option value="url">url</option><option value="email">email</option><option value="wallet">wallet</option><option value="hash">hash</option><option value="term">term</option>
                  </select>
                  <input value={omniTarget} onChange={e=>setOmniTarget(e.target.value)} placeholder="target — e.g. 8.8.8.8 / example.com / bc1q..." className="flex-1 min-w-[180px] bg-transparent px-3 py-2 outline-none text-sm placeholder:text-[#5b7590]"/>
                  <button onClick={queryOmni} disabled={omniBusy||!omniTarget.trim()} className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#00e5ff] to-[#7b2cff] text-[#02070e] font-extrabold text-sm disabled:opacity-50 shadow-[0_0_18px_rgba(0,229,255,.22)]">{omniBusy?"Querying…":"⚡ Omni Query"}</button>
                </div>
                <div className="mt-2 flex flex-wrap gap-1.5 text-[11px] font-mono text-[#5b7590]">
                  <span>Presets:</span>
                  {["8.8.8.8","google.com","https://example.com","satoshi@nakamoto.com","1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"].map(s=>(
                    <button key={s} onClick={()=>{setOmniTarget(s); setOmniType(s.includes("@")?"email": s.startsWith("http")?"url": s.includes(".") && !s.includes("/")?"domain": s.startsWith("1")||s.startsWith("bc1")?"wallet":"term");}} className="px-2 py-1 rounded-full bg-white/5 border border-white/10 hover:text-[#eaf2ff]">{s}</button>
                  ))}
                </div>
              </div>

              {omniRes && (
                <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] p-4">
                  <div className="flex flex-wrap gap-2 items-center justify-between"><h3 className="font-bold">⚡ Omni Result — {omniRes.target} <span className="text-xs font-mono px-2 py-1 rounded-full bg-[#00ff9d]/10 border border-[#00ff9d]/20 text-[#7dffc0]">{omniRes.target_type}</span></h3><span className="text-xs font-mono text-[#5b7590]">{omniRes.sources_ok}/{omniRes.sources_queried} ok • {omniRes.elapsed_s}s • hash {omniRes.omni_hash}</span></div>
                  <div className="mt-4 grid gap-3">
                    {Object.entries(omniRes.results as any).map(([k,v]:any)=>{
                      const hasData = v && (Array.isArray(v) ? v.length>0 : (typeof v==="object" && Object.keys(v).length>0 && !v.error && v.status!=="not_configured"));
                      const isEmptyArray = Array.isArray(v) && v.length===0;
                      const isNotConfigured = v?.status==="not_configured";
                      return (
                        <details key={k} open={hasData && !isEmptyArray} className="group rounded-xl bg-[#071325] border border-[#1a3560] overflow-hidden">
                          <summary className="p-3 flex items-center gap-3 cursor-pointer list-none">
                            <span className={`w-2 h-2 rounded-full ${hasData?"bg-[#00ff9d] shadow-[0_0_8px_#00ff9d]": isNotConfigured?"bg-[#ffd600]":"bg-[#5b7590]"}`}/>
                            <b className="font-mono text-sm">{k}</b>
                            <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-[#8ea6c0]">{Array.isArray(v)? `${v.length} items` : v?.status || (v&&Object.keys(v).length? "object" : "empty")}</span>
                            <span className="ml-auto text-xs text-[#5b7590] group-open:rotate-180 transition">▼</span>
                          </summary>
                          <div className="px-3 pb-3">
                            {isNotConfigured ? <div className="text-xs text-[#ffe27a] bg-[#ffd600]/10 border border-[#ffd600]/20 p-2 rounded-lg">Optional key not configured — set {omniCat?.sources?.find((s:any)=>s.id===k.replace("_","-"))?.env || "env"} to unlock.</div>
                            : Array.isArray(v) ? (
                              <div className="grid gap-1.5 max-h-[260px] overflow-auto pr-1">
                                {v.slice(0,20).map((x:any,i:number)=>(
                                  <div key={i} className="p-2 rounded-lg bg-[#0c1a2e] border border-[#1a3560]/60 font-mono text-xs text-[#cfe0f2] overflow-auto"><pre className="whitespace-pre-wrap break-all text-[11px] leading-5">{JSON.stringify(x,null,2).slice(0,800)}</pre></div>
                                ))}
                                {v.length===0&&<div className="text-xs text-[#5b7590]">No results (bounded, public).</div>}
                              </div>
                            ) : (
                              <pre className="p-2 rounded-lg bg-[#0c1a2e] border border-[#1a3560] text-[11px] font-mono text-[#cfe0f2] overflow-auto max-h-[260px] whitespace-pre-wrap break-all">{JSON.stringify(v,null,2).slice(0,4000)}</pre>
                            )}
                          </div>
                        </details>
                      )
                    })}
                  </div>
                </div>
              )}

              <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] p-4">
                <div className="flex flex-wrap gap-2 items-center justify-between"><h3 className="font-bold">📚 Source Catalog — {omniCat?.count||"—"} adapters</h3>
                  <div className="flex gap-1.5 overflow-auto">
                    {["all","infrastructure","web","threat","blockchain","social","environment","geo","knowledge"].map(f=>(
                      <button key={f} onClick={()=>setOmniFilter(f)} className={`px-2.5 py-1 rounded-full border text-xs font-mono capitalize ${omniFilter===f?"bg-[#00e5ff]/15 border-[#00e5ff]/30 text-[#7beaff]":"bg-white/5 border-white/10 text-[#8ea6c0]"}`}>{f}</button>
                    ))}
                  </div>
                </div>
                {!omniCat ? <div className="mt-4 p-10 text-center rounded-xl bg-[#071325] border border-dashed border-[#1a3560] text-[#8ea6c0]">Click Refresh catalog to load all 45+ public sources.</div> :
                <div className="mt-4 grid md:grid-cols-2 xl:grid-cols-3 gap-2.5 max-h-[520px] overflow-auto pr-1">
                  {omniCat.sources.filter((s:any)=> omniFilter==="all" || s.family===omniFilter || s.id.includes(omniFilter)).map((s:any)=>(
                    <div key={s.id} className={`p-3 rounded-xl border flex gap-3 ${s.configured?"bg-[#071325] border-[#1a3560]":"bg-[#071325]/60 border-dashed border-[#1a3560]/60"}`}>
                      <span className={`w-8 h-8 rounded-lg grid place-items-center text-xs border shrink-0 ${s.configured?"bg-[#00ff9d]/10 border-[#00ff9d]/20 text-[#7dffc0]":"bg-[#ffd600]/10 border-[#ffd600]/20 text-[#ffe27a]"}`}>{s.configured?"✓":"○"}</span>
                      <div className="min-w-0"><div className="font-bold text-sm leading-none truncate">{s.name}</div><div className="text-[11px] font-mono text-[#8ea6c0]">{s.family} • {s.id} • {s.key_required?"optional key":"free"}</div><div className="text-[11px] text-[#5b7590] truncate">{s.docs}</div>{s.env&&<div className="text-[10px] font-mono text-[#5b7590]">env: {s.env} {s.configured?"●":"○"}</div>}</div>
                      <span className={`ml-auto text-[10px] px-1.5 py-0.5 rounded-full border font-mono h-fit ${s.configured?"bg-[#00ff9d]/10 border-[#00ff9d]/20 text-[#7dffc0]":"bg-white/5 border-white/10 text-[#8ea6c0]"}`}>{s.configured?"ready":"optional"}</span>
                    </div>
                  ))}
                </div>}
                <div className="mt-3 text-[11px] font-mono text-[#5b7590]">All adapters are public/free-tier, bounded (≤200), 6-8s timeout, User-Agent: NEXUS-OSINT/4. Optional keys unlock full data without changing public boundary.</div>
              </div>
            </div>
          )}

          {tab==="evidence"&&(
            <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] overflow-hidden">
              <div className="p-4 flex flex-col sm:flex-row gap-3 sm:items-center justify-between border-b border-[#142a4a]">
                <h3 className="font-bold">Immutable evidence records <span className="ml-2 text-xs font-mono px-2 py-1 rounded-full bg-[#00e5ff]/10 border border-[#00e5ff]/20 text-[#7beaff]">{evidenceQ.length}</span></h3>
                <div className="flex items-center gap-2">
                  <span className="hidden sm:inline text-xs text-[#5b7590] font-mono">Search evidence</span>
                  <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Filter by source / target / hash…" className="px-3 py-2 rounded-xl bg-[#071325] border border-[#1a3560] text-sm w-[260px] max-w-[60vw] outline-none"/>
                </div>
              </div>
              <div className="overflow-auto">
                <table className="w-full text-sm">
                  <thead className="text-[11px] tracking-widest font-mono text-[#5b7590]"><tr className="border-b border-[#142a4a] bg-[#071325]/60"><th className="text-left p-3">SOURCE</th><th className="text-left p-3">TARGET</th><th className="text-left p-3">OBSERVED</th><th className="text-left p-3">CONF</th><th className="text-left p-3">PROVENANCE</th></tr></thead>
                  <tbody>{evidenceQ.map((r:any)=>(
                    <tr key={r.id||r.provenance_hash} className="border-b border-[#142a4a]/60 hover:bg-[#071325]/40">
                      <td className="p-3"><span className="px-2 py-1 rounded-full bg-[#00e5ff]/10 border border-[#00e5ff]/15 text-[#7beaff] font-mono text-xs">{r.source}</span></td>
                      <td className="p-3 font-mono text-xs text-[#cfe0f2]">{r.target}</td>
                      <td className="p-3 font-mono text-xs text-[#8ea6c0]">{String(r.observed_at)}</td>
                      <td className="p-3"><span className="px-2 py-1 rounded-full bg-white/5 border border-white/10 font-mono text-xs">{Math.round(Number(r.confidence||0)*100)}%</span></td>
                      <td className="p-3 font-mono text-[11px] text-[#8ea6c0]"><span className="inline-flex items-center gap-2"><span className="truncate max-w-[160px]">{r.provenance_hash}</span><button onClick={()=>navigator.clipboard.writeText(r.provenance_hash)} className="px-1.5 py-0.5 rounded bg-white/5 border border-white/10 hover:bg-white/10">copy</button></span></td>
                    </tr>
                  ))}</tbody>
                </table>
                {!evidenceQ.length&&<div className="p-10 text-center text-sm text-[#5b7590]">No records match your filter.</div>}
              </div>
            </div>
          )}

          {tab==="entities"&&(
            <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] overflow-hidden">
              <div className="p-4 border-b border-[#142a4a] flex items-center justify-between"><h3 className="font-bold">Entity index</h3><button onClick={()=>{if(selected) {setShadowId(entities[0]?.id||""); setTab("lab"); setLabTab("shadow");}}} className="text-xs px-2 py-1 rounded-full bg-[#7b2cff]/10 border border-[#7b2cff]/20 text-[#c9b6ff]">Open Shadow 360 →</button></div>
              <div className="overflow-auto">
                <table className="w-full text-sm">
                  <thead className="text-[11px] tracking-widest font-mono text-[#5b7590]"><tr className="border-b border-[#142a4a] bg-[#071325]/60"><th className="text-left p-3">TYPE</th><th className="text-left p-3">CANONICAL</th><th className="text-left p-3">FINGERPRINT</th><th className="text-left p-3">SHADOW</th></tr></thead>
                  <tbody>{entities.map((r:any)=>(
                    <tr key={r.id} className="border-b border-[#142a4a]/60 hover:bg-[#071325]/40">
                      <td className="p-3"><span className="px-2 py-1 rounded-full bg-[#7b2cff]/10 border border-[#7b2cff]/20 text-[#c9b6ff] font-mono text-xs">{r.entity_type}</span></td>
                      <td className="p-3 font-mono text-xs text-[#eaf2ff]">{r.canonical}</td>
                      <td className="p-3 font-mono text-[11px] text-[#8ea6c0]">{r.fingerprint?.slice(0,16)}…</td>
                      <td className="p-3"><button onClick={()=>{setShadowId(r.id); setTab("lab"); setLabTab("shadow"); setTimeout(fetchShadow,120)}} className="px-2 py-1 rounded-full bg-[#00e5ff]/10 border border-[#00e5ff]/20 text-[#7beaff] text-xs">360°</button></td>
                    </tr>
                  ))}</tbody>
                </table>
                {!entities.length&&<div className="p-10 text-center text-sm text-[#5b7590]">No entities yet — run Scan.</div>}
              </div>
            </div>
          )}

          {tab==="jobs"&&(
            <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] overflow-hidden">
              <div className="p-4 border-b border-[#142a4a] flex items-center justify-between gap-3"><h3 className="font-bold">Background jobs</h3><button onClick={pollJobs} className="px-3 py-2 rounded-xl bg-[#0a1830] border border-[#1a3560] text-sm">Refresh</button></div>
              <div className="overflow-auto">
                <table className="w-full text-sm">
                  <thead className="text-[11px] tracking-widest font-mono text-[#5b7590]"><tr className="border-b border-[#142a4a] bg-[#071325]/60"><th className="text-left p-3">TARGET</th><th className="text-left p-3">TYPE</th><th className="text-left p-3">STATUS</th><th className="text-left p-3">ATTEMPTS</th><th className="text-left p-3">CREATED</th></tr></thead>
                  <tbody>{jobs.filter(j=>!selected||j.case_id===selected.id).map((r:any)=>(
                    <tr key={r.id} className="border-b border-[#142a4a]/60 hover:bg-[#071325]/40">
                      <td className="p-3 font-mono text-xs">{r.target}</td>
                      <td className="p-3"><span className="px-2 py-1 rounded-full bg-white/5 border border-white/10 font-mono text-xs">{r.target_type}</span></td>
                      <td className="p-3"><span className={`px-2.5 py-1 rounded-full border font-mono text-xs ${r.status==="completed"?"bg-[#00ff9d]/10 border-[#00ff9d]/20 text-[#7dffc0]":r.status==="failed"?"bg-[#ff2e6b]/10 border-[#ff2e6b]/20 text-[#ff9eb5]":r.status==="running"?"bg-[#00e5ff]/10 border-[#00e5ff]/20 text-[#7beaff]":"bg-white/5 border-white/10 text-[#8ea6c0]"}`}>{r.status}</span></td>
                      <td className="p-3 font-mono text-xs">{r.attempts}</td>
                      <td className="p-3 font-mono text-xs text-[#8ea6c0]">{String(r.created_at).slice(0,19)}</td>
                    </tr>
                  ))}</tbody>
                </table>
                {!jobs.filter(j=>!selected||j.case_id===selected.id).length&&<div className="p-10 text-center text-sm text-[#5b7590]">No jobs — use Scan.</div>}
              </div>
            </div>
          )}

          {tab==="graph"&&(
            <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] p-4">
              <div className="flex items-center justify-between"><h3 className="font-bold">Relationship graph</h3><button onClick={()=>setTab("lab")} className="text-xs px-2 py-1 rounded-full bg-[#00e5ff]/10 border border-[#00e5ff]/20 text-[#7beaff]">Try Neural Mesh →</button></div>
              <div className="mt-4 relative h-[420px] rounded-2xl overflow-hidden bg-[radial-gradient(600px_300px_at_50%_0%,rgba(0,229,255,.10),transparent_70%)] bg-[#071325] border border-[#1a3560] p-4">
                <svg viewBox="0 0 800 380" className="w-full h-full">
                  <defs><marker id="arr2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L6,3 z" fill="rgba(0,229,255,.6)"/></marker></defs>
                  <circle cx="400" cy="190" r="54" fill="rgba(0,229,255,.12)" stroke="rgba(0,229,255,.35)" strokeWidth="1.5"/>
                  <text x="400" y="195" textAnchor="middle" fontFamily="JetBrains Mono" fontSize="12" fill="#7beaff" fontWeight="800">CASE</text>
                  {(selected?.targets||[]).slice(0,8).map((t:string,i:number)=>{
                    const angle=(i/(Math.max(1,(selected?.targets||[]).slice(0,8).length))*Math.PI*2)-Math.PI/2;
                    const r=132, x=400+Math.cos(angle)*r, y=190+Math.sin(angle)*r;
                    return (
                      <g key={t}>
                        <line x1="400" y1="190" x2={x} y2={y} stroke="rgba(0,229,255,.22)" strokeDasharray="6 6" markerEnd="url(#arr2)"/>
                        <rect x={x-72} y={y-16} width="144" height="32" rx="16" fill="#0f2340" stroke="rgba(0,229,255,.22)"/>
                        <text x={x} y={y+4} textAnchor="middle" fontFamily="JetBrains Mono" fontSize="10" fill="#cfe0f2">{t.length>20? t.slice(0,20)+"…":t}</text>
                      </g>
                    )
                  })}
                </svg>
                {!(selected?.targets||[]).length&&<div className="absolute inset-0 grid place-items-center"><div className="px-4 py-2 rounded-full bg-[#0c1a2e] border border-[#1a3560] text-sm text-[#8ea6c0]">Add targets to see the graph</div></div>}
              </div>
            </div>
          )}

          {tab==="timeline"&&(
            <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] p-4">
              <div className="flex items-center justify-between"><h3 className="font-bold">Evidence timeline</h3><button onClick={()=>{setTab("lab"); setLabTab("prophet"); fetchProphet();}} className="text-xs px-2 py-1 rounded-full bg-[#ffd600]/10 border border-[#ffd600]/20 text-[#ffe27a]">Forecast with Prophet →</button></div>
              <div className="mt-4 relative pl-6 border-l border-[#1a3560] grid gap-3">
                {[...(selected?.evidence||[])].sort((a,b)=>String(a.observed_at).localeCompare(String(b.observed_at))).map((e:any)=>(
                  <div key={e.id||e.provenance_hash} className="relative p-3 rounded-xl bg-[#071325] border border-[#1a3560]">
                    <span className="absolute -left-[29px] top-4 w-3 h-3 rounded-full bg-[#00e5ff] shadow-[0_0_8px_#00e5ff] border-2 border-[#02070e]"/>
                    <div className="flex flex-wrap gap-2 items-center text-xs font-mono text-[#8ea6c0]"><span className="px-2 py-1 rounded-full bg-[#00e5ff]/10 border border-[#00e5ff]/15 text-[#7beaff]">{e.source}</span><span>{String(e.observed_at)}</span><span className="ml-auto px-2 py-1 rounded-full bg-white/5 border border-white/10">{Math.round(Number(e.confidence||0)*100)}%</span></div>
                    <div className="mt-1 font-mono text-sm text-[#cfe0f2]">{e.target}</div>
                    <div className="mt-1 font-mono text-[11px] text-[#5b7590] truncate">{e.provenance_hash}</div>
                  </div>
                ))}
                {!(selected?.evidence||[]).length&&<div className="p-8 text-center rounded-xl bg-[#071325] border border-dashed border-[#1a3560] text-sm text-[#5b7590]">No timeline yet.</div>}
              </div>
            </div>
          )}

          {tab==="score"&&(
            <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] p-6 grid md:grid-cols-[320px_1fr] gap-6 items-center">
              <div className="relative w-[280px] h-[280px] mx-auto grid place-items-center">
                <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
                  <circle cx="60" cy="60" r="54" fill="none" stroke="#0f2340" strokeWidth="10"/>
                  <circle cx="60" cy="60" r="54" fill="none" stroke="url(#g2)" strokeWidth="10" strokeLinecap="round" strokeDasharray={`${score*3.39} 339`} />
                  <defs><linearGradient id="g2" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stopColor="#00e5ff"/><stop offset="100%" stopColor="#7b2cff"/></linearGradient></defs>
                </svg>
                <div className="absolute inset-0 grid place-items-center"><div className="text-center"><div className="text-[54px] font-black tracking-[-0.04em] leading-none">{score}<span className="text-[18px] text-[#8ea6c0] font-bold">/100</span></div><div className="text-xs tracking-widest font-mono text-[#5b7590]">DETERMINISTIC SCORE</div></div></div>
              </div>
              <div>
                <h3 className="text-[18px] font-bold">Explainable confidence — no black box</h3>
                <p className="mt-2 text-sm leading-6 text-[#8ea6c0]">Score is the mean of evidence confidence values. For deeper reasoning, open <b>Shadow 360</b> for per-entity risk.</p>
                <button onClick={()=>{setTab("lab"); setLabTab("shadow")}} className="mt-3 px-3 py-2 rounded-xl bg-[#0a1830] border border-[#1a3560] text-sm">Open Shadow 360 →</button>
              </div>
            </div>
          )}

          {tab==="reports"&&(
            <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] p-4">
              <h3 className="font-bold">Deterministic reports</h3>
              <p className="text-sm text-[#8ea6c0]">Authenticated exports with prism vault hash + audit chain.</p>
              <div className="mt-4 grid md:grid-cols-3 gap-3">
                {[
                  {k:"md",title:"Markdown",desc:"Human-readable report",icon:"▭",color:"from-[#00e5ff]/15 to-transparent"},
                  {k:"html",title:"HTML",desc:"Shareable styled report",icon:"◈",color:"from-[#7b2cff]/15 to-transparent"},
                  {k:"json",title:"JSON Bundle",desc:"Machine-readable + LAB",icon:"⬢",color:"from-[#00ff9d]/10 to-transparent"},
                ].map(c=>(
                  <button key={c.k} onClick={()=>downloadReport(c.k as any)} disabled={!selected} className={`text-left p-4 rounded-2xl bg-gradient-to-b ${c.color} to-[#071325] border border-[#1a3560] hover:border-[#00e5ff]/30 transition disabled:opacity-40`}>
                    <div className="w-9 h-9 rounded-xl bg-white/5 border border-white/10 grid place-items-center text-[#7beaff]">{c.icon}</div>
                    <div className="mt-3 font-bold">{c.title}</div><div className="text-sm text-[#8ea6c0]">{c.desc}</div><div className="mt-3 inline-flex px-3 py-1.5 rounded-full bg-white text-[#02070e] text-xs font-extrabold">Download {c.k.toUpperCase()} →</div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {tab==="audit"&&(
            <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] overflow-hidden">
              <div className="p-4 border-b border-[#142a4a] flex items-center justify-between"><h3 className="font-bold">Tamper-evident audit</h3><span className="text-xs font-mono text-[#5b7590]">Hash-chained</span></div>
              <div className="overflow-auto">
                <table className="w-full text-sm">
                  <thead className="text-[11px] tracking-widest font-mono text-[#5b7590]"><tr className="border-b border-[#142a4a] bg-[#071325]/60"><th className="text-left p-3">TIME</th><th className="text-left p-3">ACTOR</th><th className="text-left p-3">ACTION</th><th className="text-left p-3">RESOURCE</th><th className="text-left p-3">HASH</th></tr></thead>
                  <tbody>{audit.map((r:any,i:number)=>(
                    <tr key={r.event_hash||i} className="border-b border-[#142a4a]/60 hover:bg-[#071325]/40">
                      <td className="p-3 font-mono text-xs text-[#8ea6c0]">{String(r.created_at).slice(0,19)}</td>
                      <td className="p-3 font-mono text-xs">{r.actor}</td>
                      <td className="p-3"><span className="px-2 py-1 rounded-full bg-white/5 border border-white/10 font-mono text-xs">{r.action}</span></td>
                      <td className="p-3 font-mono text-xs text-[#cfe0f2]">{r.resource}</td>
                      <td className="p-3 font-mono text-[11px] text-[#8ea6c0] truncate max-w-[160px]">{r.event_hash}</td>
                    </tr>
                  ))}</tbody>
                </table>
                {!audit.length&&<div className="p-10 text-center text-sm text-[#5b7590]">No audit events — open this tab to load.</div>}
              </div>
            </div>
          )}

          {tab==="intel"&&(
            <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] p-4">
              <div className="flex flex-wrap gap-3 items-center justify-between"><h3 className="font-bold">DNS / RDAP intelligence</h3><button onClick={()=>loadTab("intel")} disabled={!target} className="px-3 py-2 rounded-xl bg-[#0a1830] border border-[#1a3560] text-sm disabled:opacity-40">Lookup</button></div>
              <p className="text-sm text-[#8ea6c0] mt-1">Bounded and cached. Try Quantum for NL queries like “show all infra linked to this cert”.</p>
              {intel? <pre className="mt-4 p-4 rounded-xl bg-[#071325] border border-[#1a3560] overflow-auto text-xs leading-6 text-[#cfe0f2]">{JSON.stringify(intel,null,2)}</pre> : <div className="mt-4 p-10 text-center rounded-xl bg-[#071325] border border-dashed border-[#1a3560] text-sm text-[#5b7590]">No result yet.</div>}
            </div>
          )}

          {tab==="workflow"&&(
            <div className="rounded-2xl bg-[#0c1a2e] border border-[#142a4a] p-4">
              <h3 className="font-bold">Workflow & tags</h3>
              <div className="mt-4 grid md:grid-cols-[1fr_1fr] gap-4">
                <label className="grid gap-2"><span className="text-xs tracking-widest font-mono text-[#5b7590]">STATE</span>
                  <select value={meta?.workflow||"triage"} onChange={e=>setMeta({...meta,workflow:e.target.value})} className="px-3 py-3 rounded-xl bg-[#071325] border border-[#1a3560] text-sm outline-none">
                    {["triage","active","review","closed"].map(s=><option key={s} value={s}>{s}</option>)}
                  </select>
                </label>
                <label className="grid gap-2"><span className="text-xs tracking-widest font-mono text-[#5b7590]">TAGS (comma separated)</span>
                  <input placeholder="e.g. apt, phishing, infra" value={tags || ((meta?.tags||[]).join(", "))} onChange={e=>setTags(e.target.value)} className="px-3 py-3 rounded-xl bg-[#071325] border border-[#1a3560] text-sm outline-none"/>
                </label>
              </div>
              <button onClick={saveMeta} disabled={user.role==="viewer"||!selected} className="mt-4 px-4 py-2.5 rounded-xl bg-gradient-to-r from-[#00e5ff] to-[#7b2cff] text-[#02070e] font-extrabold text-sm disabled:opacity-40">Save workflow</button>
            </div>
          )}
        </div>
        <div className="mt-4 p-3 rounded-xl bg-[#071325] border border-[#1a3560] text-[11px] leading-5 text-[#5b7590] font-mono text-center">NEXUS LAB • prism • neural • shadow • prophet • quantum • copilot • All deterministic, bounded, auditable</div>
      </section>
    </div>

    {/* Copilot Drawer */}
    {copilotOpen&&(
      <div className="fixed inset-0 z-50 flex justify-end">
        <button onClick={()=>setCopilotOpen(false)} className="absolute inset-0 bg-black/40 backdrop-blur-sm"/>
        <div className="relative w-[380px] max-w-[92vw] h-full bg-gradient-to-b from-[#0c1a2e] to-[#02070e] border-l border-[#1a3560] shadow-[-24px_0_80px_rgba(0,0,0,.5)] flex flex-col">
          <div className="p-4 border-b border-[#1a3560] flex items-center justify-between">
            <div><div className="font-bold flex items-center gap-2">✦ NEXUS Copilot <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-[#00ff9d]/10 border border-[#00ff9d]/20 text-[#7dffc0] font-mono">LAB</span></div><div className="text-xs text-[#8ea6c0]">Ask in natural language — grounded in this case.</div></div>
            <button onClick={()=>setCopilotOpen(false)} className="w-8 h-8 rounded-full bg-white/5 border border-white/10 grid place-items-center">✕</button>
          </div>
          <div className="flex-1 overflow-auto p-4 grid gap-3 content-start">
            {!copilotMsgs.length&&<div className="p-4 rounded-xl bg-[#071325] border border-dashed border-[#1a3560] text-sm text-[#5b7590]">Try: <button onClick={()=>setCopilotQ("summarize this case")} className="text-[#7beaff]">summarize</button> • <button onClick={()=>setCopilotQ("what links these targets?")} className="text-[#7beaff]">what links these targets?</button> • <button onClick={()=>setCopilotQ("forecast next moves")} className="text-[#7beaff]">forecast</button></div>}
            {copilotMsgs.map((m,i)=>(
              <div key={i} className="grid gap-2">
                <div className="ml-auto max-w-[80%] px-3 py-2 rounded-2xl bg-gradient-to-r from-[#00e5ff] to-[#7b2cff] text-[#02070e] text-sm font-medium">{m.q}</div>
                <div className="mr-auto max-w-[88%] px-3 py-3 rounded-2xl bg-[#0a1830] border border-[#1a3560] text-sm leading-6 text-[#cfe0f2]">{m.a}</div>
              </div>
            ))}
          </div>
          <div className="p-3 border-t border-[#1a3560] flex gap-2">
            <input value={copilotQ} onChange={e=>setCopilotQ(e.target.value)} onKeyDown={e=>e.key==="Enter"&&askCopilot()} placeholder="Ask copilot…" className="flex-1 px-3 py-3 rounded-xl bg-[#071325] border border-[#1a3560] text-sm outline-none placeholder:text-[#5b7590]"/>
            <button onClick={askCopilot} className="px-4 py-3 rounded-xl bg-white text-[#02070e] font-bold text-sm">Send</button>
          </div>
          <div className="px-3 pb-3 text-[11px] font-mono text-[#5b7590]">Deterministic — no external LLM. Answers use only this case's evidence/entities.</div>
        </div>
      </div>
    )}

    {/* floating copilot button when closed */}
    {!copilotOpen&&<button onClick={()=>setCopilotOpen(true)} className="fixed right-4 bottom-4 z-40 w-14 h-14 rounded-full bg-gradient-to-br from-[#00e5ff] to-[#7b2cff] text-[#02070e] shadow-[0_12px_40px_rgba(0,229,255,.35)] grid place-items-center text-xl font-black hover:scale-105 transition">✦</button>}

    {sideOpen&&<button aria-label="Close sidebar" onClick={()=>setSideOpen(false)} className="fixed inset-0 z-30 bg-black/40 backdrop-blur-sm md:hidden"/>}
  </div>
 );
}

function Radar({axes}:{axes:Record<string,number>}){
 const keys=["infrastructure","identity","temporal","geospatial","hygiene","exposure"];
 const cx=120, cy=120, r=86;
 function pt(i:number,val:number){
   const a=(i/keys.length)*Math.PI*2 - Math.PI/2;
   const rr=r*val;
   return [cx+Math.cos(a)*rr, cy+Math.sin(a)*rr] as const;
 }
 const poly=keys.map((k,i)=>pt(i,axes[k]||0).join(",")).join(" ");
 const grid=[0.25,0.5,0.75,1].map(s=> keys.map((_,i)=>pt(i,s).join(",")).join(" "));
 return (
   <svg viewBox="0 0 240 240" className="w-[300px] h-[300px]">
     <defs><radialGradient id="rg" cx="50%" cy="50%"><stop offset="0%" stopColor="rgba(0,229,255,.18)"/><stop offset="100%" stopColor="rgba(0,0,0,0)"/></radialGradient></defs>
     <circle cx={cx} cy={cy} r={r+12} fill="url(#rg)"/>
     {grid.map((g,i)=><polygon key={i} points={g} fill="none" stroke="rgba(0,229,255,.12)" strokeWidth="1"/>)}
     {keys.map((_,i)=>{const [x,y]=pt(i,1); return <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke="rgba(0,229,255,.10)"/>})}
     <polygon points={poly} fill="rgba(0,229,255,.18)" stroke="#00e5ff" strokeWidth="2"/>
     {keys.map((k,i)=>{const [x,y]=pt(i,1); const [lx,ly]=pt(i,1.14); return <g key={k}><circle cx={x} cy={y} r="2.2" fill="#00e5ff"/><text x={lx} y={ly} textAnchor="middle" dominantBaseline="middle" fontFamily="JetBrains Mono" fontSize="8" fill="#8ea6c0">{k.slice(0,4).toUpperCase()}</text></g>})}
   </svg>
 );
}
