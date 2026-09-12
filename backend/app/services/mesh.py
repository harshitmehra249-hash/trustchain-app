"""Mesh network service"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
import logging

from app.models.mesh import MeshNode, MeshMessage, MeshNodeHealthLog
from app.core.config import settings

logger = logging.getLogger(__name__)


class MeshService:
    """Mesh network service"""

    @staticmethod
    async def register_node(
        device_id: str,
        latitude: float,
        longitude: float,
        node_name: Optional[str],
        node_type: Optional[str],
        firmware_version: Optional[str],
        db: AsyncSession,
    ) -> dict:
        """
        Register a new mesh node.
        
        Args:
            device_id: Unique device identifier
            latitude: Node latitude
            longitude: Node longitude
            node_name: Human-readable node name
            node_type: Type of node (esp32, lora, etc.)
            firmware_version: Node firmware version
            db: Database session
            
        Returns:
            Registered node data
            
        Raises:
            ValueError: If device_id already exists or invalid coordinates
        """
        try:
            # Check if node already exists
            query = select(MeshNode).where(MeshNode.device_id == device_id)
            existing_node = await db.execute(query)
            if existing_node.scalar_one_or_none():
                raise ValueError(f"Node with device_id '{device_id}' already exists")

            # Create new node
            node = MeshNode(
                device_id=device_id,
                node_name=node_name,
                latitude=latitude,
                longitude=longitude,
                node_type=node_type,
                firmware_version=firmware_version,
                is_active=True,
                last_heartbeat=datetime.now(timezone.utc),
            )
            db.add(node)
            await db.commit()

            logger.info(f"Mesh node registered: {device_id}")
            return {
                "id": node.id,
                "device_id": node.device_id,
                "node_name": node.node_name,
                "latitude": node.latitude,
                "longitude": node.longitude,
                "is_active": node.is_active,
            }
        except Exception as e:
            await db.rollback()
            logger.error(f"Error registering mesh node: {e}")
            raise

    @staticmethod
    async def get_node_status(
        node_id: int,
        db: AsyncSession,
    ) -> Optional[dict]:
        """
        Get mesh node status.
        
        Args:
            node_id: Node ID
            db: Database session
            
        Returns:
            Node status data
        """
        try:
            node = await db.get(MeshNode, node_id)
            if not node:
                return None

            # Calculate success rate
            success_rate = None
            if node.total_messages > 0:
                success_rate = (
                    (node.total_messages - node.failed_messages)
                    / node.total_messages
                    * 100
                )

            return {
                "id": node.id,
                "device_id": node.device_id,
                "node_name": node.node_name,
                "latitude": node.latitude,
                "longitude": node.longitude,
                "altitude": node.altitude,
                "is_active": node.is_active,
                "battery_level": node.battery_level,
                "signal_strength": node.signal_strength,
                "uptime_seconds": node.uptime_seconds,
                "total_messages": node.total_messages,
                "failed_messages": node.failed_messages,
                "success_rate": success_rate,
                "last_heartbeat": node.last_heartbeat,
                "node_type": node.node_type,
                "firmware_version": node.firmware_version,
            }
        except Exception as e:
            logger.error(f"Error getting node status: {e}")
            raise

    @staticmethod
    async def get_active_nodes(db: AsyncSession) -> List[dict]:
        """
        Get all active mesh nodes.
        
        Args:
            db: Database session
            
        Returns:
            List of active nodes
        """
        try:
            query = select(MeshNode).where(MeshNode.is_active == True)
            result = await db.execute(query)
            nodes = result.scalars().all()

            response = []
            for node in nodes:
                success_rate = None
                if node.total_messages > 0:
                    success_rate = (
                        (node.total_messages - node.failed_messages)
                        / node.total_messages
                        * 100
                    )

                response.append(
                    {
                        "id": node.id,
                        "device_id": node.device_id,
                        "node_name": node.node_name,
                        "latitude": node.latitude,
                        "longitude": node.longitude,
                        "is_active": node.is_active,
                        "battery_level": node.battery_level,
                        "signal_strength": node.signal_strength,
                        "uptime_seconds": node.uptime_seconds,
                        "success_rate": success_rate,
                        "last_heartbeat": node.last_heartbeat,
                    }
                )

            return response
        except Exception as e:
            logger.error(f"Error getting active nodes: {e}")
            raise

    @staticmethod
    async def update_node_heartbeat(
        device_id: str,
        battery_level: Optional[int],
        signal_strength: Optional[int],
        uptime_seconds: Optional[int],
        total_messages: Optional[int],
        failed_messages: Optional[int],
        db: AsyncSession,
    ) -> dict:
        """
        Update node heartbeat and metrics.
        
        Args:
            device_id: Node device ID
            battery_level: Current battery level (0-100)
            signal_strength: Signal strength in dBm
            uptime_seconds: Uptime in seconds
            total_messages: Total messages sent
            failed_messages: Failed messages
            db: Database session
            
        Returns:
            Updated node data
            
        Raises:
            ValueError: If node not found
        """
        try:
            query = select(MeshNode).where(MeshNode.device_id == device_id)
            result = await db.execute(query)
            node = result.scalar_one_or_none()

            if not node:
                raise ValueError(f"Node with device_id '{device_id}' not found")

            # Update node
            node.last_heartbeat = datetime.now(timezone.utc)
            if battery_level is not None:
                node.battery_level = battery_level
            if signal_strength is not None:
                node.signal_strength = signal_strength
            if uptime_seconds is not None:
                node.uptime_seconds = uptime_seconds
            if total_messages is not None:
                node.total_messages = total_messages
            if failed_messages is not None:
                node.failed_messages = failed_messages

            await db.commit()

            # Log health metrics
            health_log = MeshNodeHealthLog(
                node_id=node.id,
                battery_level=battery_level,
                signal_strength=signal_strength,
            )
            db.add(health_log)
            await db.commit()

            logger.info(f"Node heartbeat updated: {device_id}")
            return await MeshService.get_node_status(node.id, db)
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating node heartbeat: {e}")
            raise

    @staticmethod
    async def send_message(
        source_node_id: int,
        destination_node_id: Optional[int],
        message_type: str,
        message_content: str,
        ttl: Optional[int],
        db: AsyncSession,
    ) -> dict:
        """
        Send a mesh message.
        
        Args:
            source_node_id: Source node ID
            destination_node_id: Destination node ID (None for broadcast)
            message_type: Type of message
            message_content: Message content
            ttl: Time to live (hops)
            db: Database session
            
        Returns:
            Message data
            
        Raises:
            ValueError: If source node not found
        """
        try:
            # Verify source node exists
            source_node = await db.get(MeshNode, source_node_id)
            if not source_node:
                raise ValueError(f"Source node with id {source_node_id} not found")

            # Create message
            message = MeshMessage(
                source_node_id=source_node_id,
                destination_node_id=destination_node_id,
                message_type=message_type,
                message_content=message_content,
                ttl=ttl or 255,
                status="pending",
                hop_count=0,
                route_path=[source_node_id],
            )
            db.add(message)
            await db.commit()

            logger.info(
                f"Mesh message created: {message.id} from node {source_node_id}"
            )
            return {
                "id": message.id,
                "source_node_id": message.source_node_id,
                "destination_node_id": message.destination_node_id,
                "message_type": message.message_type,
                "message_content": message.message_content,
                "status": message.status,
                "created_at": message.created_at,
            }
        except Exception as e:
            await db.rollback()
            logger.error(f"Error sending mesh message: {e}")
            raise

    @staticmethod
    async def get_network_status(db: AsyncSession) -> dict:
        """
        Get overall mesh network status.
        
        Args:
            db: Database session
            
        Returns:
            Network status data
        """
        try:
            # Count nodes
            query = select(func.count(MeshNode.id)).where(MeshNode.is_active == True)
            active_count_result = await db.execute(query)
            active_count = active_count_result.scalar() or 0

            query = select(func.count(MeshNode.id)).where(MeshNode.is_active == False)
            inactive_count_result = await db.execute(query)
            inactive_count = inactive_count_result.scalar() or 0

            query = select(func.count(MeshNode.id))
            total_count_result = await db.execute(query)
            total_count = total_count_result.scalar() or 0

            # Calculate averages
            query = select(func.avg(MeshNode.battery_level))
            avg_battery_result = await db.execute(query)
            avg_battery = avg_battery_result.scalar()

            query = select(func.avg(MeshNode.signal_strength))
            avg_signal_result = await db.execute(query)
            avg_signal = avg_signal_result.scalar()

            # Sum messages
            query = select(
                func.sum(MeshNode.total_messages),
                func.sum(MeshNode.failed_messages),
            )
            msg_result = await db.execute(query)
            total_msgs, failed_msgs = msg_result.one()
            total_msgs = total_msgs or 0
            failed_msgs = failed_msgs or 0

            # Calculate network health (0-100)
            network_health = 100.0
            if active_count == 0:
                network_health = 0.0
            else:
                # Reduce health if many nodes are inactive
                inactive_ratio = inactive_count / max(total_count, 1)
                network_health -= inactive_ratio * 30

                # Reduce health if battery is low
                if avg_battery and avg_battery < 20:
                    network_health -= 20
                elif avg_battery and avg_battery < 50:
                    network_health -= 10

                # Reduce health if signal is weak
                if avg_signal and avg_signal < -80:
                    network_health -= 15

                network_health = max(0, min(100, network_health))

            return {
                "total_nodes": total_count,
                "active_nodes": active_count,
                "inactive_nodes": inactive_count,
                "average_battery": float(avg_battery) if avg_battery else None,
                "average_signal": float(avg_signal) if avg_signal else None,
                "total_messages": int(total_msgs),
                "failed_messages": int(failed_msgs),
                "network_health": network_health,
            }
        except Exception as e:
            logger.error(f"Error getting network status: {e}")
            raise
