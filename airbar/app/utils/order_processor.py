from decimal import Decimal
from typing import List, Dict
from prisma import Prisma
from fastapi import HTTPException
from ..models.order import OrderItemCreate
from ..utils.notification_manager import notification_manager, NotificationType, NotificationPriority
from ..websocket.notification_handler import notification_ws_manager

class OrderProcessor:
    def __init__(self):
        self.db = Prisma()

    async def calculate_order_total(self, items: List[OrderItemCreate]) -> Decimal:
        """Calculate the total amount for an order."""
        total = Decimal('0')
        for item in items:
            db_item = await self.db.item.find_unique(where={"id": item.item_id})
            if not db_item:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item {item.item_id} not found"
                )
            total += db_item.price * Decimal(str(item.quantity))
        return total

    async def validate_reservation_status(self, reservation_id: str) -> bool:
        """Check if the reservation is active and valid for ordering."""
        reservation = await self.db.reservation.find_unique(
            where={"id": reservation_id}
        )
        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")

        if reservation.status not in ["ACTIVE", "CHECKED_IN"]:
            raise HTTPException(
                status_code=400,
                detail="Orders can only be placed for active reservations"
            )
        return True

    async def validate_items_availability(
        self,
        items: List[OrderItemCreate]
    ) -> Dict[str, Dict]:
        """Validate that all items exist and are available."""
        item_details = {}
        for item in items:
            db_item = await self.db.item.find_unique(where={"id": item.item_id})
            if not db_item:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item {item.item_id} not found"
                )
            if not db_item.available:
                raise HTTPException(
                    status_code=400,
                    detail=f"Item {db_item.name} is currently unavailable"
                )
            item_details[item.item_id] = {
                "name": db_item.name,
                "price": db_item.price,
                "quantity": item.quantity
            }
        return item_details

    async def create_order_items(
        self,
        order_id: str,
        items: Dict[str, Dict]
    ) -> List[Dict]:
        """Create order items in the database."""
        order_items = []
        for item_id, details in items.items():
            order_item = await self.db.orderItem.create(
                data={
                    "orderId": order_id,
                    "itemId": item_id,
                    "quantity": details["quantity"],
                    "price": details["price"]
                }
            )
            order_items.append(order_item)
        return order_items

    async def get_unpaid_orders_total(self, reservation_id: str) -> Decimal:
        """Calculate total amount of unpaid orders for a reservation."""
        unpaid_orders = await self.db.order.find_many(
            where={
                "reservationId": reservation_id,
                "paymentId": None,
                "status": {"not": "CANCELLED"}
            }
        )
        return sum(order.totalAmount for order in unpaid_orders)

    async def notify_order_created(self, order_id: str, reservation_id: str) -> None:
        """Send notifications for new order creation."""
        try:
            order = await self.db.order.find_unique(
                where={"id": order_id},
                include={
                    "orderItems": {
                        "include": {
                            "item": True
                        }
                    },
                    "reservation": True
                }
            )

            if not order:
                return

            notification_data = {
                "order_id": order.id,
                "reservation_id": reservation_id,
                "guest_name": order.reservation.guestName,
                "room_number": order.reservation.roomNumber,
                "total_amount": float(order.totalAmount),
                "items": [
                    {
                        "name": item.item.name,
                        "quantity": item.quantity,
                        "price": float(item.price)
                    }
                    for item in order.orderItems
                ]
            }

            await notification_manager.create_notification(
                type=NotificationType.NEW_ORDER,
                message=f"New order #{order.id} from Room {order.reservation.roomNumber}",
                priority=NotificationPriority.MEDIUM,
                metadata=notification_data
            )

            await notification_ws_manager.notify_new_order(notification_data)

        except Exception as e:
            print(f"Error sending order notification: {str(e)}")

order_processor = OrderProcessor()
