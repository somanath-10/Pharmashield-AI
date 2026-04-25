from pydantic import BaseModel

class InventoryBase(BaseModel):
    location_id: str
    quantity_on_hand: int

class InventoryResponse(InventoryBase):
    id: str
