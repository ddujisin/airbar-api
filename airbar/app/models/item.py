from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

class ItemBase(BaseModel):
    name: str = Field(..., description="Name of the item")
    price: Decimal = Field(..., description="Price of the item", gt=0)
    description: Optional[str] = Field(None, description="Description of the item")
    category: Optional[str] = Field(None, description="Category of the item")

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    name: Optional[str] = Field(None, description="Name of the item")
    price: Optional[Decimal] = Field(None, description="Price of the item", gt=0)

class Item(ItemBase):
    id: str
    qrCode: str

    class Config:
        from_attributes = True
