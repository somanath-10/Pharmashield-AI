from pydantic import BaseModel

class SchemeBase(BaseModel):
    scheme_name: str
    scheme_type: str | None = None
    eligibility_summary: str | None = None

class SchemeResponse(SchemeBase):
    id: str
