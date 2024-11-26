from fastapi import APIRouter, Depends, HTTPException
from ..models.reservation import ReservationCreate, ReservationResponse, ReservationUpdate
from ..middleware.session_middleware import get_current_session
from ..utils.pin_generator import pin_generator
from prisma import Prisma
from typing import List

router = APIRouter()
db = Prisma()

@router.post("/", response_model=ReservationResponse)
async def create_reservation(reservation: ReservationCreate, session=Depends(get_current_session)):
    """Create a new reservation with a PIN code."""
    try:
        # Create reservation
        created_reservation = await db.reservation.create(
            data={
                "roomNumber": reservation.room_number,
                "guestName": reservation.guest_name,
                "checkIn": reservation.check_in,
                "checkOut": reservation.check_out,
                "status": "PENDING"
            }
        )

        # Generate PIN for the reservation
        await pin_generator.create_reservation_pin(created_reservation.id)

        # Fetch updated reservation
        complete_reservation = await db.reservation.find_unique(
            where={"id": created_reservation.id}
        )

        return ReservationResponse(**complete_reservation.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(reservation_id: str, session=Depends(get_current_session)):
    """Get reservation details."""
    reservation = await db.reservation.find_unique(
        where={"id": reservation_id}
    )
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation

@router.get("/", response_model=List[ReservationResponse])
async def list_reservations(session=Depends(get_current_session)):
    """List all active reservations."""
    reservations = await db.reservation.find_many(
        where={"status": {"not": "CHECKED_OUT"}}
    )
    return reservations

@router.patch("/{reservation_id}", response_model=ReservationResponse)
async def update_reservation(
    reservation_id: str,
    reservation: ReservationUpdate,
    session=Depends(get_current_session)
):
    """Update reservation details."""
    try:
        updated_reservation = await db.reservation.update(
            where={"id": reservation_id},
            data={
                "roomNumber": reservation.room_number,
                "guestName": reservation.guest_name,
                "checkIn": reservation.check_in,
                "checkOut": reservation.check_out,
                "status": reservation.status
            }
        )
        return updated_reservation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{reservation_id}/reset-pin")
async def reset_reservation_pin(reservation_id: str, session=Depends(get_current_session)):
    """Reset the PIN code for a reservation."""
    try:
        new_pin = await pin_generator.reset_pin(reservation_id)
        return {"message": "PIN reset successful", "pin": new_pin}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate-pin")
async def validate_reservation_pin(pin: str, reservation_id: str = None):
    """Validate a reservation PIN code."""
    try:
        is_valid = await pin_generator.validate_pin(pin, reservation_id)
        return {"valid": is_valid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
