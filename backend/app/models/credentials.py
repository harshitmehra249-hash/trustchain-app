"""Volunteer credential and KYC database models."""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from app.db.base import Base


class CredentialRequest(Base):
    """KYC request submitted by a volunteer."""

    __tablename__ = "credential_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    volunteer_id = Column(String(100), unique=True, index=True, nullable=True)
    document_type = Column(String(50), nullable=False)
    document_hash = Column(String(128), nullable=False)
    document_url = Column(Text, nullable=True)
    status = Column(String(30), nullable=False, default="pending", index=True)
    rejection_reason = Column(String(500), nullable=True)
    reviewed_by = Column(Integer, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class VerifiableCredential(Base):
    """Issued W3C-style credential metadata."""

    __tablename__ = "verifiable_credentials"

    id = Column(Integer, primary_key=True, index=True)
    credential_request_id = Column(Integer, ForeignKey("credential_requests.id"), nullable=False, unique=True)
    user_id = Column(Integer, nullable=False, index=True)
    credential_id = Column(String(255), unique=True, index=True, nullable=False)
    issuer = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    credential_type = Column(String(100), nullable=False, default="TrustChainVolunteerCredential")
    claims = Column(JSON, nullable=False)
    proof = Column(JSON, nullable=False)
    issued_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    revoked_reason = Column(String(500), nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
