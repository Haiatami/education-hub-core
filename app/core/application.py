# education-hub-core/app/core/application.py
import asyncio
import signal
import sys
import time
from typing import Any

from app.config.config import settings
from app.util.logger import logger
from app.database.connection import init_postgres


class Application:
    def __init__(self):
        self.should_exit = False
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)

    def handle_exit(self, sig: int, _: Any) -> None:
        signame = signal.Signals(sig).name
        logger.info(f"Received signal {signame}. Starting graceful shutdown...")
        self.should_exit = True

    async def setup(self):
        logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
        logger.info(f"Environment: {settings.ENV}")
        try:
            await asyncio.to_thread(init_postgres)
            logger.success("Application setup complete.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise e

    async def shutdown(self):
        logger.info("Cleaning up resources...")
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
