from celery import Celery

from src.config import settings

celery_app = Celery(
    "app",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
    include=["src.tasks", "src.tasks.scan_files", "src.tasks.streaming_to_minio"],
    auto_import_tasks=True,
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
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default"
)

celery_app.conf.beat_schedule = {
    "scan-files-every-1-minute": {
        "task": "src.tasks.scan_files.celery_scan_files",
        "schedule": 60.0,
    },
    "stream-files-every-1-minute": {
        "task": "src.tasks.streaming_to_minio.celery_streaming_files",
        "schedule": 60.0,
    }
}

# Команда вызова celery на Windows: python -m celery -A src.celery_worker.celery_app worker --loglevel=info --pool=solo
# команда для запуска beat: python -m celery -A src.celery_worker.celery_app beat --loglevel=info
