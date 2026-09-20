"""API v1 router."""

from fastapi import APIRouter
from app.api.v1.endpoints import ai, auth, mesh, supply_chain

api_router = APIRouter()


@api_router.get("/health")
async def health() -> dict[str, str]:
    """API health check."""
    return {"status": "API is running"}


api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(mesh.router, prefix="/mesh", tags=["Mesh Network"])
api_router.include_router(supply_chain.router, prefix="/supply-chain", tags=["Supply Chain"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Resource Allocation"])
