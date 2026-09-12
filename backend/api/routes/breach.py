"""Authorized breach-exposure metadata endpoints."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from api.security import get_current_user
from osint_core.breach_exposure import check_account

router=APIRouter()

@router.get("/account")
async def breach_account(account: str=Query(...,min_length=3,max_length=320), _: dict=Depends(get_current_user)):
    try:
        return await check_account(account)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
