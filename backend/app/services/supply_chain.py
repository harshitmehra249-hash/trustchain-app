"""Supply chain service for blockchain integration"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
import logging
import json
import qrcode
from io import BytesIO
import base64
from hashlib import sha256

from app.models.supply_chain import (
    SupplyChainItem,
    SupplyChainTransfer,
    BlockchainVerification,
    IPFSMetadata,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class SupplyChainService:
    """Supply chain and blockchain service"""

    @staticmethod
    async def create_item(
        item_code: str,
        item_name: str,
        category: str,
        quantity: int,
        unit: str,
        description: Optional[str],
        donor_name: Optional[str],
        donor_contact: Optional[str],
        manufacturing_date: Optional[datetime],
        expiry_date: Optional[datetime],
        batch_number: Optional[str],
        db: AsyncSession,
    ) -> dict:
        """
        Create a new supply chain item.
        
        Args:
            item_code: Unique item code
            item_name: Item name
            category: Item category
            quantity: Item quantity
            unit: Unit of measurement
            description: Item description
            donor_name: Donor name
            donor_contact: Donor contact
            manufacturing_date: Manufacturing date
            expiry_date: Expiry date
            batch_number: Batch number
            db: Database session
            
        Returns:
            Created item data
            
        Raises:
            ValueError: If item_code already exists
        """
        try:
            # Check if item_code exists
            query = select(SupplyChainItem).where(
                SupplyChainItem.item_code == item_code
            )
            existing_item = await db.execute(query)
            if existing_item.scalar_one_or_none():
                raise ValueError(f"Item with code '{item_code}' already exists")

            # Create item
            item = SupplyChainItem(
                item_code=item_code,
                item_name=item_name,
                description=description,
                category=category,
                quantity=quantity,
                unit=unit,
                donor_name=donor_name,
                donor_contact=donor_contact,
                manufacturing_date=manufacturing_date,
                expiry_date=expiry_date,
                batch_number=batch_number,
                status="registered",
            )
            db.add(item)
            await db.commit()

            logger.info(f"Supply chain item created: {item_code}")
            return {
                "id": item.id,
                "item_code": item.item_code,
                "item_name": item.item_name,
                "category": item.category,
                "quantity": item.quantity,
                "unit": item.unit,
                "status": item.status,
                "created_at": item.created_at,
            }
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating supply chain item: {e}")
            raise

    @staticmethod
    async def get_item(
        item_id: int,
        db: AsyncSession,
    ) -> Optional[dict]:
        """
        Get supply chain item details.
        
        Args:
            item_id: Item ID
            db: Database session
            
        Returns:
            Item data
        """
        try:
            item = await db.get(SupplyChainItem, item_id)
            if not item:
                return None

            return {
                "id": item.id,
                "item_code": item.item_code,
                "item_name": item.item_name,
                "description": item.description,
                "category": item.category,
                "quantity": item.quantity,
                "unit": item.unit,
                "donor_name": item.donor_name,
                "donor_contact": item.donor_contact,
                "manufacturing_date": item.manufacturing_date,
                "expiry_date": item.expiry_date,
                "batch_number": item.batch_number,
                "status": item.status,
                "is_verified": item.is_verified,
                "contract_address": item.contract_address,
                "token_id": item.token_id,
                "blockchain_tx_hash": item.blockchain_tx_hash,
                "qr_code_generated": item.qr_code_generated,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
        except Exception as e:
            logger.error(f"Error getting item: {e}")
            raise

    @staticmethod
    async def transfer_item(
        item_id: int,
        from_location: str,
        to_location: str,
        from_party: str,
        to_party: str,
        from_party_type: str,
        to_party_type: str,
        from_latitude: Optional[float],
        from_longitude: Optional[float],
        to_latitude: Optional[float],
        to_longitude: Optional[float],
        condition_notes: Optional[str],
        verification_method: Optional[str],
        db: AsyncSession,
    ) -> dict:
        """
        Transfer item in supply chain.
        
        Args:
            item_id: Item ID
            from_location: Source location
            to_location: Destination location
            from_party: Transferring party name
            to_party: Receiving party name
            from_party_type: Transferring party type
            to_party_type: Receiving party type
            from_latitude: Source latitude
            from_longitude: Source longitude
            to_latitude: Destination latitude
            to_longitude: Destination longitude
            condition_notes: Condition notes
            verification_method: Verification method
            db: Database session
            
        Returns:
            Transfer data
            
        Raises:
            ValueError: If item not found
        """
        try:
            item = await db.get(SupplyChainItem, item_id)
            if not item:
                raise ValueError(f"Item with id {item_id} not found")

            # Create transfer
            transfer = SupplyChainTransfer(
                item_id=item_id,
                from_location=from_location,
                to_location=to_location,
                from_party=from_party,
                to_party=to_party,
                from_party_type=from_party_type,
                to_party_type=to_party_type,
                from_latitude=from_latitude,
                from_longitude=from_longitude,
                to_latitude=to_latitude,
                to_longitude=to_longitude,
                condition_notes=condition_notes,
                verification_method=verification_method,
            )
            db.add(transfer)

            # Update item status
            item.status = "in_transit"
            item.updated_at = datetime.now(timezone.utc)

            await db.commit()

            logger.info(f"Item {item_id} transferred from {from_party} to {to_party}")
            return {
                "id": transfer.id,
                "item_id": transfer.item_id,
                "from_location": transfer.from_location,
                "to_location": transfer.to_location,
                "from_party": transfer.from_party,
                "to_party": transfer.to_party,
                "transferred_at": transfer.transferred_at,
            }
        except Exception as e:
            await db.rollback()
            logger.error(f"Error transferring item: {e}")
            raise

    @staticmethod
    async def get_item_history(
        item_id: int,
        db: AsyncSession,
    ) -> Optional[dict]:
        """
        Get complete supply chain history for an item.
        
        Args:
            item_id: Item ID
            db: Database session
            
        Returns:
            Item history data
        """
        try:
            item = await db.get(SupplyChainItem, item_id)
            if not item:
                return None

            # Get transfers
            query = select(SupplyChainTransfer).where(
                SupplyChainTransfer.item_id == item_id
            ).order_by(SupplyChainTransfer.transferred_at)
            transfers_result = await db.execute(query)
            transfers = transfers_result.scalars().all()

            # Get verifications
            query = select(BlockchainVerification).where(
                BlockchainVerification.item_id == item_id
            ).order_by(BlockchainVerification.verified_at)
            verifications_result = await db.execute(query)
            verifications = verifications_result.scalars().all()

            # Get IPFS metadata
            query = select(IPFSMetadata).where(
                IPFSMetadata.item_id == item_id
            )
            ipfs_result = await db.execute(query)
            ipfs_metadata = ipfs_result.scalar_one_or_none()

            # Build timeline
            timeline = []
            timeline.append({
                "event": "registered",
                "timestamp": item.created_at,
                "details": f"Item {item.item_code} registered",
            })

            for transfer in transfers:
                timeline.append({
                    "event": "transfer",
                    "timestamp": transfer.transferred_at,
                    "details": f"Transferred from {transfer.from_party} to {transfer.to_party}",
                    "location": transfer.to_location,
                })

            for verification in verifications:
                timeline.append({
                    "event": "blockchain_verification",
                    "timestamp": verification.verified_at,
                    "details": f"Verified on blockchain ({verification.verification_type})",
                    "tx_hash": verification.transaction_hash,
                })

            # Sort timeline
            timeline.sort(key=lambda x: x["timestamp"])

            return {
                "item": await SupplyChainService.get_item(item_id, db),
                "transfers": [
                    {
                        "id": t.id,
                        "from_party": t.from_party,
                        "to_party": t.to_party,
                        "from_location": t.from_location,
                        "to_location": t.to_location,
                        "transferred_at": t.transferred_at,
                        "verified_at": t.verified_at,
                    }
                    for t in transfers
                ],
                "verifications": [
                    {
                        "id": v.id,
                        "transaction_hash": v.transaction_hash,
                        "verification_type": v.verification_type,
                        "is_confirmed": v.is_confirmed,
                        "verified_at": v.verified_at,
                    }
                    for v in verifications
                ],
                "current_location": transfers[-1].to_location if transfers else None,
                "current_holder": transfers[-1].to_party if transfers else item.donor_name,
                "timeline": timeline,
            }
        except Exception as e:
            logger.error(f"Error getting item history: {e}")
            raise

    @staticmethod
    def generate_qr_code(
        item_id: int,
        item_code: str,
        include_metadata: bool = False,
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Generate QR code for supply chain item.
        
        Args:
            item_id: Item ID
            item_code: Item code
            include_metadata: Whether to include metadata in QR
            metadata: Optional metadata to include
            
        Returns:
            Base64 encoded QR code image
        """
        try:
            # Create QR data
            qr_data = {
                "item_id": item_id,
                "item_code": item_code,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if include_metadata and metadata:
                qr_data["metadata"] = metadata

            qr_content = json.dumps(qr_data)

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)

            # Create image
            img = qr.make_image(fill_color="black", back_color="white")

            # Convert to base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()

            logger.info(f"QR code generated for item {item_code}")
            return img_base64
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            raise

    @staticmethod
    async def get_dashboard_stats(db: AsyncSession) -> dict:
        """
        Get supply chain dashboard statistics.
        
        Args:
            db: Database session
            
        Returns:
            Dashboard statistics
        """
        try:
            # Total items
            query = select(func.count(SupplyChainItem.id))
            total_result = await db.execute(query)
            total_items = total_result.scalar() or 0

            # Items by status
            query = select(
                SupplyChainItem.status,
                func.count(SupplyChainItem.id),
            ).group_by(SupplyChainItem.status)
            status_result = await db.execute(query)
            status_data = dict(status_result.all())

            # Items by category
            query = select(
                SupplyChainItem.category,
                func.count(SupplyChainItem.id),
            ).group_by(SupplyChainItem.category)
            category_result = await db.execute(query)
            category_data = dict(category_result.all())

            # Total quantity
            query = select(func.sum(SupplyChainItem.quantity))
            qty_result = await db.execute(query)
            total_quantity = qty_result.scalar() or 0

            # Verified items
            query = select(func.count(SupplyChainItem.id)).where(
                SupplyChainItem.is_verified == True
            )
            verified_result = await db.execute(query)
            verified_items = verified_result.scalar() or 0

            # Blockchain transactions
            query = select(func.count(BlockchainVerification.id))
            tx_result = await db.execute(query)
            blockchain_tx = tx_result.scalar() or 0

            # IPFS entries
            query = select(func.count(IPFSMetadata.id))
            ipfs_result = await db.execute(query)
            ipfs_count = ipfs_result.scalar() or 0

            return {
                "total_items": total_items,
                "items_registered": status_data.get("registered", 0),
                "items_in_transit": status_data.get("in_transit", 0),
                "items_delivered": status_data.get("delivered", 0),
                "items_received": status_data.get("received", 0),
                "verified_items": verified_items,
                "total_quantity": int(total_quantity),
                "by_category": category_data,
                "by_status": status_data,
                "blockchain_transactions": blockchain_tx,
                "ipfs_entries": ipfs_count,
            }
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            raise
