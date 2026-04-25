from pydantic import BaseModel

class PriceRecordBase(BaseModel):
    generic_name: str
    brand_name: str | None = None
    mrp: float | None = None
    ceiling_price: float | None = None
    source: str

class PriceRecordResponse(PriceRecordBase):
    id: str
