"""NEXUS-OSINT application entry point."""
from contextlib import asynccontextmanager
import os,time
import structlog
from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config import get_settings
from db.memgraph import get_memgraph
from api.app import create_router
from api.websocket.graph_ws import router as ws_router
from api.routes.auth import router as auth_router
from osint_core.auth import bootstrap_admin,decode_session
from osint_core.rbac import allowed
logger=structlog.get_logger(__name__);settings=get_settings()
@asynccontextmanager
async def lifespan(app:FastAPI):
 logger.info("app.starting",version=settings.APP_VERSION);bootstrap_admin();memgraph=await get_memgraph();logger.info("app.memgraph_connected");yield;await memgraph.disconnect();logger.info("app.shutdown_complete")
app=FastAPI(title=settings.APP_NAME,version=settings.APP_VERSION,description="AI-Native OSINT & 3D Link Analysis Platform",lifespan=lifespan)
origins=[x.strip() for x in os.getenv("NEXUS_CORS_ORIGINS","http://localhost:3000").split(",") if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],allow_headers=["Authorization","Content-Type"],max_age=600)
_RATE={}
def permission_for(path,method):
 if path.endswith("/audit"):return "audit:read"
 if "/jobs" in path:return "job:run"
 if path.startswith("/api/v1/cases") or path.startswith("/api/v1/intelligence/entities"):return "case:write" if method in {"POST","PUT","PATCH","DELETE"} else "case:read"
 if path.startswith("/api/v1/osint") or path.endswith("/dns-rdap"):return "scan:run" if method in {"POST","PUT","PATCH"} else "case:read"
 if path.startswith("/api/v1/reports"):return "report:read"
 if path.startswith("/api/v1/investigation-graph") or path.startswith("/api/v1/graph"):return "graph:read"
 return None
@app.middleware("http")
async def security_middleware(request:Request,call_next):
 length=request.headers.get("content-length")
 if length and length.isdigit() and int(length)>2_000_000:return JSONResponse({"detail":"request too large"},status_code=413)
 path=request.url.path
 if path.startswith("/api/v1/") and not path.startswith("/api/v1/auth/"):
  auth=request.headers.get("Authorization","")
  if not auth.startswith("Bearer "):return JSONResponse({"detail":"Bearer session required"},status_code=401)
  try:user=decode_session(auth[7:].strip())
  except ValueError as exc:return JSONResponse({"detail":str(exc)},status_code=401)
  permission=permission_for(path,request.method)
  if permission and not allowed(user.get("role",""),permission):return JSONResponse({"detail":"Insufficient role"},status_code=403)
  key=request.client.host if request.client else "unknown";now=time.monotonic();recent=[t for t in _RATE.get(key,[]) if now-t<60]
  if len(recent)>=120:return JSONResponse({"detail":"rate limit exceeded"},status_code=429)
  recent.append(now);_RATE[key]=recent
 response=await call_next(request)
 response.headers["X-Content-Type-Options"]="nosniff";response.headers["X-Frame-Options"]="DENY";response.headers["Referrer-Policy"]="no-referrer";response.headers["Content-Security-Policy"]="default-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'"
 return response
app.include_router(auth_router,prefix="/api/v1/auth",tags=["Authentication"]);app.include_router(create_router(),prefix="/api/v1");app.include_router(ws_router)
@app.get("/health")
async def health_check():return {"status":"healthy","service":settings.APP_NAME,"version":settings.APP_VERSION}
