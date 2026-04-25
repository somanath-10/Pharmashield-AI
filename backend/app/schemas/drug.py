from pydantic import BaseModel

class DrugBase(BaseModel):
    generic_name: str
    brand_name: str | None = None
    composition: str | None = None
    strength: str | None = None
    dosage_form: str | None = None
    schedule_category: str | None = None

class DrugResponse(DrugBase):
    id: str
