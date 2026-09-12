"""Authentication endpoints"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.schemas.user import (
    UserCreate,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    SuccessResponse,
    ErrorResponse,
    UserResponse,
)
from app.services.auth import AuthService
from app.dependencies import get_db
from app.dependencies.auth import get_current_user, get_client_ip
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/register",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Success response with verification token
    """
    try:
        result = await AuthService.register_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role,
            db=db,
        )
        return {
            "success": True,
            "data": result,
            "message": "User registered successfully. Please verify your email.",
        }
    except ValueError as e:
        logger.warning(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration",
        )


@router.post(
    "/verify-email",
    response_model=SuccessResponse,
    responses={400: {"model": ErrorResponse}},
)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify user email with token.
    
    Args:
        token: Verification token
        db: Database session
        
    Returns:
        Success response
    """
    try:
        result = await AuthService.verify_email(token, db)
        return {
            "success": True,
            "message": result["message"],
        }
    except ValueError as e:
        logger.warning(f"Email verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error during email verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during email verification",
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}},
)
async def login(
    login_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return JWT tokens.
    
    Args:
        login_data: User login credentials
        request: HTTP request (for IP extraction)
        db: Database session
        
    Returns:
        Token response with access and refresh tokens
    """
    try:
        ip_address = get_client_ip(request)
        result = await AuthService.login(
            email=login_data.email,
            password=login_data.password,
            ip_address=ip_address,
            db=db,
        )
        return {
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "token_type": result["token_type"],
            "expires_in": result["expires_in"],
            "user": result["user"],
        }
    except ValueError as e:
        logger.warning(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login",
        )


@router.post(
    "/refresh",
    response_model=SuccessResponse,
    responses={401: {"model": ErrorResponse}},
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_data: Refresh token data
        db: Database session
        
    Returns:
        New access token
    """
    try:
        result = await AuthService.refresh_access_token(
            refresh_token=refresh_data.refresh_token,
            db=db,
        )
        return {
            "success": True,
            "data": result,
        }
    except ValueError as e:
        logger.warning(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during token refresh",
        )


@router.post(
    "/logout",
    response_model=SuccessResponse,
)
async def logout(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Logout user by revoking refresh token.
    
    Args:
        refresh_data: Refresh token data
        db: Database session
        
    Returns:
        Success response
    """
    try:
        result = await AuthService.logout(
            refresh_token=refresh_data.refresh_token,
            db=db,
        )
        return {
            "success": True,
            "message": result["message"],
        }
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during logout",
        )


@router.get(
    "/me",
    response_model=UserResponse,
    responses={401: {"model": ErrorResponse}},
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User profile
    """
    return current_user
