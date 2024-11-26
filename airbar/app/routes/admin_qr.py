from fastapi import APIRouter, Depends, HTTPException
from ..utils.qr_generator import qr_generator
from prisma import Prisma
from typing import List
from ..middleware.session_middleware import get_current_session

router = APIRouter()
db = Prisma()

@router.get("/items/{item_id}/qr")
async def get_item_qr(item_id: str, session=Depends(get_current_session)):
    """Generate QR code for a single item."""
    try:
        item = await db.item.find_unique(where={"id": item_id})
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        qr_code = qr_generator.generate_item_qr({
            "id": item.id,
            "name": item.name,
            "price": item.price
        })

        return {
            "item_id": item.id,
            "item_name": item.name,
            "qr_code": qr_code
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/items/batch-qr")
async def generate_batch_qr_codes(
    item_ids: List[str],
    session=Depends(get_current_session)
):
    """Generate QR codes for multiple items."""
    try:
        items = await db.item.find_many(
            where={"id": {"in": item_ids}}
        )
        if not items:
            raise HTTPException(status_code=404, detail="No items found")

        item_data = [{
            "id": item.id,
            "name": item.name,
            "price": item.price
        } for item in items]

        return qr_generator.generate_batch_qr_codes(item_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items/print-labels")
async def get_all_items_qr(session=Depends(get_current_session)):
    """Generate QR codes for all available items."""
    try:
        items = await db.item.find_many(
            where={"available": True}
        )
        if not items:
            raise HTTPException(status_code=404, detail="No items found")

        item_data = [{
            "id": item.id,
            "name": item.name,
            "price": item.price
        } for item in items]

        return qr_generator.generate_batch_qr_codes(item_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
