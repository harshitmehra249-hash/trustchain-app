"""Deterministic AI orchestration with a safe rule-based fallback."""

from math import asin, cos, radians, sin, sqrt
from typing import Any
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai import DisasterRequest, ResourceAllocation


CATEGORY_BASE_SCORE = {
    "medical": 95,
    "medicine": 95,
    "shelter": 70,
    "food": 60,
    "water": 75,
    "rescue": 90,
    "other": 40,
}


def calculate_priority(urgency: int, category: str, affected_people: int, accessibility: int) -> float:
    """Calculate a bounded priority score without requiring an external model."""
    category_score = CATEGORY_BASE_SCORE.get(category.lower(), 40)
    people_score = min(20.0, sqrt(affected_people) * 2.0)
    access_score = (100 - accessibility) * 0.10
    return round(min(100.0, max(0.0, urgency * 0.55 + category_score * 0.25 + people_score + access_score)), 2)


def _assessment(category: str, affected_people: int, accessibility: int) -> dict[str, Any]:
    """Return explainable fallback assessment details."""
    return {
        "engine": "rule-based-fallback",
        "category": category,
        "affected_people": affected_people,
        "accessibility": accessibility,
        "reason": "External AI agents are optional; deterministic scoring keeps response available offline.",
    }


def haversine_km(start_lat: float, start_lng: float, end_lat: float, end_lng: float) -> float:
    """Calculate great-circle distance between two coordinates."""
    earth_radius = 6371.0
    lat_delta = radians(end_lat - start_lat)
    lng_delta = radians(end_lng - start_lng)
    value = sin(lat_delta / 2) ** 2 + cos(radians(start_lat)) * cos(radians(end_lat)) * sin(lng_delta / 2) ** 2
    return round(earth_radius * 2 * asin(sqrt(value)), 2)


class AIResourceService:
    """Needs assessment, prioritization, allocation, and route services."""

    @staticmethod
    async def assess_needs(payload: dict[str, Any], db: AsyncSession) -> DisasterRequest:
        """Persist a request and calculate its explainable priority score."""
        score = calculate_priority(payload["urgency"], payload["category"], payload["affected_people"], payload["accessibility"])
        request = DisasterRequest(**payload, priority_score=score, assessment=_assessment(payload["category"], payload["affected_people"], payload["accessibility"]))
        db.add(request)
        await db.commit()
        await db.refresh(request)
        return request

    @staticmethod
    async def prioritized_requests(limit: int, db: AsyncSession) -> list[DisasterRequest]:
        """Return highest-priority pending requests first."""
        result = await db.execute(select(DisasterRequest).where(DisasterRequest.status == "pending").order_by(desc(DisasterRequest.priority_score), DisasterRequest.created_at).limit(limit))
        return list(result.scalars().all())

    @staticmethod
    async def allocate(payload: dict[str, Any], db: AsyncSession) -> ResourceAllocation:
        """Create an allocation and mark the request as allocated."""
        request = await db.get(DisasterRequest, payload["request_id"])
        if request is None:
            raise ValueError("Disaster request not found")
        allocation = ResourceAllocation(**payload)
        request.status = "allocated"
        db.add(allocation)
        await db.commit()
        await db.refresh(allocation)
        return allocation
