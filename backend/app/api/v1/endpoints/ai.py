"""AI resource allocation API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.ai import NeedsAssessmentCreate, NeedsAssessmentResponse, ResourceAllocationCreate, RouteOptimizationRequest, RouteOptimizationResponse
from app.services.ai import AIResourceService, haversine_km

router = APIRouter()


@router.post("/assess-needs", response_model=NeedsAssessmentResponse, status_code=status.HTTP_201_CREATED)
async def assess_needs(payload: NeedsAssessmentCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> DisasterRequest:
    """Submit and prioritize a disaster-relief request."""
    data = payload.model_dump()
    data["requester_id"] = current_user.id
    return await AIResourceService.assess_needs(data, db)


@router.get("/prioritized-requests", response_model=list[NeedsAssessmentResponse])
async def prioritized_requests(limit: int = Query(50, ge=1, le=100), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[DisasterRequest]:
    """List pending requests ordered by priority."""
    return await AIResourceService.prioritized_requests(limit, db)


@router.post("/allocate-resources")
async def allocate_resources(payload: ResourceAllocationCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict:
    """Allocate a resource, returning a clear 404 for unknown requests."""
    try:
        allocation = await AIResourceService.allocate(payload.model_dump(), db)
        return {"success": True, "data": {"id": allocation.id, "request_id": allocation.request_id, "status": allocation.status}}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/route-optimization", response_model=RouteOptimizationResponse)
async def route_optimization(payload: RouteOptimizationRequest = Depends(), current_user: User = Depends(get_current_user)) -> RouteOptimizationResponse:
    """Return a deterministic straight-line route when a routing provider is unavailable."""
    distance = haversine_km(payload.start_latitude, payload.start_longitude, payload.end_latitude, payload.end_longitude)
    return RouteOptimizationResponse(
        distance_km=distance,
        estimated_minutes=max(1, round(distance / 40 * 60)),
        route=[
            {"latitude": payload.start_latitude, "longitude": payload.start_longitude},
            {"latitude": payload.end_latitude, "longitude": payload.end_longitude},
        ],
        provider="offline-fallback",
        fallback=True,
    )
