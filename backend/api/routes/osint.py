from fastapi import APIRouter, HTTPException

from osint_core.cases import store
from osint_core.models import ScanRequest, ScanResponse
from osint_core.service import OSINTService

router = APIRouter()
service = OSINTService()


@router.post("/scan", response_model=ScanResponse)
async def scan(request: ScanRequest) -> ScanResponse:
    """Run bounded public-source collection and optionally attach evidence to a case."""
    if request.case_id and not store.get(request.case_id):
        raise HTTPException(status_code=404, detail="Case not found")

    result = service.scan(request.target, request.target_type, request.authorized)
    if request.case_id:
        for evidence in result.evidence:
            store.add_evidence(request.case_id, evidence)
        result.case_id = request.case_id
    return result
