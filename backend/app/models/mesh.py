"""Mesh network models and database schema"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from app.db.base import Base


class MeshNode(Base):
    """Mesh network node model"""
    __tablename__ = "mesh_nodes"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), unique=True, index=True, nullable=False)
    node_name = Column(String(255), nullable=True)
    
    # Location
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    location_name = Column(String(255), nullable=True)
    
    # Node status
    is_active = Column(Boolean, default=True, nullable=False)
    last_heartbeat = Column(DateTime, nullable=True)
    battery_level = Column(Integer, nullable=True)  # 0-100
    signal_strength = Column(Integer, nullable=True)  # dBm
    
    # Metrics
    uptime_seconds = Column(Integer, default=0, nullable=False)
    total_messages = Column(Integer, default=0, nullable=False)
    failed_messages = Column(Integer, default=0, nullable=False)
    
    # Metadata
    node_type = Column(String(50), nullable=True)  # 'esp32', 'lora', 'wifi', etc.
    firmware_version = Column(String(50), nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<MeshNode(id={self.id}, device_id={self.device_id}, is_active={self.is_active})>"


class MeshMessage(Base):
    """Mesh network message model"""
    __tablename__ = "mesh_messages"

    id = Column(Integer, primary_key=True, index=True)
    source_node_id = Column(Integer, ForeignKey("mesh_nodes.id"), nullable=False)
    destination_node_id = Column(Integer, ForeignKey("mesh_nodes.id"), nullable=True)
    
    # Message content
    message_type = Column(String(50), nullable=False)  # 'alert', 'status', 'data', etc.
    message_content = Column(String(500), nullable=False)
    
    # Routing
    hop_count = Column(Integer, default=0, nullable=False)
    route_path = Column(JSON, nullable=True)  # List of node IDs
    ttl = Column(Integer, nullable=True)  # Time to live
    
    # Status
    status = Column(String(50), default="pending", nullable=False)  # pending, sent, delivered, failed
    retry_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<MeshMessage(id={self.id}, source_node_id={self.source_node_id}, status={self.status})>"


class MeshNodeHealthLog(Base):
    """Health metrics log for mesh nodes"""
    __tablename__ = "mesh_node_health_logs"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("mesh_nodes.id"), nullable=False, index=True)
    
    # Metrics snapshot
    battery_level = Column(Integer, nullable=True)
    signal_strength = Column(Integer, nullable=True)
    temperature = Column(Float, nullable=True)
    free_memory = Column(Integer, nullable=True)
    
    # Performance
    message_rate = Column(Float, nullable=True)  # messages per minute
    success_rate = Column(Float, nullable=True)  # 0-100
    
    # Timestamp
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<MeshNodeHealthLog(node_id={self.node_id}, recorded_at={self.recorded_at})>"
