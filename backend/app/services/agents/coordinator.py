from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.security import hash_patient_context
from app.db.models import AgentRun, PharmacyCase
from app.schemas.case import CaseAnalyzeRequest, CaseAnalyzeResponse
from app.services.agents.authenticity_agent import AuthenticityAgent
from app.services.agents.coverage_agent import CoverageAgent
from app.services.agents.intent_router import IntentRouter
from app.services.agents.memory_agent import MemoryAgent
from app.services.agents.shortage_agent import ShortageAgent
from app.services.agents.synthesis_agent import SynthesisAgent
from app.services.guardrails.output_validator import OutputValidator


class AgentCoordinator:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.intent_router = IntentRouter()
        self.shortage_agent = ShortageAgent(db)
        self.coverage_agent = CoverageAgent(db)
        self.authenticity_agent = AuthenticityAgent(db)
        self.memory_agent = MemoryAgent(db)
        self.synthesis_agent = SynthesisAgent()
        self.guardrails = OutputValidator()

    async def analyze_case(self, request: CaseAnalyzeRequest) -> CaseAnalyzeResponse:
        case = PharmacyCase(
            case_type="analysis",
            status="running",
            patient_hash=hash_patient_context(request.patient_context.model_dump()),
            drug_name=request.drug_name,
            payer_name=request.payer_name,
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
                if agent_name == "shortage_agent":
                    output = await self.shortage_agent.run(request)
                    agent_outputs["shortage"] = output
                elif agent_name == "coverage_agent":
                    output = await self.coverage_agent.run(request)
                    agent_outputs["coverage"] = output
                elif agent_name == "authenticity_agent":
                    output = await self.authenticity_agent.run(request)
                    agent_outputs["authenticity"] = output
                else:
                    output = {"agent_name": agent_name, "status": "skipped", "risk_level": "LOW"}
                run.status = "completed"
                run.output_json = output
                run.completed_at = datetime.now(timezone.utc)
                self.db.add(run)
                self.db.commit()
            except Exception as exc:  # pragma: no cover - defensive persistence
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
        validated = self.guardrails.validate(final)

        case.status = "completed"
        case.case_type = classification.intent
        case.final_risk_level = validated.risk_level.value
        case.final_answer = json.dumps(validated.model_dump(mode="json"))
        self.db.add(case)
        self.db.commit()
        return validated
