"""Volunteer credential endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.dependencies.auth import get_current_user, require_role
from app.models.credentials import CredentialRequest
from app.models.user import User, UserRole
from app.schemas.credentials import CredentialRequestCreate, CredentialRequestResponse, CredentialVerificationRequest, CredentialVerificationResponse, VerifiableCredentialResponse
from app.services.credentials import CredentialService

router = APIRouter()


@router.post("/request", response_model=CredentialRequestResponse, status_code=status.HTTP_201_CREATED)
async def request_credential(payload: CredentialRequestCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> CredentialRequest:
    """Submit KYC documents for volunteer credential review."""
    try:
        return await CredentialService.request_credential(current_user.id, payload.model_dump(), db)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/status", response_model=CredentialRequestResponse)
async def credential_status(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> CredentialRequest:
    """Check the current user's KYC status."""
    request = await CredentialService.get_status(current_user.id, db)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No credential request found")
    return request


@router.post("/issue/{request_id}", response_model=VerifiableCredentialResponse)
async def issue_credential(request_id: int, current_user: User = Depends(require_role(UserRole.ADMIN)), db: AsyncSession = Depends(get_db)) -> object:
    """Approve a pending KYC request; admin-only."""
    try:
        return await CredentialService.issue_credential(request_id, current_user.id, db)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/verify", response_model=CredentialVerificationResponse)
async def verify_credential(payload: CredentialVerificationRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict:
    """Verify a presented credential and return a precise failure reason."""
    return await CredentialService.verify_credential(payload.model_dump(), db)
