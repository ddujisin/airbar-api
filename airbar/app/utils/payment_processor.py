from decimal import Decimal
from typing import Optional, Dict
from prisma import Prisma
from fastapi import HTTPException
from ..utils.notification_manager import notification_manager, NotificationType, NotificationPriority
from ..websocket.notification_handler import notification_ws_manager

class PaymentProcessor:
    def __init__(self):
        self.db = Prisma()

    async def validate_payment_amount(self, reservation_id: str, amount: Decimal) -> bool:
        """Validates if the payment amount matches the total of unpaid orders."""
        unpaid_orders = await self.db.order.find_many(
            where={
                "reservationId": reservation_id,
                "paymentId": None,
                "status": {"not": "CANCELLED"}
            }
        )

        total_unpaid = sum(order.totalAmount for order in unpaid_orders)
        return abs(total_unpaid - amount) < Decimal('0.01')  # Allow for small rounding differences

    async def notify_payment_processed(
        self,
        payment_id: str,
        reservation_id: str,
        amount: Decimal,
        method: str
    ) -> None:
        """Send notifications for processed payment."""
        try:
            payment = await self.db.payment.find_unique(
                where={"id": payment_id},
                include={
                    "reservation": True
                }
            )

            if not payment:
                return

            notification_data = {
                "payment_id": payment.id,
                "reservation_id": reservation_id,
                "amount": float(amount),
                "method": method,
                "guest_name": payment.reservation.guestName,
                "room_number": payment.reservation.roomNumber,
                "transaction_id": payment.transactionId
            }

            # Create notification in database
            await notification_manager.create_notification(
                type=NotificationType.PAYMENT,
                message=f"Payment processed: ${amount} via {method}",
                priority=NotificationPriority.MEDIUM,
                metadata=notification_data
            )

            # Send real-time notification via WebSocket
            await notification_ws_manager.notify_payment(notification_data)

        except Exception as e:
            print(f"Error sending payment notification: {str(e)}")

    async def process_room_charge(
        self,
        reservation_id: str,
        amount: Decimal,
        room_number: str
    ) -> Dict:
        """Process a room charge payment."""
        try:
            # Verify reservation exists
            reservation = await self.db.reservation.find_unique(
                where={"id": reservation_id}
            )
            if not reservation:
                raise HTTPException(status_code=404, detail="Reservation not found")

            # Validate room number matches reservation
            if reservation.roomNumber != room_number:
                raise HTTPException(
                    status_code=400,
                    detail="Room number does not match reservation"
                )

            # Create payment record
            payment = await self.db.payment.create(
                data={
                    "reservationId": reservation_id,
                    "amount": amount,
                    "method": "ROOM_CHARGE",
                    "status": "COMPLETED",
                    "transactionId": f"RC-{reservation.roomNumber}-{reservation_id[:8]}"
                }
            )

            # Send payment notification
            await self.notify_payment_processed(
                payment.id,
                reservation_id,
                amount,
                "ROOM_CHARGE"
            )

            return {
                "payment_id": payment.id,
                "status": "COMPLETED",
                "transaction_id": payment.transactionId
            }

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def process_card_payment(
        self,
        reservation_id: str,
        amount: Decimal,
        card_token: str
    ) -> Dict:
        """Process a credit card payment."""
        try:
            # In a real implementation, this would integrate with a payment gateway
            # For now, we'll simulate a successful card payment
            payment = await self.db.payment.create(
                data={
                    "reservationId": reservation_id,
                    "amount": amount,
                    "method": "CREDIT_CARD",
                    "status": "COMPLETED",
                    "transactionId": f"CC-{card_token[:8]}-{reservation_id[:8]}"
                }
            )

            # Send payment notification
            await self.notify_payment_processed(
                payment.id,
                reservation_id,
                amount,
                "CREDIT_CARD"
            )

            return {
                "payment_id": payment.id,
                "status": "COMPLETED",
                "transaction_id": payment.transactionId
            }

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

payment_processor = PaymentProcessor()
