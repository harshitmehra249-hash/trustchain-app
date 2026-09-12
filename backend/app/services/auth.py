"""Authentication service"""

from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging

from app.models.user import User, UserRole, VerificationToken, RefreshToken, LoginAttempt
from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    generate_verification_token,
    hash_token,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service"""

    @staticmethod
    async def register_user(
        email: str,
        username: str,
        password: str,
        full_name: Optional[str],
        role: UserRole,
        db: AsyncSession,
    ) -> dict:
        """
        Register a new user.
        
        Args:
            email: User email
            username: User username
            password: User password
            full_name: User full name
            role: User role
            db: Database session
            
        Returns:
            Dictionary with user data and verification token
            
        Raises:
            ValueError: If email or username already exists
        """
        try:
            # Check if email exists
            query = select(User).where(User.email == email)
            existing_user = await db.execute(query)
            if existing_user.scalar_one_or_none():
                raise ValueError("Email already registered")

            # Check if username exists
            query = select(User).where(User.username == username)
            existing_user = await db.execute(query)
            if existing_user.scalar_one_or_none():
                raise ValueError("Username already taken")

            # Create user
            hashed_password = get_password_hash(password)
            user = User(
                email=email,
                username=username,
                full_name=full_name,
                hashed_password=hashed_password,
                role=role,
                is_active=True,  # Will be activated after email verification
            )
            db.add(user)
            await db.flush()  # Get user ID without committing

            # Create verification token
            verification_token_str = generate_verification_token()
            verification_token = VerificationToken(
                user_id=user.id,
                token=hash_token(verification_token_str),
                token_type="email_verification",
                expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
            )
            db.add(verification_token)
            await db.commit()

            logger.info(f"User registered successfully: {email}")
            return {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "verification_token": verification_token_str,  # Send via email
            }
        except Exception as e:
            await db.rollback()
            logger.error(f"Error registering user: {e}")
            raise

    @staticmethod
    async def verify_email(token: str, db: AsyncSession) -> dict:
        """
        Verify user email.
        
        Args:
            token: Verification token
            db: Database session
            
        Returns:
            Dictionary with success status
            
        Raises:
            ValueError: If token is invalid or expired
        """
        try:
            token_hash = hash_token(token)
            query = select(VerificationToken).where(
                and_(
                    VerificationToken.token == token_hash,
                    VerificationToken.token_type == "email_verification",
                    VerificationToken.is_used == False,
                )
            )
            verification_token = await db.execute(query)
            token_obj = verification_token.scalar_one_or_none()

            if not token_obj:
                raise ValueError("Invalid verification token")

            if token_obj.expires_at < datetime.now(timezone.utc):
                raise ValueError("Verification token expired")

            # Update user
            user = await db.get(User, token_obj.user_id)
            user.is_email_verified = True
            user.is_verified = True

            # Mark token as used
            token_obj.is_used = True

            await db.commit()
            logger.info(f"Email verified for user: {user.email}")
            return {"success": True, "message": "Email verified successfully"}
        except Exception as e:
            await db.rollback()
            logger.error(f"Error verifying email: {e}")
            raise

    @staticmethod
    async def login(
        email: str, password: str, ip_address: str, db: AsyncSession
    ) -> dict:
        """
        Authenticate user and return tokens.
        
        Args:
            email: User email
            password: User password
            ip_address: Client IP address (for rate limiting)
            db: Database session
            
        Returns:
            Dictionary with access_token, refresh_token, and user data
            
        Raises:
            ValueError: If credentials are invalid
        """
        try:
            # Check rate limiting
            query = select(LoginAttempt).where(
                and_(
                    LoginAttempt.email == email,
                    LoginAttempt.ip_address == ip_address,
                    LoginAttempt.created_at
                    > datetime.now(timezone.utc)
                    - timedelta(seconds=settings.LOGIN_RATE_LIMIT_WINDOW),
                )
            )
            attempts = await db.execute(query)
            failed_attempts = len([a for a in attempts.scalars() if not a.success])

            if failed_attempts >= settings.LOGIN_RATE_LIMIT_ATTEMPTS:
                raise ValueError("Too many failed login attempts. Please try later.")

            # Get user
            query = select(User).where(User.email == email)
            user_result = await db.execute(query)
            user = user_result.scalar_one_or_none()

            if not user or not verify_password(password, user.hashed_password):
                # Log failed attempt
                failed_attempt = LoginAttempt(
                    email=email, ip_address=ip_address, success=False
                )
                db.add(failed_attempt)
                await db.commit()
                raise ValueError("Invalid email or password")

            if not user.is_active:
                raise ValueError("User account is inactive")

            # Create tokens
            access_token = create_access_token(data={"sub": str(user.id)})
            refresh_token_str = create_refresh_token(data={"sub": str(user.id)})

            # Store refresh token
            refresh_token_obj = RefreshToken(
                user_id=user.id,
                token=refresh_token_str,
                expires_at=datetime.now(timezone.utc)
                + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            )
            db.add(refresh_token_obj)

            # Update user
            user.last_login = datetime.now(timezone.utc)
            user.failed_login_attempts = 0

            # Log successful attempt
            success_attempt = LoginAttempt(
                email=email, ip_address=ip_address, success=True
            )
            db.add(success_attempt)
            await db.commit()

            logger.info(f"User logged in successfully: {email}")
            return {
                "access_token": access_token,
                "refresh_token": refresh_token_str,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "is_email_verified": user.is_email_verified,
                },
            }
        except Exception as e:
            await db.rollback()
            logger.error(f"Login error: {e}")
            raise

    @staticmethod
    async def refresh_access_token(refresh_token: str, db: AsyncSession) -> dict:
        """
        Generate new access token using refresh token.
        
        Args:
            refresh_token: Refresh token
            db: Database session
            
        Returns:
            New access token
            
        Raises:
            ValueError: If refresh token is invalid
        """
        try:
            # Verify token
            payload = verify_token(refresh_token, "refresh")
            if not payload:
                raise ValueError("Invalid refresh token")

            user_id = int(payload.get("sub"))

            # Check if token exists in database and not revoked
            query = select(RefreshToken).where(
                and_(
                    RefreshToken.token == refresh_token,
                    RefreshToken.user_id == user_id,
                    RefreshToken.is_revoked == False,
                )
            )
            token_result = await db.execute(query)
            token_obj = token_result.scalar_one_or_none()

            if not token_obj or token_obj.expires_at < datetime.now(timezone.utc):
                raise ValueError("Refresh token expired or revoked")

            # Get user
            user = await db.get(User, user_id)
            if not user or not user.is_active:
                raise ValueError("User not found or inactive")

            # Create new access token
            new_access_token = create_access_token(data={"sub": str(user.id)})

            logger.info(f"Access token refreshed for user: {user.email}")
            return {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            }
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise

    @staticmethod
    async def logout(refresh_token: str, db: AsyncSession) -> dict:
        """
        Logout user by revoking refresh token.
        
        Args:
            refresh_token: Refresh token to revoke
            db: Database session
            
        Returns:
            Dictionary with success status
        """
        try:
            query = select(RefreshToken).where(
                RefreshToken.token == refresh_token
            )
            token_result = await db.execute(query)
            token_obj = token_result.scalar_one_or_none()

            if token_obj:
                token_obj.is_revoked = True
                await db.commit()

            logger.info("User logged out successfully")
            return {"success": True, "message": "Logged out successfully"}
        except Exception as e:
            await db.rollback()
            logger.error(f"Logout error: {e}")
            raise
