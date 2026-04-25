import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.core.config import get_settings
from app.models.domain import (
    User,
    Case,
    UserDocument,
    DocumentChunk,
    ExtractedMedicine,
    ExtractedLabValue,
    AgentRun,
    Feedback,
    Citation,
)

logger = logging.getLogger(__name__)


async def init_db() -> None:
    settings = get_settings()
    logger.info("Connecting to MongoDB for PharmaShield India (Role-Based MVP)...")

    client = AsyncIOMotorClient(settings.database_url)

    # Parse DB name from the URL (path segment before query string)
    db_path = settings.database_url.split("/")
    db_name = db_path[-1].split("?")[0] if db_path else "pharmashield_india"

    await init_beanie(
        database=client[db_name],
        document_models=[
            User,
            Case,
            UserDocument,
            DocumentChunk,
            ExtractedMedicine,
            ExtractedLabValue,
            AgentRun,
            Feedback,
            Citation,
        ],
    )
    logger.info("MongoDB and Beanie ODM initialized successfully.")
