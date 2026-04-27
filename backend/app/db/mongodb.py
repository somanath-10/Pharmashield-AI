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
    PrescriptionExtraction,
    SellerRiskAssessment,
    BatchVerification,
    PriceComplianceCheck,
    SubstitutionCheck,
    ADRReport,
    PharmacistReview,
    DoctorReview,
    DoctorPharmacistMessage,
    VerifiedPrescription,
    DataSourceSyncStatus,
)
from app.services.memory.memory_store import MemoryEntry

logger = logging.getLogger(__name__)


async def init_db() -> None:
    settings = get_settings()
    logger.info("Connecting to MongoDB for PharmaShield India (Role-Based MVP)...")

    client = AsyncIOMotorClient(settings.mongo_uri)

    # Parse DB name from the URL (path segment before query string)
    db_path = settings.mongo_uri.split("/")
    db_name = db_path[-1].split("?")[0] if db_path else "pharmashield_db"

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
            MemoryEntry,
            PrescriptionExtraction,
            SellerRiskAssessment,
            BatchVerification,
            PriceComplianceCheck,
            SubstitutionCheck,
            ADRReport,
            PharmacistReview,
            DoctorReview,
            DoctorPharmacistMessage,
            VerifiedPrescription,
            DataSourceSyncStatus,
        ],
    )
    logger.info("MongoDB and Beanie ODM initialized successfully.")
