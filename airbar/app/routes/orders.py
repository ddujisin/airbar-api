from fastapi import APIRouter, Depends, HTTPException
from prisma import Prisma
from ..models.order import OrderCreate, OrderResponse, OrderUpdate
from ..middleware.session_middleware import get_current_session
from typing import List
from decimal import Decimal
from ..websocket.order_handler import order_manager
from ..utils.order_processor import order_processor
from ..utils.notification_manager import notification_manager, NotificationType, NotificationPriority

router = APIRouter()
db = Prisma()

@router.post("/", response_model=OrderResponse)
async def create_order(order: OrderCreate, session=Depends(get_current_session)):
    try:
        # Validate reservation status
        await order_processor.validate_reservation_status(order.reservation_id)

        # Validate items and get their details
        item_details = await order_processor.validate_items_availability(order.items)

        # Calculate total amount
        total_amount = await order_processor.calculate_order_total(order.items)

        # Create the order
        created_order = await db.order.create(
            data={
                "reservationId": order.reservation_id,
                "totalAmount": total_amount,
                "status": "PENDING",
                "notes": order.notes
            }
        )

        # Create order items
        await order_processor.create_order_items(created_order.id, item_details)

        # Fetch complete order with items
        complete_order = await db.order.find_unique(
            where={"id": created_order.id},
            include={
                "orderItems": {
                    "include": {
                        "item": True
                    }
                }
            }
        )

        # Send WebSocket notification
        await order_manager.notify_order_update(
            order_id=complete_order.id,
            reservation_id=order.reservation_id,
            status="PENDING"
        )

        # Send notifications through our new system
        await order_processor.notify_order_created(
            complete_order.id,
            order.reservation_id
        )

        return OrderResponse(**complete_order.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, session=Depends(get_current_session)):
    order = await db.order.find_unique(
        where={"id": order_id},
        include={
            "orderItems": {
                "include": {
                    "item": True
                }
            }
        }
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/reservation/{reservation_id}", response_model=List[OrderResponse])
async def get_reservation_orders(reservation_id: str, session=Depends(get_current_session)):
    orders = await db.order.find_many(
        where={"reservationId": reservation_id},
        include={
            "orderItems": {
                "include": {
                    "item": True
                }
            }
        }
    )
    return orders

@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(order_id: str, order_update: OrderUpdate, session=Depends(get_current_session)):
    try:
        updated_order = await db.order.update(
            where={"id": order_id},
            data={
                "status": order_update.status,
                "notes": order_update.notes
            },
            include={
                "orderItems": {
                    "include": {
                        "item": True
                    }
                },
                "reservation": True
            }
        )

        # Send WebSocket notification
        await order_manager.notify_order_update(
            order_id=updated_order.id,
            reservation_id=updated_order.reservation.id,
            status=updated_order.status
        )

        # Send notification for order status update
        await notification_manager.create_notification(
            type=NotificationType.NEW_ORDER,
            message=f"Order #{updated_order.id} status updated to {updated_order.status}",
            priority=NotificationPriority.MEDIUM,
            metadata={
                "order_id": updated_order.id,
                "reservation_id": updated_order.reservation.id,
                "status": updated_order.status,
                "guest_name": updated_order.reservation.guestName,
                "room_number": updated_order.reservation.roomNumber
            }
        )

        return updated_order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
