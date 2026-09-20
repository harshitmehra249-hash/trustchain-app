"""Celery app configuration for background workers."""

from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "trustchain",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    timezone="UTC",
    enable_utc=True,
)
