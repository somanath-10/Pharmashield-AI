from pydantic import BaseModel

class ComplianceBase(BaseModel):
    rule_summary: str

class ComplianceResponse(ComplianceBase):
    id: str
