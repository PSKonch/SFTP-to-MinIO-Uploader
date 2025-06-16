from aio_pika import connect_robust
from src.config import settings

async def get_rabbit_connection():
    return await connect_robust(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        login=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASSWORD
    )

