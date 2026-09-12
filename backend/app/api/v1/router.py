"""API v1 Router Configuration with Auth endpoints"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth

api_router = APIRouter()

# Health check endpoint
@api_router.get("/health")
async def health():
    """API health check"""
    return {"status": "API is running"}

# Include authentication router
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

# TODO: Add additional routers as features are implemented
# from app.api.v1.endpoints import disaster_requests, mesh, supply_chain, ai
# api_router.include_router(disaster_requests.router, prefix="/disaster-requests", tags=["Disaster Requests"])
# api_router.include_router(mesh.router, prefix="/mesh", tags=["Mesh Network"])
# api_router.include_router(supply_chain.router, prefix="/supply-chain", tags=["Supply Chain"])
# api_router.include_router(ai.router, prefix="/ai", tags=["AI Services"])
