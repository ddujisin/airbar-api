import secrets
import string
from typing import Optional
from prisma import Prisma
from fastapi import HTTPException

class PINGenerator:
    def __init__(self):
        self.db = Prisma()
        self.PIN_LENGTH = 4

    def generate_pin(self) -> str:
        """Generate a random 4-digit PIN code."""
        return ''.join(secrets.choice(string.digits) for _ in range(self.PIN_LENGTH))

    async def create_reservation_pin(self, reservation_id: str) -> str:
        """Create a new PIN for a reservation."""
        try:
            # Generate PIN and ensure it's unique
            while True:
                pin = self.generate_pin()
                existing = await self.db.reservation.find_first(
                    where={
                        "pin": pin,
                        "status": {"not": "CHECKED_OUT"}
                    }
                )
                if not existing:
                    break

            # Update reservation with new PIN
            await self.db.reservation.update(
                where={"id": reservation_id},
                data={"pin": pin}
            )

            return pin

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating PIN: {str(e)}"
            )

    async def validate_pin(self, pin: str, reservation_id: Optional[str] = None) -> bool:
        """
        Validate a PIN code. If reservation_id is provided,
        verify the PIN belongs to that specific reservation.
        """
        try:
            where_clause = {
                "pin": pin,
                "status": {"not": "CHECKED_OUT"}
            }
            if reservation_id:
                where_clause["id"] = reservation_id

            reservation = await self.db.reservation.find_first(
                where=where_clause
            )

            return reservation is not None

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error validating PIN: {str(e)}"
            )

    async def reset_pin(self, reservation_id: str) -> str:
        """Reset a reservation's PIN code."""
        try:
            # Verify reservation exists
            reservation = await self.db.reservation.find_unique(
                where={"id": reservation_id}
            )
            if not reservation:
                raise HTTPException(status_code=404, detail="Reservation not found")

            # Generate new PIN
            return await self.create_reservation_pin(reservation_id)

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error resetting PIN: {str(e)}"
            )

pin_generator = PINGenerator()
