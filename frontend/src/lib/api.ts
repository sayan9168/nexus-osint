const API=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000/api/v1";
export type InvestigationResult={status:string;report:string;entities_found:number;correlations_found:number;transforms_executed:string[]};
export async function triggerInvestigation(target:string,goal:string,maxIterations:number):Promise<InvestigationResult>{
 const token=typeof window!=="undefined"?localStorage.getItem("nexus_token"):null;
 if(!token)throw new Error("Authentication required");
 const response=await fetch(`${API}/agent/investigate`,{method:"POST",headers:{"Content-Type":"application/json",Authorization:`Bearer ${token}`},body:JSON.stringify({target,goal,max_iterations:Math.max(1,Math.min(maxIterations,20))})});
 const data=await response.json().catch(()=>({}));
 if(!response.ok)throw new Error(data.detail||`HTTP ${response.status}`);
 return data as InvestigationResult;
}
