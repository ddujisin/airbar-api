from pydantic import BaseModel, validator
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class PaymentCreate(BaseModel):
    reservation_id: str
    amount: Decimal
    method: str
    transaction_id: Optional[str]
    order_ids: Optional[List[str]]
    # New fields for different payment methods
    card_token: Optional[str]
    room_number: Optional[str]

    @validator('method')
    def validate_payment_method(cls, v):
        valid_methods = ['CREDIT_CARD', 'ROOM_CHARGE']
        if v not in valid_methods:
            raise ValueError(f'Payment method must be one of: {valid_methods}')
        return v

    @validator('card_token')
    def validate_card_token(cls, v, values):
        if values.get('method') == 'CREDIT_CARD' and not v:
            raise ValueError('card_token is required for credit card payments')
        return v

    @validator('room_number')
    def validate_room_number(cls, v, values):
        if values.get('method') == 'ROOM_CHARGE' and not v:
            raise ValueError('room_number is required for room charge payments')
        return v

class PaymentResponse(BaseModel):
    id: str
    reservation_id: str
    amount: Decimal
    status: str
    method: str
    transaction_id: Optional[str]
    created_at: datetime
    updated_at: datetime

class PaymentUpdate(BaseModel):
    status: str
    transaction_id: Optional[str]
