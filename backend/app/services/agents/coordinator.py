from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.security import hash_patient_context
from app.db.models import AgentRun, PharmacyCase
from app.schemas.case import CaseAnalyzeRequest, CaseAnalyzeResponse
from app.services.agents.intent_router import IntentRouter
from app.services.agents.memory_agent import MemoryAgent
from app.services.agents.synthesis_agent import SynthesisAgent

from app.services.agents.availability_agent import AvailabilityAgent
from app.services.agents.price_janaushadhi_agent import PriceJanAushadhiAgent
from app.services.agents.prescription_compliance_agent import PrescriptionComplianceAgent
from app.services.agents.nsq_spurious_agent import NSQSpuriousAgent
from app.services.agents.scheme_claim_agent import SchemeClaimAgent
from app.services.agents.online_seller_risk_agent import OnlineSellerRiskAgent


class AgentCoordinator:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.intent_router = IntentRouter()
        
        self.availability_agent = AvailabilityAgent(db)
        self.price_janaushadhi_agent = PriceJanAushadhiAgent(db)
        self.prescription_compliance_agent = PrescriptionComplianceAgent(db)
        self.nsq_spurious_agent = NSQSpuriousAgent(db)
        self.scheme_claim_agent = SchemeClaimAgent(db)
        self.online_seller_risk_agent = OnlineSellerRiskAgent(db)
        
        self.memory_agent = MemoryAgent(db)
        self.synthesis_agent = SynthesisAgent()

    async def analyze_case(self, request: CaseAnalyzeRequest) -> CaseAnalyzeResponse:
        case = PharmacyCase(
            case_type="analysis",
            status="running",
            patient_hash=hash_patient_context(request.patient_context.model_dump()),
            drug_name=request.drug_name,
            brand_name=request.brand_name,
            location_state=request.location_state,
            case_input_json=request.model_dump(),
        )
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)

        classification = await self.intent_router.classify(request)
        agent_outputs: dict[str, dict] = {}
        
        for agent_name in classification.selected_agents:
            if agent_name == "synthesis_agent":
                continue
            run = AgentRun(
                case_id=case.id,
                agent_name=agent_name,
                status="running",
                input_json=request.model_dump(),
            )
            self.db.add(run)
            self.db.commit()
            self.db.refresh(run)
            try:
                if agent_name == "availability_agent":
                    output = await self.availability_agent.run(request)
                    agent_outputs["availability"] = output
                elif agent_name == "price_janaushadhi_agent":
                    output = await self.price_janaushadhi_agent.run(request)
                    agent_outputs["price_janaushadhi"] = output
                elif agent_name == "prescription_compliance_agent":
                    output = await self.prescription_compliance_agent.run(request)
                    agent_outputs["prescription_compliance"] = output
                elif agent_name == "nsq_spurious_agent":
                    output = await self.nsq_spurious_agent.run(request)
                    agent_outputs["nsq_spurious"] = output
                elif agent_name == "scheme_claim_agent":
                    output = await self.scheme_claim_agent.run(request)
                    agent_outputs["scheme_claim"] = output
                elif agent_name == "online_seller_risk_agent":
                    output = await self.online_seller_risk_agent.run(request)
                    agent_outputs["online_seller_risk"] = output
                else:
                    output = {"agent_name": agent_name, "status": "skipped", "risk_level": "LOW"}
                run.status = "completed"
                run.output_json = output
                run.completed_at = datetime.now(timezone.utc)
                self.db.add(run)
                self.db.commit()
            except Exception as exc:
                run.status = "failed"
                run.error_message = str(exc)
                run.completed_at = datetime.now(timezone.utc)
                self.db.add(run)
                self.db.commit()
                raise

        memory_notes = await self.memory_agent.retrieve_relevant_memory(request)
        final = await self.synthesis_agent.run(
            case_id=case.id,
            request=request,
            intent=classification.intent,
            detected_intents=classification.detected_intents,
            agent_outputs=agent_outputs,
            memory_notes=memory_notes,
        )

        case.status = "completed"
        case.case_type = classification.intent
        case.final_risk_level = final.risk_level.value
        case.final_answer = json.dumps(final.model_dump(mode="json"))
        self.db.add(case)
        self.db.commit()
        return final
