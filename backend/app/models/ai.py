"""Disaster request and AI allocation models."""

from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, JSON, String, Text
from app.db.base import Base


class DisasterRequest(Base):
    """A request for disaster-relief assistance."""

    __tablename__ = "disaster_requests"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, nullable=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    urgency = Column(Integer, nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    affected_people = Column(Integer, nullable=False, default=1)
    accessibility = Column(Integer, nullable=False, default=50)
    language = Column(String(30), nullable=False, default="en")
    status = Column(String(30), nullable=False, default="pending", index=True)
    priority_score = Column(Float, nullable=False, default=0)
    assessment = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ResourceAllocation(Base):
    """An allocation decision produced by the resource engine."""

    __tablename__ = "resource_allocations"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    source_location = Column(String(255), nullable=False)
    destination_location = Column(String(255), nullable=False)
    route = Column(JSON, nullable=True)
    status = Column(String(30), nullable=False, default="planned")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
