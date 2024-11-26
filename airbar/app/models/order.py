from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class OrderItemCreate(BaseModel):
    item_id: str
    quantity: int

class OrderCreate(BaseModel):
    reservation_id: str
    items: List[OrderItemCreate]
    notes: Optional[str] = None

class OrderItemResponse(BaseModel):
    id: str
    item_id: str
    quantity: int
    price: Decimal
    created_at: datetime
    updated_at: datetime

class OrderResponse(BaseModel):
    id: str
    reservation_id: str
    total_amount: Decimal
    status: str
    payment_id: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItemResponse]

class OrderUpdate(BaseModel):
    status: Optional[str]
    notes: Optional[str]
