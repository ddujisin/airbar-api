from fastapi import APIRouter, Depends, HTTPException
from prisma import Prisma
from datetime import datetime, date
from ..middleware.auth import get_current_admin
from typing import List

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(db: Prisma = Depends(Prisma), _=Depends(get_current_admin)):
    try:
        # Get total items count
        total_items = await db.item.count()

        # Get active reservations (current date falls between start and end date)
        today = date.today()
        active_reservations = await db.reservation.count(
            where={
                "startDate": {"lte": today},
                "endDate": {"gte": today}
            }
        )

        # Get today's orders
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        today_orders = await db.order.count(
            where={
                "createdAt": {
                    "gte": today_start,
                    "lte": today_end
                }
            }
        )

        # Get total unique guests
        total_guests = await db.guest.count()

        # Get recent orders with guest information
        recent_orders = await db.order.find_many(
            take=5,
            order={
                "createdAt": "desc"
            },
            include={
                "reservation": {
                    "include": {
                        "guest": True
                    }
                }
            }
        )

        return {
            "totalItems": total_items,
            "activeReservations": active_reservations,
            "todayOrders": today_orders,
            "totalGuests": total_guests,
            "recentOrders": [
                {
                    "id": order.id,
                    "createdAt": order.createdAt,
                    "total": order.total,
                    "guestName": order.reservation.guest.name
                }
                for order in recent_orders
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
