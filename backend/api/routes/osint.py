from fastapi import APIRouter

from osint_core.models import ScanRequest, ScanResponse
from osint_core.service import OSINTService

router = APIRouter()
service = OSINTService()


@router.post("/scan", response_model=ScanResponse)
async def scan(request: ScanRequest) -> ScanResponse:
    """Run a bounded public-source OSINT collection after authorization is declared."""
    return service.scan(request.target, request.target_type, request.authorized)
