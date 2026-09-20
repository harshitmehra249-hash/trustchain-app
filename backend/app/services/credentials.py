"""Credential issuance and verification service."""

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import secrets
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.credentials import CredentialRequest, VerifiableCredential


class CredentialService:
    """Manage KYC requests and signed volunteer credentials."""

    @staticmethod
    async def request_credential(user_id: int, payload: dict[str, Any], db: AsyncSession) -> CredentialRequest:
        """Create one KYC request per user and prevent duplicate submissions."""
        existing = await db.execute(select(CredentialRequest).where(CredentialRequest.user_id == user_id))
        if existing.scalar_one_or_none() is not None:
            raise ValueError("A KYC request already exists for this volunteer")

        request = CredentialRequest(user_id=user_id, **payload)
        db.add(request)
        await db.commit()
        await db.refresh(request)
        return request

    @staticmethod
    async def get_status(user_id: int, db: AsyncSession) -> CredentialRequest | None:
        """Return the current KYC request for a user."""
        result = await db.execute(select(CredentialRequest).where(CredentialRequest.user_id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def issue_credential(request_id: int, reviewer_id: int, db: AsyncSession) -> VerifiableCredential:
        """Approve a KYC request and issue a tamper-evident credential."""
        request = await db.get(CredentialRequest, request_id)
        if request is None:
            raise ValueError("Credential request not found")
        if request.status == "approved":
            raise ValueError("Credential request has already been approved")
        if request.status != "pending":
            raise ValueError("Only pending credential requests can be approved")

        now = datetime.now(timezone.utc)
        volunteer_id = request.volunteer_id or f"TCV-{secrets.token_hex(6).upper()}"
        expires_at = now + timedelta(days=365)
        credential_id = f"urn:trustchain:credential:{secrets.token_urlsafe(18)}"
        claims = {
            "volunteerId": volunteer_id,
            "role": "volunteer",
            "documentType": request.document_type,
            "documentHash": request.document_hash,
        }
        proof_payload = {
            "type": "TrustChainIntegrityProof",
            "created": now.isoformat(),
            "verificationMethod": "trustchain:issuer",
        }
        digest = sha256(json.dumps({"credential_id": credential_id, "claims": claims}, sort_keys=True).encode()).hexdigest()
        proof = {**proof_payload, "proofPurpose": "assertionMethod", "proofValue": digest}
        credential = VerifiableCredential(
            credential_request_id=request.id,
            user_id=request.user_id,
            credential_id=credential_id,
            issuer="did:web:trustchain.app",
            subject=f"did:trustchain:user:{request.user_id}",
            claims=claims,
            proof=proof,
            issued_at=now,
            expires_at=expires_at,
        )
        request.volunteer_id = volunteer_id
        request.status = "approved"
        request.reviewed_by = reviewer_id
        request.reviewed_at = now
        db.add(credential)
        await db.commit()
        await db.refresh(credential)
        return credential

    @staticmethod
    async def verify_credential(payload: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """Verify existence, expiry, revocation, and integrity digest."""
        credential_data = payload.get("credential", {})
        credential_id = credential_data.get("credentialId") or credential_data.get("id")
        if not credential_id:
            return {"valid": False, "reason": "missing_credential_id"}

        result = await db.execute(select(VerifiableCredential).where(VerifiableCredential.credential_id == credential_id))
        stored = result.scalar_one_or_none()
        if stored is None:
            return {"valid": False, "reason": "unknown_credential", "credential_id": credential_id}
        if stored.revoked:
            return {"valid": False, "reason": "revoked", "credential_id": credential_id}
        now = datetime.now(timezone.utc)
        if stored.expires_at <= now:
            return {"valid": False, "reason": "expired", "credential_id": credential_id, "expires_at": stored.expires_at}

        expected = sha256(json.dumps({"credential_id": stored.credential_id, "claims": stored.claims}, sort_keys=True).encode()).hexdigest()
        presented_proof = payload.get("proof", {}).get("proofValue")
        if presented_proof != expected:
            return {"valid": False, "reason": "invalid_signature", "credential_id": credential_id}
        return {
            "valid": True,
            "credential_id": stored.credential_id,
            "subject": stored.subject,
            "expires_at": stored.expires_at,
        }
