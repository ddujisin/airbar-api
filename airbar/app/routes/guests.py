from fastapi import APIRouter, Depends, HTTPException
from prisma import Prisma
from pydantic import BaseModel, EmailStr
from typing import List
from ..middleware.auth import get_current_admin, get_prisma

router = APIRouter()

class GuestCreate(BaseModel):
    name: str
    email: EmailStr

class GuestUpdate(BaseModel):
    name: str
    email: EmailStr

class Guest(BaseModel):
    id: str
    name: str
    email: str
    createdAt: str

    class Config:
        from_attributes = True

@router.get("", response_model=List[Guest])
async def get_guests(db: Prisma = Depends(get_prisma), _=Depends(get_current_admin)):
    try:
        guests = await db.guest.find_many(
            order={
                "createdAt": "desc"
            }
        )
        return guests
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=Guest)
async def create_guest(guest: GuestCreate, db: Prisma = Depends(get_prisma), _=Depends(get_current_admin)):
    try:
        # Check if guest with email already exists
        existing_guest = await db.guest.find_first(
            where={
                "email": guest.email
            }
        )
        if existing_guest:
            raise HTTPException(status_code=400, detail="Guest with this email already exists")

        new_guest = await db.guest.create(
            data={
                "name": guest.name,
                "email": guest.email,
            }
        )
        return new_guest
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{guest_id}", response_model=Guest)
async def update_guest(guest_id: str, guest: GuestUpdate, db: Prisma = Depends(get_prisma), _=Depends(get_current_admin)):
    try:
        # Check if guest exists
        existing_guest = await db.guest.find_unique(
            where={
                "id": guest_id
            }
        )
        if not existing_guest:
            raise HTTPException(status_code=404, detail="Guest not found")

        # Check if email is taken by another guest
        email_taken = await db.guest.find_first(
            where={
                "email": guest.email,
                "id": {"not": guest_id}
            }
        )
        if email_taken:
            raise HTTPException(status_code=400, detail="Email is already taken by another guest")

        updated_guest = await db.guest.update(
            where={
                "id": guest_id
            },
            data={
                "name": guest.name,
                "email": guest.email,
            }
        )
        return updated_guest
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{guest_id}")
async def delete_guest(guest_id: str, db: Prisma = Depends(get_prisma), _=Depends(get_current_admin)):
    try:
        # Check if guest exists
        existing_guest = await db.guest.find_unique(
            where={
                "id": guest_id
            }
        )
        if not existing_guest:
            raise HTTPException(status_code=404, detail="Guest not found")

        # Check if guest has any reservations
        reservations = await db.reservation.find_first(
            where={
                "guestId": guest_id
            }
        )
        if reservations:
            raise HTTPException(status_code=400, detail="Cannot delete guest with existing reservations")

        await db.guest.delete(
            where={
                "id": guest_id
            }
        )
        return {"message": "Guest deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
