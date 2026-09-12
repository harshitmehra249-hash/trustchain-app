"""Mesh network endpoints"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.schemas.mesh import (
    MeshNodeRegister,
    MeshNodeUpdate,
    MeshNodeStatus,
    MeshMessageSend,
    MeshMessageResponse,
    MeshNetworkStatus,
    MeshNodeHeartbeat,
)
from app.services.mesh import MeshService
from app.dependencies import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/nodes/register",
    response_model=MeshNodeStatus,
    status_code=status.HTTP_201_CREATED,
)
async def register_mesh_node(
    node_data: MeshNodeRegister,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Register a new mesh node.
    
    Args:
        node_data: Node registration data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Registered node status
    """
    try:
        result = await MeshService.register_node(
            device_id=node_data.device_id,
            latitude=node_data.latitude,
            longitude=node_data.longitude,
            node_name=node_data.node_name,
            node_type=node_data.node_type,
            firmware_version=node_data.firmware_version,
            db=db,
        )
        return result
    except ValueError as e:
        logger.warning(f"Node registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error during node registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during node registration",
        )


@router.get(
    "/nodes/{node_id}/status",
    response_model=MeshNodeStatus,
)
async def get_node_status(
    node_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get mesh node status.
    
    Args:
        node_id: Node ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Node status
    """
    try:
        result = await MeshService.get_node_status(node_id, db)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Node with id {node_id} not found",
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting node status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching node status",
        )


@router.get(
    "/nodes/active",
    response_model=list[MeshNodeStatus],
)
async def get_active_nodes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all active mesh nodes.
    
    Args:
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of active nodes
    """
    try:
        result = await MeshService.get_active_nodes(db)
        return result
    except Exception as e:
        logger.error(f"Error getting active nodes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching active nodes",
        )


@router.post(
    "/nodes/{node_id}/heartbeat",
    response_model=MeshNodeStatus,
)
async def node_heartbeat(
    node_id: int,
    heartbeat_data: MeshNodeHeartbeat,
    db: AsyncSession = Depends(get_db),
):
    """
    Update node heartbeat and metrics.
    
    Args:
        node_id: Node ID
        heartbeat_data: Heartbeat data
        db: Database session
        
    Returns:
        Updated node status
    """
    try:
        result = await MeshService.update_node_heartbeat(
            device_id=heartbeat_data.device_id,
            battery_level=heartbeat_data.battery_level,
            signal_strength=heartbeat_data.signal_strength,
            uptime_seconds=heartbeat_data.uptime_seconds,
            total_messages=heartbeat_data.total_messages,
            failed_messages=heartbeat_data.failed_messages,
            db=db,
        )
        return result
    except ValueError as e:
        logger.warning(f"Heartbeat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error updating heartbeat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating heartbeat",
        )


@router.post(
    "/messages/send",
    response_model=MeshMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_mesh_message(
    source_node_id: int,
    message_data: MeshMessageSend,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send a mesh message.
    
    Args:
        source_node_id: Source node ID
        message_data: Message data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Message data
    """
    try:
        result = await MeshService.send_message(
            source_node_id=source_node_id,
            destination_node_id=message_data.destination_node_id,
            message_type=message_data.message_type,
            message_content=message_data.message_content,
            ttl=message_data.ttl,
            db=db,
        )
        return result
    except ValueError as e:
        logger.warning(f"Message send error: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while sending message",
        )


@router.get(
    "/network/status",
    response_model=MeshNetworkStatus,
)
async def get_network_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get overall mesh network status.
    
    Args:
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Network status
    """
    try:
        result = await MeshService.get_network_status(db)
        return result
    except Exception as e:
        logger.error(f"Error getting network status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching network status",
        )
