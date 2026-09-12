"""Blockchain supply chain endpoints"""

from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.schemas.supply_chain import (
    SupplyChainItemCreate,
    SupplyChainItemResponse,
    SupplyChainTransferCreate,
    SupplyChainTransferResponse,
    SupplyChainItemHistoryResponse,
    SupplyChainDashboardStats,
    QRCodeGenerateRequest,
)
from app.services.supply_chain import SupplyChainService
from app.dependencies import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/items",
    response_model=SupplyChainItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_supply_item(
    item_data: SupplyChainItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new supply chain item.
    
    Args:
        item_data: Item data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Created item
    """
    try:
        result = await SupplyChainService.create_item(
            item_code=item_data.item_code,
            item_name=item_data.item_name,
            category=item_data.category,
            quantity=item_data.quantity,
            unit=item_data.unit,
            description=item_data.description,
            donor_name=item_data.donor_name,
            donor_contact=item_data.donor_contact,
            manufacturing_date=item_data.manufacturing_date,
            expiry_date=item_data.expiry_date,
            batch_number=item_data.batch_number,
            db=db,
        )
        return result
    except ValueError as e:
        logger.warning(f"Item creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error creating supply item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the item",
        )


@router.get(
    "/items/{item_id}",
    response_model=SupplyChainItemResponse,
)
async def get_supply_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get supply chain item details.
    
    Args:
        item_id: Item ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Item details
    """
    try:
        result = await SupplyChainService.get_item(item_id, db)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found",
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting supply item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the item",
        )


@router.post(
    "/items/{item_id}/transfer",
    response_model=SupplyChainTransferResponse,
    status_code=status.HTTP_201_CREATED,
)
async def transfer_supply_item(
    item_id: int,
    transfer_data: SupplyChainTransferCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Transfer item in supply chain.
    
    Args:
        item_id: Item ID
        transfer_data: Transfer details
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Transfer record
    """
    try:
        result = await SupplyChainService.transfer_item(
            item_id=item_id,
            from_location=transfer_data.from_location,
            to_location=transfer_data.to_location,
            from_party=transfer_data.from_party,
            to_party=transfer_data.to_party,
            from_party_type=transfer_data.from_party_type,
            to_party_type=transfer_data.to_party_type,
            from_latitude=transfer_data.from_latitude,
            from_longitude=transfer_data.from_longitude,
            to_latitude=transfer_data.to_latitude,
            to_longitude=transfer_data.to_longitude,
            condition_notes=transfer_data.condition_notes,
            verification_method=transfer_data.verification_method,
            db=db,
        )
        return result
    except ValueError as e:
        logger.warning(f"Transfer error: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error transferring item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while transferring the item",
        )


@router.get(
    "/items/{item_id}/history",
    response_model=SupplyChainItemHistoryResponse,
)
async def get_item_history(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get complete supply chain history for an item.
    
    Args:
        item_id: Item ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Item history with timeline
    """
    try:
        result = await SupplyChainService.get_item_history(item_id, db)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found",
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting item history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching item history",
        )


@router.post(
    "/items/{item_id}/qr-code",
    response_model=dict,
)
async def generate_qr_code(
    item_id: int,
    request_data: QRCodeGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate QR code for supply chain item.
    
    Args:
        item_id: Item ID
        request_data: QR generation request
        db: Database session
        current_user: Authenticated user
        
    Returns:
        QR code data (base64 encoded)
    """
    try:
        item = await SupplyChainService.get_item(item_id, db)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found",
            )

        qr_code = SupplyChainService.generate_qr_code(
            item_id=item_id,
            item_code=item["item_code"],
            include_metadata=request_data.include_metadata,
            metadata=item if request_data.include_metadata else None,
        )

        return {
            "item_id": item_id,
            "qr_code": qr_code,
            "qr_code_format": "base64_png",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating QR code",
        )


@router.get(
    "/dashboard/stats",
    response_model=SupplyChainDashboardStats,
)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get supply chain dashboard statistics.
    
    Args:
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Dashboard statistics
    """
    try:
        result = await SupplyChainService.get_dashboard_stats(db)
        return result
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching dashboard stats",
        )
