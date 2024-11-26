from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List
from ..utils.inventory_manager import inventory_manager
from ..middleware.session_middleware import get_current_session
from pydantic import BaseModel

router = APIRouter()

class StockUpdate(BaseModel):
    quantity: int

@router.put("/{item_id}/stock")
async def update_stock(
    item_id: str,
    stock_data: StockUpdate,
    session=Depends(get_current_session)
) -> Dict:
    """Update stock level for an item."""
    return await inventory_manager.update_stock_level(item_id, stock_data.quantity)

@router.get("/low-stock")
async def get_low_stock_items(
    threshold: int = Query(default=10, ge=0),
    session=Depends(get_current_session)
) -> List[Dict]:
    """Get items with low stock levels."""
    return await inventory_manager.get_low_stock_items(threshold)

@router.get("/value")
async def get_inventory_value(
    session=Depends(get_current_session)
) -> Dict:
    """Get total inventory value and statistics."""
    return await inventory_manager.get_inventory_value()
