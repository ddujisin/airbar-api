from fastapi import APIRouter, Depends, HTTPException
from prisma import Prisma
from ..middleware.auth import get_current_admin, get_prisma, create_access_token
from pydantic import BaseModel
import bcrypt
from typing import List, Optional
from datetime import datetime
import random

router = APIRouter()

class AdminLogin(BaseModel):
    email: str
    password: str

class AdminCreate(BaseModel):
    email: str
    password: str

class ReservationCreate(BaseModel):
    startDate: datetime
    endDate: datetime
    guestId: str

class GuestCreate(BaseModel):
    name: str
    email: str

class ItemCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    category: Optional[str] = None

@router.post("/login")
async def login(login_data: AdminLogin, prisma: Prisma = Depends(get_prisma)):
    admin = await prisma.admin.find_first(
        where={
            'email': login_data.email
        }
    )
    if not admin or not bcrypt.checkpw(login_data.password.encode(), admin.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": admin.id, "is_admin": True})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/reservations")
async def create_reservation(reservation: ReservationCreate,
                           prisma: Prisma = Depends(get_prisma),
                           admin=Depends(get_current_admin)):
    pin_code = str(random.randint(1000, 9999))
    return await prisma.reservation.create(
        data={
            'startDate': reservation.startDate,
            'endDate': reservation.endDate,
            'guestId': reservation.guestId,
            'pinCode': pin_code
        }
    )

@router.get("/reservations")
async def get_reservations(prisma: Prisma = Depends(get_prisma),
                         admin=Depends(get_current_admin)):
    return await prisma.reservation.find_many(
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

@router.delete("/reservations/{reservation_id}")
async def delete_reservation(reservation_id: str,
                           prisma: Prisma = Depends(get_prisma),
                           admin=Depends(get_current_admin)):
    return await prisma.reservation.delete(
        where={
            'id': reservation_id
        }
    )

@router.post("/guests")
async def create_guest(guest: GuestCreate,
                      prisma: Prisma = Depends(get_prisma),
                      admin=Depends(get_current_admin)):
    return await prisma.guest.create(
        data={
            'name': guest.name,
            'email': guest.email
        }
    )

@router.get("/guests")
async def get_guests(prisma: Prisma = Depends(get_prisma),
                    admin=Depends(get_current_admin)):
    return await prisma.guest.find_many()

@router.delete("/guests/{guest_id}")
async def delete_guest(guest_id: str,
                      prisma: Prisma = Depends(get_prisma),
                      admin=Depends(get_current_admin)):
    return await prisma.guest.delete(
        where={
            'id': guest_id
        }
    )

@router.post("/items")
async def create_item(item: ItemCreate,
                     prisma: Prisma = Depends(get_prisma),
                     admin=Depends(get_current_admin)):
    # Generate a unique QR code using UUID
    import uuid
    qr_code = str(uuid.uuid4())

    return await prisma.item.create(
        data={
            'name': item.name,
            'price': item.price,
            'qrCode': qr_code,
            'description': item.description,
            'category': item.category
        }
    )

@router.get("/items")
async def get_items(prisma: Prisma = Depends(get_prisma),
                   admin=Depends(get_current_admin)):
    return await prisma.item.find_many()

@router.put("/items/{item_id}")
async def update_item(item_id: str,
                     item: ItemCreate,
                     prisma: Prisma = Depends(get_prisma),
                     admin=Depends(get_current_admin)):
    return await prisma.item.update(
        where={'id': item_id},
        data={
            'name': item.name,
            'price': item.price,
            'description': item.description,
            'category': item.category
        }
    )

@router.delete("/items/{item_id}")
async def delete_item(item_id: str,
                     prisma: Prisma = Depends(get_prisma),
                     admin=Depends(get_current_admin)):
    return await prisma.item.delete(
        where={
            'id': item_id
        }
    )
