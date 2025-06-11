from celery import Celery

from config import settings

celery_app = Celery(
    "app",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
    include=[""]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry=True,
    broker_connection_max_retries=5,
    broker_connection_retry_delay=5,
)
