"""Schemas for volunteer KYC and verifiable credentials."""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class CredentialRequestCreate(BaseModel):
    """Submit a KYC document for review."""

    document_type: str = Field(..., min_length=2, max_length=50)
    document_hash: str = Field(..., min_length=32, max_length=128)
    document_url: Optional[str] = Field(None, max_length=2000)


class CredentialRequestResponse(BaseModel):
    """KYC request status."""

    id: int
    volunteer_id: Optional[str]
    document_type: str
    status: str
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CredentialVerificationRequest(BaseModel):
    """Credential presentation submitted for verification."""

    credential: dict[str, Any]
    proof: dict[str, Any]


class CredentialVerificationResponse(BaseModel):
    """Verification result with a specific failure reason."""

    valid: bool
    reason: Optional[str] = None
    credential_id: Optional[str] = None
    subject: Optional[str] = None
    expires_at: Optional[datetime] = None


class VerifiableCredentialResponse(BaseModel):
    """Issued credential response."""

    credential_id: str
    issuer: str
    subject: str
    credential_type: str
    claims: dict[str, Any]
    proof: dict[str, Any]
    issued_at: datetime
    expires_at: datetime
    revoked: bool

    class Config:
        from_attributes = True
