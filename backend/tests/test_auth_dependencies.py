from fastapi import HTTPException
import pytest

from app.dependencies.auth import require_role
from app.models.user import User, UserRole


@pytest.mark.asyncio
async def test_require_role_allows_authorized_user() -> None:
    checker = require_role(UserRole.ADMIN)
    user = User(role=UserRole.ADMIN)

    result = await checker(current_user=user)

    assert result is user


@pytest.mark.asyncio
async def test_require_role_rejects_unauthorized_user() -> None:
    checker = require_role(UserRole.ADMIN)
    user = User(role=UserRole.VOLUNTEER)

    with pytest.raises(HTTPException) as exc_info:
        await checker(current_user=user)

    assert exc_info.value.status_code == 403
