"""Dashboard aggregation and cache service."""

from datetime import datetime, timedelta, timezone
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai import DisasterRequest, ResourceAllocation
from app.models.dashboard import DashboardEvent, DisasterZoneMetric
from app.models.mesh import MeshNode
from app.models.supply_chain import SupplyChainItem
from app.models.user import User, UserRole


class DashboardService:
    """Build dashboard data from operational tables."""

    @staticmethod
    async def summary(db: AsyncSession) -> dict:
        """Return aggregate metrics and a short-term deterministic forecast."""
        requests = await db.execute(select(func.count(DisasterRequest.id)))
        pending = await db.execute(select(func.count(DisasterRequest.id)).where(DisasterRequest.status == "pending"))
        allocated = await db.execute(select(func.count(DisasterRequest.id)).where(DisasterRequest.status == "allocated"))
        nodes = await db.execute(select(func.count(MeshNode.id)).where(MeshNode.is_active.is_(True)))
        items = await db.execute(select(func.count(SupplyChainItem.id)))
        delivered = await db.execute(select(func.count(SupplyChainItem.id)).where(SupplyChainItem.status == "delivered"))
        volunteers = await db.execute(select(func.count(User.id)).where(User.role == UserRole.VOLUNTEER))

        category_result = await db.execute(
            select(DisasterRequest.category, func.count(DisasterRequest.id))
            .group_by(DisasterRequest.category)
        )
        allocation_by_category = {category: count for category, count in category_result.all()}

        now = datetime.now(timezone.utc)
        forecast = [
            {"window": "next_6_hours", "expected_requests": max(0, int((pending.scalar() or 0) * 0.35))},
            {"window": "next_12_hours", "expected_requests": max(0, int((pending.scalar() or 0) * 0.65))},
            {"window": "next_24_hours", "expected_requests": max(0, int((pending.scalar() or 0) * 1.1))},
        ]
        return {
            "generated_at": now,
            "total_requests": requests.scalar() or 0,
            "pending_requests": pending.scalar() or 0,
            "allocated_requests": allocated.scalar() or 0,
            "active_mesh_nodes": nodes.scalar() or 0,
            "total_supply_items": items.scalar() or 0,
            "delivered_supply_items": delivered.scalar() or 0,
            "volunteers": volunteers.scalar() or 0,
            "allocation_by_category": allocation_by_category,
            "forecast": forecast,
            "stale": False,
        }

    @staticmethod
    async def activity(limit: int, db: AsyncSession) -> list[DashboardEvent]:
        """Return newest activity events."""
        result = await db.execute(
            select(DashboardEvent).order_by(DashboardEvent.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def zones(db: AsyncSession) -> list[DisasterZoneMetric]:
        """Return current disaster zone metrics."""
        result = await db.execute(select(DisasterZoneMetric).order_by(DisasterZoneMetric.severity.desc()))
        return list(result.scalars().all())
