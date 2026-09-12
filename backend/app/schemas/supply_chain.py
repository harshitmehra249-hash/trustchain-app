"""Pydantic schemas for supply chain"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class SupplyChainItemCreate(BaseModel):
    """Create supply chain item schema"""
    item_code: str = Field(..., min_length=3, max_length=255)
    item_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: str = Field(..., max_length=100)
    quantity: int = Field(..., gt=0)
    unit: str = Field(..., max_length=50)
    donor_name: Optional[str] = None
    donor_contact: Optional[str] = None
    manufacturing_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    batch_number: Optional[str] = None

    @validator('category')
    def validate_category(cls, v: str) -> str:
        """Validate item category"""
        valid_categories = ['food', 'medicine', 'water', 'blankets', 'clothing', 'tools', 'fuel', 'other']
        if v not in valid_categories:
            raise ValueError(f'Category must be one of {valid_categories}')
        return v

    @validator('expiry_date')
    def validate_expiry_date(cls, v: Optional[datetime], values: dict) -> Optional[datetime]:
        """Validate expiry date is after manufacturing date"""
        if v and 'manufacturing_date' in values:
            manufacturing = values.get('manufacturing_date')
            if manufacturing and v <= manufacturing:
                raise ValueError('Expiry date must be after manufacturing date')
        return v


class SupplyChainItemUpdate(BaseModel):
    """Update supply chain item schema"""
    item_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    status: Optional[str] = None
    is_verified: Optional[bool] = None

    @validator('quantity')
    def validate_quantity(cls, v: Optional[int]) -> Optional[int]:
        """Validate quantity"""
        if v is not None and v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v


class SupplyChainItemResponse(SupplyChainItemCreate):
    """Supply chain item response schema"""
    id: int
    item_code: str
    status: str
    is_verified: bool
    qr_code_generated: bool
    contract_address: Optional[str]
    token_id: Optional[str]
    blockchain_tx_hash: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SupplyChainTransferCreate(BaseModel):
    """Create supply chain transfer schema"""
    item_id: int
    from_location: str = Field(..., min_length=1, max_length=255)
    to_location: str = Field(..., min_length=1, max_length=255)
    from_latitude: Optional[float] = Field(None, ge=-90, le=90)
    from_longitude: Optional[float] = Field(None, ge=-180, le=180)
    to_latitude: Optional[float] = Field(None, ge=-90, le=90)
    to_longitude: Optional[float] = Field(None, ge=-180, le=180)
    from_party: str = Field(..., max_length=255)
    to_party: str = Field(..., max_length=255)
    from_party_type: str = Field(..., max_length=50)
    to_party_type: str = Field(..., max_length=50)
    condition_notes: Optional[str] = None
    verification_method: Optional[str] = None

    @validator('from_party_type', 'to_party_type')
    def validate_party_type(cls, v: str) -> str:
        """Validate party type"""
        valid_types = ['donor', 'warehouse', 'volunteer', 'beneficiary', 'government', 'ngo']
        if v not in valid_types:
            raise ValueError(f'Party type must be one of {valid_types}')
        return v


class SupplyChainTransferResponse(SupplyChainTransferCreate):
    """Supply chain transfer response schema"""
    id: int
    verified_by: Optional[str]
    blockchain_tx_hash: Optional[str]
    photos: Optional[List[str]]
    transferred_at: datetime
    verified_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class BlockchainVerificationResponse(BaseModel):
    """Blockchain verification response schema"""
    id: int
    item_id: int
    transaction_hash: str
    block_number: Optional[int]
    contract_address: str
    verification_type: str
    is_confirmed: bool
    confirmation_count: int
    verified_at: datetime
    confirmed_at: Optional[datetime]

    class Config:
        from_attributes = True


class IPFSMetadataResponse(BaseModel):
    """IPFS metadata response schema"""
    id: int
    item_id: int
    ipfs_hash: str
    metadata_type: str
    content_hash: str
    is_pinned: bool
    file_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SupplyChainItemHistoryResponse(BaseModel):
    """Complete supply chain item history"""
    item: SupplyChainItemResponse
    transfers: List[SupplyChainTransferResponse]
    verifications: List[BlockchainVerificationResponse]
    ipfs_metadata: Optional[IPFSMetadataResponse]
    current_location: Optional[str]
    current_holder: Optional[str]
    timeline: List[dict]  # Chronological timeline of all events


class QRCodeGenerateRequest(BaseModel):
    """QR code generation request"""
    item_id: int
    include_metadata: bool = False


class QRCodeVerifyRequest(BaseModel):
    """QR code verification request"""
    qr_code_data: str
    verifier_name: str


class SupplyChainDashboardStats(BaseModel):
    """Supply chain dashboard statistics"""
    total_items: int
    items_registered: int
    items_in_transit: int
    items_delivered: int
    verified_items: int
    total_quantity: int
    by_category: dict  # Category-wise breakdown
    by_status: dict  # Status-wise breakdown
    blockchain_transactions: int
    ipfs_entries: int
