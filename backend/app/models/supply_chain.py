"""Blockchain supply chain models and database schema"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text
from app.db.base import Base


class SupplyChainItem(Base):
    """Supply chain item model"""
    __tablename__ = "supply_chain_items"

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String(255), unique=True, index=True, nullable=False)
    item_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)  # 'food', 'medicine', 'water', 'blankets', etc.
    quantity = Column(Integer, nullable=False)
    unit = Column(String(50), nullable=False)  # 'kg', 'liter', 'box', 'piece', etc.
    
    # Blockchain
    contract_address = Column(String(255), nullable=True)  # Smart contract address
    token_id = Column(String(255), nullable=True)  # NFT token ID
    blockchain_tx_hash = Column(String(255), nullable=True, index=True)  # Transaction hash
    
    # Metadata
    donor_name = Column(String(255), nullable=True)
    donor_contact = Column(String(255), nullable=True)
    manufacturing_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    batch_number = Column(String(100), nullable=True)
    
    # QR Code
    qr_code_data = Column(Text, nullable=True)  # QR code content
    qr_code_generated = Column(Boolean, default=False, nullable=False)
    
    # Status
    status = Column(String(50), default="registered", nullable=False)  # registered, in_transit, delivered, received
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<SupplyChainItem(id={self.id}, item_code={self.item_code}, status={self.status})>"


class SupplyChainTransfer(Base):
    """Track item transfers through the supply chain"""
    __tablename__ = "supply_chain_transfers"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("supply_chain_items.id"), nullable=False, index=True)
    
    # Transfer details
    from_location = Column(String(255), nullable=False)
    to_location = Column(String(255), nullable=False)
    from_latitude = Column(Float, nullable=True)
    from_longitude = Column(Float, nullable=True)
    to_latitude = Column(Float, nullable=True)
    to_longitude = Column(Float, nullable=True)
    
    # Parties involved
    from_party = Column(String(255), nullable=False)  # Name of transferring party
    to_party = Column(String(255), nullable=False)  # Name of receiving party
    from_party_type = Column(String(50), nullable=False)  # 'donor', 'warehouse', 'volunteer', 'beneficiary'
    to_party_type = Column(String(50), nullable=False)
    
    # Verification
    verified_by = Column(String(255), nullable=True)
    verification_method = Column(String(100), nullable=True)  # 'qr_scan', 'manual', 'signature'
    blockchain_tx_hash = Column(String(255), nullable=True, index=True)
    
    # Condition at transfer
    condition_notes = Column(Text, nullable=True)
    photos = Column(JSON, nullable=True)  # List of photo URLs
    
    # Timestamps
    transferred_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<SupplyChainTransfer(id={self.id}, item_id={self.item_id}, from_party={self.from_party})>"


class BlockchainVerification(Base):
    """Store blockchain verification records"""
    __tablename__ = "blockchain_verifications"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("supply_chain_items.id"), nullable=False, index=True)
    
    # Blockchain details
    transaction_hash = Column(String(255), unique=True, index=True, nullable=False)
    block_number = Column(Integer, nullable=True)
    contract_address = Column(String(255), nullable=False)
    token_id = Column(String(255), nullable=True)
    
    # Verification data
    verification_type = Column(String(100), nullable=False)  # 'registration', 'transfer', 'delivery'
    verified_data = Column(JSON, nullable=False)  # Actual data verified on blockchain
    
    # Status
    is_confirmed = Column(Boolean, default=False, nullable=False)
    confirmation_count = Column(Integer, default=0, nullable=False)  # Number of block confirmations
    
    # Timestamps
    verified_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    confirmed_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<BlockchainVerification(id={self.id}, transaction_hash={self.transaction_hash[:10]}...)>"


class IPFSMetadata(Base):
    """Store IPFS metadata for supply chain items"""
    __tablename__ = "ipfs_metadata"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("supply_chain_items.id"), nullable=False, unique=True, index=True)
    
    # IPFS details
    ipfs_hash = Column(String(255), unique=True, index=True, nullable=False)
    metadata_type = Column(String(100), nullable=False)  # 'item_info', 'images', 'documents'
    content_hash = Column(String(255), nullable=False)  # Hash of the content
    
    # Metadata content (structured)
    metadata_json = Column(JSON, nullable=False)
    
    # File references
    file_count = Column(Integer, default=0, nullable=False)
    file_sizes = Column(JSON, nullable=True)  # List of file sizes
    
    # Status
    is_pinned = Column(Boolean, default=False, nullable=False)  # If pinned on IPFS for permanence
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<IPFSMetadata(item_id={self.item_id}, ipfs_hash={self.ipfs_hash[:10]}...)>"
