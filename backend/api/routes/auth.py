from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from api.security import current_user
from osint_core.auth import authenticate, create_user, issue_session
router = APIRouter()
class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=10, max_length=256)
@router.post("/register")
def register(body: Credentials):
    try: user=create_user(body.username,body.password,"viewer")
    except ValueError as exc: raise HTTPException(400,str(exc)) from exc
    return {"user":user,"token":issue_session(user)}
@router.post("/login")
def login(body: Credentials):
    user=authenticate(body.username,body.password)
    if not user: raise HTTPException(401,"invalid credentials")
    return {"user":user,"token":issue_session(user)}
@router.get("/me")
def me(user=Depends(current_user)): return {"user":user}
