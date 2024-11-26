from typing import Dict, List
from prisma import Prisma
from fastapi import HTTPException
from decimal import Decimal
from datetime import datetime, timedelta

class OrderAnalytics:
    def __init__(self):
        self.db = Prisma()

    async def get_daily_sales_report(self, date: datetime) -> Dict:
        """Generate daily sales report."""
        try:
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)

            orders = await self.db.order.find_many(
                where={
                    "createdAt": {
                        "gte": start_date,
                        "lt": end_date
                    },
                    "status": "COMPLETED"
                },
                include={
                    "orderItems": {
                        "include": {
                            "item": True
                        }
                    },
                    "payment": True
                }
            )

            total_sales = Decimal('0')
            payment_methods = {}
            item_sales = {}
            hourly_sales = {str(i): 0 for i in range(24)}

            for order in orders:
                total_sales += order.totalAmount

                # Payment method breakdown
                if order.payment:
                    method = order.payment.method
                    payment_methods[method] = payment_methods.get(method, 0) + order.totalAmount

                # Item sales breakdown
                for order_item in order.orderItems:
                    item_id = order_item.item.id
                    if item_id not in item_sales:
                        item_sales[item_id] = {
                            "name": order_item.item.name,
                            "quantity": 0,
                            "revenue": Decimal('0')
                        }
                    item_sales[item_id]["quantity"] += order_item.quantity
                    item_sales[item_id]["revenue"] += order_item.price * order_item.quantity

                # Hourly sales breakdown
                hour = str(order.createdAt.hour)
                hourly_sales[hour] += float(order.totalAmount)

            return {
                "date": date.date(),
                "total_sales": total_sales,
                "order_count": len(orders),
                "payment_methods": payment_methods,
                "item_sales": list(item_sales.values()),
                "hourly_sales": hourly_sales
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating daily sales report: {str(e)}"
            )

    async def get_popular_items(self, days: int = 30) -> List[Dict]:
        """Get popular items based on sales data."""
        try:
            start_date = datetime.now() - timedelta(days=days)

            orders = await self.db.order.find_many(
                where={
                    "createdAt": {"gte": start_date},
                    "status": "COMPLETED"
                },
                include={
                    "orderItems": {
                        "include": {
                            "item": True
                        }
                    }
                }
            )

            item_stats = {}
            for order in orders:
                for order_item in order.orderItems:
                    item = order_item.item
                    if item.id not in item_stats:
                        item_stats[item.id] = {
                            "id": item.id,
                            "name": item.name,
                            "total_quantity": 0,
                            "total_revenue": Decimal('0'),
                            "order_count": 0
                        }

                    item_stats[item.id]["total_quantity"] += order_item.quantity
                    item_stats[item.id]["total_revenue"] += order_item.price * order_item.quantity
                    item_stats[item.id]["order_count"] += 1

            # Sort items by total quantity sold
            popular_items = sorted(
                item_stats.values(),
                key=lambda x: (x["total_quantity"], x["total_revenue"]),
                reverse=True
            )

            return popular_items
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting popular items: {str(e)}"
            )

    async def get_revenue_trends(self, days: int = 30) -> Dict:
        """Get revenue trends over time."""
        try:
            start_date = datetime.now() - timedelta(days=days)

            orders = await self.db.order.find_many(
                where={
                    "createdAt": {"gte": start_date},
                    "status": "COMPLETED"
                },
                include={
                    "payment": True
                }
            )

            daily_revenue = {}
            for order in orders:
                date_key = order.createdAt.date().isoformat()
                if date_key not in daily_revenue:
                    daily_revenue[date_key] = {
                        "date": date_key,
                        "total": Decimal('0'),
                        "order_count": 0
                    }
                daily_revenue[date_key]["total"] += order.totalAmount
                daily_revenue[date_key]["order_count"] += 1

            return {
                "daily_revenue": list(daily_revenue.values()),
                "total_revenue": sum(day["total"] for day in daily_revenue.values()),
                "total_orders": sum(day["order_count"] for day in daily_revenue.values()),
                "average_order_value": (
                    sum(day["total"] for day in daily_revenue.values()) /
                    sum(day["order_count"] for day in daily_revenue.values())
                    if daily_revenue else Decimal('0')
                )
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting revenue trends: {str(e)}"
            )

order_analytics = OrderAnalytics()
