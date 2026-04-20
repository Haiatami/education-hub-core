# education-hub-core/app/core/application.py
import asyncio
import json
import signal
import sys
import time
from typing import Any

import aio_pika

from app.config.config import settings
from app.util.logger import logger
from app.database.connection import init_postgres

from app.mq.rabbit_manager import RabbitMQManager


class Application:
    def __init__(self):
        self.should_exit = False
        self.mq = RabbitMQManager(settings.rabbitmq.rabbitmq_uri)
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)

    def handle_exit(self, sig: int, _: Any) -> None:
        signame = signal.Signals(sig).name
        logger.info(f"Received signal {signame}. Starting graceful shutdown...")
        self.should_exit = True

    async def process_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            try:
                payload = json.loads(message.body.decode())
                task_type = payload.get("task")
                data = payload.get("data")

                logger.info(f"Dispatching task: {task_type}")

                if task_type == "process_vector":
                    logger.success(f"Successfully processed vector for: {data}")

                elif task_type == "other_task":
                    pass

            except json.JSONDecodeError:
                logger.error("Failed to decode JSON message")
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    async def setup(self):
        logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
        logger.info(f"Environment: {settings.ENV}")
        try:
            await asyncio.to_thread(init_postgres)
            try:
                await self.mq.connect()
                await self.mq.start_consuming(
                    settings.rabbitmq.RABBITMQ_DEFAULT_QUEUE, self.process_message
                )
            except Exception as e:
                logger.error(f"MQ Setup failed: {e}")
                raise e
            logger.success("Application setup complete.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise e

    async def shutdown(self):
        logger.info("Cleaning up resources...")
        await self.mq.close()
        logger.success("Shutdown complete. Goodbye!")

    async def run(self):
        await self.setup()

        try:
            logger.info("Core service is running. Press Ctrl+C to stop.")
            while not self.should_exit:
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            raise e
        finally:
            await self.shutdown()
