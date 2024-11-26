from typing import Dict, List, Optional
from prisma import Prisma
from fastapi import HTTPException
from decimal import Decimal

class GuestProfileManager:
    def __init__(self):
        self.db = Prisma()

    async def get_guest_profile(self, reservation_id: str) -> Dict:
        """Get guest profile with order history and preferences."""
        try:
            reservation = await self.db.reservation.find_unique(
                where={"id": reservation_id},
                include={
                    "orders": {
                        "include": {
                            "orderItems": {
                                "include": {
                                    "item": True
                                }
                            }
                        }
                    }
                }
            )

            if not reservation:
                raise HTTPException(status_code=404, detail="Reservation not found")

            # Calculate favorite items based on order history
            item_frequency = {}
            total_spent = Decimal('0')

            for order in reservation.orders:
                total_spent += order.totalAmount
                for order_item in order.orderItems:
                    item_id = order_item.item.id
                    if item_id in item_frequency:
                        item_frequency[item_id]["count"] += order_item.quantity
                        item_frequency[item_id]["total_spent"] += (
                            order_item.price * order_item.quantity
                        )
                    else:
                        item_frequency[item_id] = {
                            "count": order_item.quantity,
                            "name": order_item.item.name,
                            "total_spent": order_item.price * order_item.quantity
                        }

            # Sort items by frequency and total spent
            favorite_items = sorted(
                [
                    {
                        "item_id": k,
                        "name": v["name"],
                        "order_count": v["count"],
                        "total_spent": v["total_spent"]
                    }
                    for k, v in item_frequency.items()
                ],
                key=lambda x: (x["order_count"], x["total_spent"]),
                reverse=True
            )[:5]  # Top 5 favorite items

            return {
                "guest_name": reservation.guestName,
                "room_number": reservation.roomNumber,
                "total_orders": len(reservation.orders),
                "total_spent": total_spent,
                "favorite_items": favorite_items,
                "status": reservation.status,
                "check_in": reservation.checkIn,
                "check_out": reservation.checkOut
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching guest profile: {str(e)}"
            )

    async def get_guest_recommendations(
        self,
        reservation_id: str,
        limit: int = 5
    ) -> List[Dict]:
        """Get personalized item recommendations for guest."""
        try:
            # Get guest's order history
            reservation = await self.db.reservation.find_unique(
                where={"id": reservation_id},
                include={
                    "orders": {
                        "include": {
                            "orderItems": {
                                "include": {
                                    "item": True
                                }
                            }
                        }
                    }
                }
            )

            if not reservation:
                raise HTTPException(status_code=404, detail="Reservation not found")

            # Get items ordered by guest
            ordered_items = set()
            for order in reservation.orders:
                for order_item in order.orderItems:
                    ordered_items.add(order_item.item.id)

            # Get available items not ordered by guest
            new_items = await self.db.item.find_many(
                where={
                    "id": {"not_in": list(ordered_items)},
                    "available": True
                },
                take=limit
            )

            return [
                {
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "price": item.price,
                    "category": item.category
                }
                for item in new_items
            ]

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating recommendations: {str(e)}"
            )

guest_profile_manager = GuestProfileManager()
