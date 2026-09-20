"""Dashboard response schemas."""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class DashboardSummary(BaseModel):
    """Aggregated operational metrics."""

    generated_at: datetime
    total_requests: int
    pending_requests: int
    allocated_requests: int
    active_mesh_nodes: int
    total_supply_items: int
    delivered_supply_items: int
    volunteers: int
    allocation_by_category: dict[str, int]
    forecast: list[dict[str, Any]]
    stale: bool = False
    warning: Optional[str] = None


class ActivityEventResponse(BaseModel):
    """Activity feed event."""

    id: int
    event_type: str
    title: str
    description: str
    severity: str
    metadata: Optional[dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DisasterZoneResponse(BaseModel):
    """Map severity zone."""

    id: int
    zone_name: str
    latitude: float
    longitude: float
    severity: int = Field(..., ge=0, le=100)
    affected_people: int
    updated_at: datetime

    class Config:
        from_attributes = True
