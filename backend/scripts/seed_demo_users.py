#!/usr/bin/env python3
"""
Seed Demo Users for PharmaShield-AI
Creates the four demo accounts for local development and demos.

Usage:
  python scripts/seed_demo_users.py
  # or via Makefile:
  make seed-users
"""
import asyncio
import sys
import os

# Allow running from backend/ or project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import get_settings
from app.core.security import get_password_hash
from app.models.domain import (
    User, Case, UserDocument, DocumentChunk,
    ExtractedMedicine, ExtractedLabValue, AgentRun, Feedback,
    Citation, PrescriptionExtraction, SellerRiskAssessment,
    BatchVerification, PriceComplianceCheck, SubstitutionCheck,
    ADRReport, PharmacistReview, DoctorReview,
    DoctorPharmacistMessage, VerifiedPrescription, DataSourceSyncStatus,
)
from app.services.memory.memory_store import MemoryEntry

DEMO_USERS = [
    {"name": "Demo Patient",      "email": "patient@demo.com",     "password": "demo123", "role": "PATIENT"},
    {"name": "Demo Pharmacist",   "email": "pharmacist@demo.com",  "password": "demo123", "role": "PHARMACIST"},
    {"name": "Demo Doctor",       "email": "doctor@demo.com",      "password": "demo123", "role": "DOCTOR"},
    {"name": "Demo Admin",        "email": "admin@demo.com",       "password": "demo123", "role": "ADMIN"},
]

async def seed():
    settings = get_settings()
    if not settings.mongo_uri:
        print("❌  MONGO_URI is not set. Please configure .env before seeding.")
        sys.exit(1)

    client = AsyncIOMotorClient(settings.mongo_uri)
    db_path = settings.mongo_uri.split("/")
    db_name = db_path[-1].split("?")[0] if db_path else "pharmashield_db"

    await init_beanie(
        database=client[db_name],
        document_models=[
            User, Case, UserDocument, DocumentChunk, ExtractedMedicine,
            ExtractedLabValue, AgentRun, Feedback, Citation, MemoryEntry,
            PrescriptionExtraction, SellerRiskAssessment, BatchVerification,
            PriceComplianceCheck, SubstitutionCheck, ADRReport, PharmacistReview,
            DoctorReview, DoctorPharmacistMessage, VerifiedPrescription, DataSourceSyncStatus,
        ],
    )

    created = 0
    skipped = 0
    for u in DEMO_USERS:
        existing = await User.find_one({"email": u["email"]})
        if existing:
            print(f"  ⏭  {u['email']} already exists — skipping")
            skipped += 1
            continue

        user = User(
            name=u["name"],
            email=u["email"],
            role=u["role"],
            hashed_password=get_password_hash(u["password"]),
        )
        await user.insert()
        print(f"  ✅  Created {u['role']}: {u['email']}")
        created += 1

    print(f"\n🌱  Seeding complete — {created} created, {skipped} skipped")
    print("\n  Demo credentials (all use password: demo123)")
    print("  patient@demo.com / pharmacist@demo.com / doctor@demo.com / admin@demo.com")

if __name__ == "__main__":
    asyncio.run(seed())
