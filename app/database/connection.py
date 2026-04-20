# education-hub-core/app/database/connection.py
from typing import Generator

from sqlmodel import SQLModel, Session, create_engine, text

from app.config.config import settings
from app.util.logger import logger

connection_string = settings.postgres.postgres_uri

engine = create_engine(
    connection_string,
    echo=False,
    pool_size=settings.postgres.PG_POOL_MIN,
    max_overflow=settings.postgres.PG_POOL_MAX - settings.postgres.PG_POOL_MIN,
    pool_pre_ping=True,
)


def init_postgres():
    """
    Initialize the database by creating all defined SQLModel tables.
    Import your models here to ensure they are registered on SQLModel.metadata.
    """
    try:
        logger.info("Initializing database tables...")
        with engine.connect() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            connection.commit()

        SQLModel.metadata.create_all(engine)
        logger.success("Database initialization successful.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise e


def get_session() -> Generator[Session, None, None]:
    """
    Dependency generator for database sessions.
    Ensures the session is automatically closed after the request is finished.
    """
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()
