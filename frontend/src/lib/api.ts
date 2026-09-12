import type { TransformInfo } from "@/lib/types";
const API=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000/api/v1";
export type InvestigationResult={status:string;report:string;entities_found:number;correlations_found:number;transforms_executed:string[]};
export type ApiGraphNode={id:string;label:string;value:string;properties?:Record<string,unknown>};
export type ApiGraphEdge={source:string;target:string;type:string;properties?:Record<string,unknown>};
export type ApiGraph={nodes:ApiGraphNode[];edges:ApiGraphEdge[];total_nodes?:number;total_edges?:number};
export type ApiTransform={name:string;description?:string;input_type?:string;input_types?:string[];output_types?:string[];[key:string]:unknown};
function authHeaders():HeadersInit{const token=typeof window!=="undefined"?localStorage.getItem("nexus_token"):null;if(!token)throw new Error("Authentication required");return {Authorization:`Bearer ${token}`};}
async function request<T>(path:string,init?:RequestInit):Promise<T>{const response=await fetch(`${API}${path}`,{...init,headers:{"Content-Type":"application/json",...authHeaders(),...(init?.headers||{})}});const data=await response.json().catch(()=>({}));if(!response.ok)throw new Error((data as any).detail||`HTTP ${response.status}`);return data as T;}
export async function triggerInvestigation(target:string,goal:string,maxIterations:number):Promise<InvestigationResult>{
 const token=typeof window!=="undefined"?localStorage.getItem("nexus_token"):null;
 if(!token)throw new Error("Authentication required");
 const response=await fetch(`${API}/agent/investigate`,{method:"POST",headers:{"Content-Type":"application/json",Authorization:`Bearer ${token}`},body:JSON.stringify({target,goal,max_iterations:Math.max(1,Math.min(maxIterations,20))})});
 const data=await response.json().catch(()=>({}));
 if(!response.ok)throw new Error(data.detail||`HTTP ${response.status}`);
 return data as InvestigationResult;
}
export async function deleteEntity(entityId:string):Promise<{status:string;id:string}>{return request(`/entities/${encodeURIComponent(entityId)}`,{method:"DELETE"});}
export async function listTransforms():Promise<TransformInfo[]>{const data=await request<{transforms:ApiTransform[]}>("/transforms/");return (data.transforms||[]).map(t=>({name:t.name,input_type:t.input_type||t.input_types?.[0]||"Unknown",output_types:t.output_types||[],description:t.description}));}
export async function fetchFullGraph():Promise<ApiGraph>{return request<ApiGraph>("/graph/full");}
export async function executeTransform(transformName:string,entityType:string,entityValue:string,parameters:Record<string,unknown>={}){return request<any>("/transforms/execute",{method:"POST",body:JSON.stringify({transform_name:transformName,entity_type:entityType,entity_value:entityValue,parameters,async_execution:false})});}
