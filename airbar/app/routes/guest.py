from fastapi import APIRouter, HTTPException, Depends
from prisma import Prisma
from pydantic import BaseModel
from typing import List
from datetime import datetime
from ..middleware.auth import get_prisma

router = APIRouter()

class OrderItemCreate(BaseModel):
    itemId: str
    quantity: int

class OrderCreate(BaseModel):
    reservationId: str
    items: List[OrderItemCreate]

@router.post("/verify-pin")
async def verify_pin(pin_code: str, prisma: Prisma = Depends(get_prisma)):
    today = datetime.now().date()
    reservation = await prisma.reservation.find_first(
        where={
            'pinCode': pin_code,
            'startDate': {'lte': today},
            'endDate': {'gte': today}
        },
        include={
            'guest': True
        }
    )

    if not reservation:
        raise HTTPException(status_code=404, detail="Invalid PIN or no active reservation")

    return {
        "reservation": reservation,
        "session_token": pin_code  # Using PIN as session token for simplicity
    }

@router.get("/items/{item_id}")
async def get_item(item_id: str, prisma: Prisma = Depends(get_prisma)):
    item = await prisma.item.find_unique(where={'id': item_id})

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item

@router.get("/reservations/{pin_code}")
async def get_active_reservation(pin_code: str, prisma: Prisma = Depends(get_prisma)):
    today = datetime.now().date()
    reservation = await prisma.reservation.find_first(
        where={
            'pinCode': pin_code,
            'startDate': {'lte': today},
            'endDate': {'gte': today}
        },
        include={
            'guest': True,
            'orders': {
                'include': {
                    'orderItems': {
                        'include': {
                            'item': True
                        }
                    }
                }
            }
        }
    )

    if not reservation:
        raise HTTPException(status_code=404, detail="No active reservation found")

    return reservation

@router.post("/orders")
async def create_order(order: OrderCreate, prisma: Prisma = Depends(get_prisma)):
    # Verify reservation exists and is active
    today = datetime.now().date()
    reservation = await prisma.reservation.find_unique(
        where={'id': order.reservationId}
    )

    if not reservation or reservation.startDate.date() > today or reservation.endDate.date() < today:
        raise HTTPException(status_code=400, detail="Invalid or inactive reservation")

    # Calculate total amount and prepare order items
    total_amount = 0
    order_items_data = []

    for item in order.items:
        db_item = await prisma.item.find_unique(where={'id': item.itemId})
        if not db_item:
            raise HTTPException(status_code=404, detail=f"Item {item.itemId} not found")

        item_total = float(db_item.price) * item.quantity
        total_amount += item_total

        order_items_data.append({
            'itemId': item.itemId,
            'quantity': item.quantity,
            'price': float(db_item.price)
        })

    # Create order with items
    return await prisma.order.create(
        data={
            'reservationId': order.reservationId,
            'totalAmount': total_amount,
            'orderItems': {
                'create': order_items_data
            }
        },
        include={
            'orderItems': {
                'include': {
                    'item': True
                }
            }
        }
    )
