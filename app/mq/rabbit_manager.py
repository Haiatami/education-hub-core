# education-hub-core/app/mq/rabbit_manager.py
import asyncio
import aio_pika
from app.util.logger import logger


class RabbitMQManager:
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.connection = None
        self.channel = None

    async def connect(self):
        """
        Establish connection and channel
        """
        logger.info("Connecting to RabbitMQ...")
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()
        logger.success("RabbitMQ connected successfully.")

    async def start_consuming(self, queue_name: str, callback):
        """
        Start listening to a specific queue
        """
        queue = await self.channel.declare_queue(queue_name, durable=True)
        await queue.consume(callback)
        logger.info(f"Started consuming from queue: {queue_name}")

    async def close(self):
        """
        Gracefully close connection
        """
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed.")
