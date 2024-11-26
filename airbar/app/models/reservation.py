from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ReservationCreate(BaseModel):
    room_number: str
    guest_name: str
    check_in: datetime
    check_out: datetime

    @validator('check_out')
    def check_out_after_check_in(cls, v, values):
        if 'check_in' in values and v <= values['check_in']:
            raise ValueError('check_out must be after check_in')
        return v

class ReservationUpdate(BaseModel):
    room_number: Optional[str]
    guest_name: Optional[str]
    check_in: Optional[datetime]
    check_out: Optional[datetime]
    status: Optional[str]

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['PENDING', 'CHECKED_IN', 'CHECKED_OUT', 'CANCELLED']
        if v and v not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v

    @validator('check_out')
    def check_out_after_check_in(cls, v, values):
        if v and 'check_in' in values and values['check_in'] and v <= values['check_in']:
            raise ValueError('check_out must be after check_in')
        return v

class ReservationResponse(BaseModel):
    id: str
    room_number: str
    guest_name: str
    check_in: datetime
    check_out: datetime
    status: str
    pin: Optional[str]
    created_at: datetime
    updated_at: datetime
    total_spent: Optional[Decimal]
