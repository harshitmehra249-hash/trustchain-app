"""Pydantic schemas for mesh network"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class MeshNodeRegister(BaseModel):
    """Mesh node registration schema"""
    device_id: str = Field(..., min_length=5, max_length=255)
    node_name: Optional[str] = Field(None, max_length=255)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: Optional[float] = None
    node_type: Optional[str] = Field(None, max_length=50)
    firmware_version: Optional[str] = Field(None, max_length=50)

    @validator('latitude', 'longitude')
    def validate_coordinates(cls, v: float) -> float:
        """Validate GPS coordinates"""
        if not isinstance(v, (int, float)):
            raise ValueError('Coordinates must be numeric')
        return v


class MeshNodeUpdate(BaseModel):
    """Mesh node update schema"""
    node_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    battery_level: Optional[int] = Field(None, ge=0, le=100)
    signal_strength: Optional[int] = None
    uptime_seconds: Optional[int] = None
    total_messages: Optional[int] = None
    failed_messages: Optional[int] = None

    @validator('battery_level')
    def validate_battery(cls, v: Optional[int]) -> Optional[int]:
        """Validate battery level"""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Battery level must be between 0 and 100')
        return v


class MeshNodeStatus(BaseModel):
    """Mesh node status schema"""
    id: int
    device_id: str
    node_name: Optional[str]
    latitude: float
    longitude: float
    altitude: Optional[float]
    is_active: bool
    battery_level: Optional[int]
    signal_strength: Optional[int]
    uptime_seconds: int
    total_messages: int
    failed_messages: int
    last_heartbeat: Optional[datetime]
    node_type: Optional[str]
    firmware_version: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MeshNodeResponse(MeshNodeStatus):
    """Extended mesh node response"""
    success_rate: Optional[float] = None  # Calculated as (total - failed) / total * 100


class MeshMessageSend(BaseModel):
    """Send mesh message schema"""
    destination_node_id: Optional[int] = None  # None for broadcast
    message_type: str = Field(..., max_length=50)
    message_content: str = Field(..., min_length=1, max_length=500)
    ttl: Optional[int] = Field(None, ge=1, le=255)


class MeshMessageResponse(BaseModel):
    """Mesh message response schema"""
    id: int
    source_node_id: int
    destination_node_id: Optional[int]
    message_type: str
    message_content: str
    hop_count: int
    route_path: Optional[List[int]]
    status: str
    retry_count: int
    created_at: datetime
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]

    class Config:
        from_attributes = True


class MeshNodeHealthLog(BaseModel):
    """Mesh node health log schema"""
    id: int
    node_id: int
    battery_level: Optional[int]
    signal_strength: Optional[int]
    temperature: Optional[float]
    free_memory: Optional[int]
    message_rate: Optional[float]
    success_rate: Optional[float]
    recorded_at: datetime

    class Config:
        from_attributes = True


class MeshNetworkStatus(BaseModel):
    """Overall mesh network status"""
    total_nodes: int
    active_nodes: int
    inactive_nodes: int
    average_battery: Optional[float]
    average_signal: Optional[float]
    total_messages: int
    failed_messages: int
    network_health: float  # 0-100


class MeshNodeHeartbeat(BaseModel):
    """Mesh node heartbeat schema"""
    device_id: str
    latitude: float
    longitude: float
    battery_level: Optional[int]
    signal_strength: Optional[int]
    uptime_seconds: Optional[int]
    total_messages: Optional[int]
    failed_messages: Optional[int]
