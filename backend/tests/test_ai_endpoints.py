import importlib

import pytest

from app.models.user import User
from app.schemas.ai import RouteOptimizationRequest


def test_ai_endpoint_module_imports() -> None:
    module = importlib.import_module("app.api.v1.endpoints.ai")
    assert module is not None


@pytest.mark.asyncio
async def test_route_optimization_returns_fallback_route() -> None:
    ai_module = importlib.import_module("app.api.v1.endpoints.ai")
    payload = RouteOptimizationRequest(
        start_latitude=28.6139,
        start_longitude=77.2090,
        end_latitude=28.7041,
        end_longitude=77.1025,
    )

    response = await ai_module.route_optimization(payload=payload, current_user=User())

    assert response.fallback is True
    assert response.provider == "offline-fallback"
    assert len(response.route) == 2
