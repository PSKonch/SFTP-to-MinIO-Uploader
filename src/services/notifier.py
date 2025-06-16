import json
from aio_pika import Message
from src.rabbit import get_rabbit_connection

async def notify_about_streaming_file(file_path: str):
    async with get_rabbit_connection() as connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            Message(body=json.dumps({"file_path": file_path}).encode()),
            routing_key="streaming"
        )
        await channel.close()