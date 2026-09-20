"""Real-time dashboard analytics models."""

from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, JSON, String
from app.db.base import Base


class DashboardEvent(Base):
    """Immutable event used by the dashboard activity feed."""

    __tablename__ = "dashboard_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(80), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    severity = Column(String(20), nullable=False, default="info")
    actor_id = Column(Integer, nullable=True, index=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class DisasterZoneMetric(Base):
    """Cached severity metric for a map zone."""

    __tablename__ = "disaster_zone_metrics"

    id = Column(Integer, primary_key=True, index=True)
    zone_name = Column(String(255), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    severity = Column(Integer, nullable=False, default=0)
    affected_people = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
