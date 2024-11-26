from typing import Dict, List, Optional
from prisma import Prisma
from fastapi import HTTPException
from decimal import Decimal
from datetime import datetime

class InventoryManager:
    def __init__(self):
        self.db = Prisma()

    async def update_stock_level(self, item_id: str, quantity: int) -> Dict:
        """Update stock level for an item."""
        try:
            item = await self.db.item.find_unique(
                where={"id": item_id}
            )
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")

            updated_item = await self.db.item.update(
                where={"id": item_id},
                data={
                    "stockLevel": quantity,
                    "available": quantity > 0
                }
            )
            return {
                "id": updated_item.id,
                "name": updated_item.name,
                "stockLevel": updated_item.stockLevel,
                "available": updated_item.available
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error updating stock level: {str(e)}"
            )

    async def get_low_stock_items(self, threshold: int = 10) -> List[Dict]:
        """Get items with stock levels below threshold."""
        try:
            items = await self.db.item.find_many(
                where={
                    "stockLevel": {
                        "lte": threshold
                    }
                }
            )
            return [
                {
                    "id": item.id,
                    "name": item.name,
                    "stockLevel": item.stockLevel,
                    "category": item.category,
                    "price": item.price
                }
                for item in items
            ]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching low stock items: {str(e)}"
            )

    async def adjust_stock_after_order(self, order_items: List[Dict]) -> None:
        """Adjust stock levels after order completion."""
        try:
            for order_item in order_items:
                item = await self.db.item.find_unique(
                    where={"id": order_item["item_id"]}
                )
                if not item:
                    continue

                new_stock = max(0, item.stockLevel - order_item["quantity"])
                await self.db.item.update(
                    where={"id": item.id},
                    data={
                        "stockLevel": new_stock,
                        "available": new_stock > 0
                    }
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error adjusting stock levels: {str(e)}"
            )

    async def get_inventory_value(self) -> Dict:
        """Calculate total inventory value."""
        try:
            items = await self.db.item.find_many()
            total_value = sum(
                Decimal(str(item.price)) * item.stockLevel
                for item in items
            )
            return {
                "total_value": total_value,
                "item_count": len(items),
                "total_stock": sum(item.stockLevel for item in items)
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error calculating inventory value: {str(e)}"
            )

inventory_manager = InventoryManager()
