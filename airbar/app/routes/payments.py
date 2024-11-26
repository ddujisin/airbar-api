from fastapi import APIRouter, Depends, HTTPException
from prisma import Prisma
from ..models.payment import PaymentCreate, PaymentResponse, PaymentUpdate
from ..middleware.session_middleware import get_current_session
from typing import List
from decimal import Decimal
from ..websocket.order_handler import order_manager
from ..utils.payment_processor import payment_processor
from ..utils.notification_manager import notification_manager, NotificationType, NotificationPriority

router = APIRouter()
db = Prisma()

@router.post("/", response_model=PaymentResponse)
async def create_payment(payment: PaymentCreate, session=Depends(get_current_session)):
    try:
        # Validate payment amount
        amount_valid = await payment_processor.validate_payment_amount(
            payment.reservation_id,
            payment.amount
        )
        if not amount_valid:
            raise HTTPException(status_code=400, detail="Invalid payment amount")

        # Process payment based on method
        if payment.method == "ROOM_CHARGE":
            result = await payment_processor.process_room_charge(
                payment.reservation_id,
                payment.amount,
                payment.room_number
            )
        elif payment.method == "CREDIT_CARD":
            result = await payment_processor.process_card_payment(
                payment.reservation_id,
                payment.amount,
                payment.card_token
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported payment method")

        # Get the created payment
        payment_record = await db.payment.find_unique(
            where={"id": result["payment_id"]},
            include={"orders": True}
        )

        # Update associated orders if payment was successful
        if payment_record.status == "COMPLETED" and payment.order_ids:
            await db.order.update_many(
                where={
                    "id": {"in": payment.order_ids},
                    "paymentId": None
                },
                data={
                    "paymentId": payment_record.id,
                    "status": "COMPLETED"
                }
            )

            # Send notifications for completed orders
            for order_id in payment.order_ids:
                await order_manager.notify_order_update(
                    order_id=order_id,
                    reservation_id=payment.reservation_id,
                    status="COMPLETED"
                )

        return PaymentResponse(**payment_record.dict())

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str, session=Depends(get_current_session)):
    payment = await db.payment.find_unique(
        where={"id": payment_id},
        include={"orders": True}
    )
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.get("/reservation/{reservation_id}", response_model=List[PaymentResponse])
async def get_reservation_payments(reservation_id: str, session=Depends(get_current_session)):
    payments = await db.payment.find_many(
        where={"reservationId": reservation_id},
        include={"orders": True}
    )
    return payments

@router.patch("/{payment_id}", response_model=PaymentResponse)
async def update_payment_status(
    payment_id: str,
    payment_update: PaymentUpdate,
    session=Depends(get_current_session)
):
    try:
        updated_payment = await db.payment.update(
            where={"id": payment_id},
            data={
                "status": payment_update.status,
                "transactionId": payment_update.transaction_id
            },
            include={
                "orders": True,
                "reservation": True
            }
        )

        # Send WebSocket notification for payment update
        await order_manager.notify_payment_update(
            payment_id=updated_payment.id,
            reservation_id=updated_payment.reservation.id,
            status=updated_payment.status
        )

        # Create notification for payment status update
        notification_data = {
            "payment_id": updated_payment.id,
            "reservation_id": updated_payment.reservation.id,
            "status": updated_payment.status,
            "guest_name": updated_payment.reservation.guestName,
            "room_number": updated_payment.reservation.roomNumber,
            "transaction_id": updated_payment.transactionId,
            "amount": float(updated_payment.amount)
        }

        await notification_manager.create_notification(
            type=NotificationType.PAYMENT,
            message=f"Payment #{updated_payment.id} status updated to {updated_payment.status}",
            priority=NotificationPriority.HIGH if updated_payment.status == "COMPLETED" else NotificationPriority.MEDIUM,
            metadata=notification_data
        )

        # If payment is completed, update associated orders and send notifications
        if payment_update.status == "COMPLETED":
            await db.order.update_many(
                where={"paymentId": payment_id},
                data={"status": "COMPLETED"}
            )

            # Send notifications for each updated order
            for order in updated_payment.orders:
                await order_manager.notify_order_update(
                    order_id=order.id,
                    reservation_id=updated_payment.reservation.id,
                    status="COMPLETED"
                )

                # Create notification for completed order
                await notification_manager.create_notification(
                    type=NotificationType.NEW_ORDER,
                    message=f"Order #{order.id} completed with payment #{payment_id}",
                    priority=NotificationPriority.MEDIUM,
                    metadata={
                        "order_id": order.id,
                        "payment_id": payment_id,
                        "reservation_id": updated_payment.reservation.id,
                        "status": "COMPLETED",
                        "guest_name": updated_payment.reservation.guestName,
                        "room_number": updated_payment.reservation.roomNumber
                    }
                )

        return updated_payment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
