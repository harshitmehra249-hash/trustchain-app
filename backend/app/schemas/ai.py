"""Validation schemas for AI-powered resource allocation."""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class NeedsAssessmentCreate(BaseModel):
    """Input submitted by a person or mesh node."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    urgency: int = Field(..., ge=1, le=100)
    category: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=10, max_length=2000)
    affected_people: int = Field(1, ge=1, le=1_000_000)
    accessibility: int = Field(50, ge=0, le=100)
    language: str = Field("en", min_length=2, max_length=30)


class NeedsAssessmentResponse(BaseModel):
    """Persisted request and its priority assessment."""

    id: int
    latitude: float
    longitude: float
    category: str
    priority_score: float
    status: str
    assessment: Optional[dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ResourceAllocationCreate(BaseModel):
    """Request to allocate a resource to a disaster request."""

    request_id: int = Field(..., gt=0)
    resource_type: str = Field(..., min_length=1, max_length=50)
    quantity: int = Field(..., gt=0)
    source_location: str = Field(..., min_length=1, max_length=255)
    destination_location: str = Field(..., min_length=1, max_length=255)


class RouteOptimizationRequest(BaseModel):
    """Coordinates for route optimization."""

    start_latitude: float = Field(..., ge=-90, le=90)
    start_longitude: float = Field(..., ge=-180, le=180)
    end_latitude: float = Field(..., ge=-90, le=90)
    end_longitude: float = Field(..., ge=-180, le=180)


class RouteOptimizationResponse(BaseModel):
    """Safe, deterministic route result."""

    distance_km: float
    estimated_minutes: int
    route: list[dict[str, float]]
    provider: str
    fallback: bool
