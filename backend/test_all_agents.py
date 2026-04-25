from __future__ import annotations

import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.services.agents.coordinator import AgentCoordinator
from app.schemas.case import (
    CaseAnalyzeRequest, 
    PrescriptionContext, 
    ProductContext, 
    PatientContext
)

# DB setup
DATABASE_URL = "postgresql://postgres:422256@localhost:5432/pharmashield_india"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

async def test_scenarios():
    db = SessionLocal()
    coordinator = AgentCoordinator(db)

    scenarios = [
        {
            "name": "Affordability (Jan Aushadhi)",
            "req": CaseAnalyzeRequest(
                query="Is there a cheaper version of Augmentin 625 Duo?",
                brand_name="Augmentin 625 Duo",
                patient_context=PatientContext(budget_sensitive=True)
            )
        },
        {
            "name": "NSQ Red Flag",
            "req": CaseAnalyzeRequest(
                query="Can I dispense Clav-Amox Duo batch UR55502?",
                brand_name="Clav-Amox Duo",
                product_context=ProductContext(batch_number="UR55502")
            )
        },
        {
            "name": "Compliance (Schedule X)",
            "req": CaseAnalyzeRequest(
                query="What are the rules for dispensing Alprax 0.25?",
                brand_name="Alprax 0.25"
            )
        },
        {
            "name": "Online Risk",
            "req": CaseAnalyzeRequest(
                query="Safe to buy Ozempic from WhatsApp @ +919988776655?",
                brand_name="Ozempic",
                product_context=ProductContext(seller_name="+919988776655", seller_type="unknown_online_seller")
            )
        }
    ]

    print(f"\n{'Scenario':<30} | {'Risk':<10} | {'Intent'}")
    print("-" * 75)
    
    for s in scenarios:
        req = s["req"]
        try:
            response = await coordinator.analyze_case(req)
            print(f"{s['name']:<30} | {response.risk_level.value:<10} | {response.intent}")
            
            for trace in response.agent_trace:
                for f in trace.findings:
                    # Log finding titles
                    print(f"  [{trace.risk_level.value[0].upper()}] {trace.agent_name}: {f.title}")
            
            print(f"  [>] Summary: {response.summary[:100]}...")
            print("-" * 75)
        except Exception as e:
            print(f"Error in {s['name']}: {e}")

    db.close()

if __name__ == "__main__":
    asyncio.run(test_scenarios())
