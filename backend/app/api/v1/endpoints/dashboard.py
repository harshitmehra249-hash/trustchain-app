"""Real-time dashboard endpoints and WebSocket stream."""

import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.dashboard import ActivityEventResponse, DashboardSummary, DisasterZoneResponse
from app.services.dashboard import DashboardService

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Return dashboard aggregates."""
    return await DashboardService.summary(db)


@router.get("/activity", response_model=list[ActivityEventResponse])
async def dashboard_activity(
    limit: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list:
    """Return recent operational events."""
    return await DashboardService.activity(limit, db)


@router.get("/zones", response_model=list[DisasterZoneResponse])
async def dashboard_zones(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list:
    """Return severity zones for map rendering."""
    return await DashboardService.zones(db)


@router.websocket("/ws")
async def dashboard_websocket(websocket: WebSocket) -> None:
    """Push lightweight refresh signals every 30 seconds."""
    await websocket.accept()
    try:
        while True:
            await websocket.send_text(json.dumps({"type": "dashboard.refresh"}))
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        return
    except asyncio.CancelledError:
        return
