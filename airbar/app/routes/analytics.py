from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional
from ..utils.order_analytics import order_analytics
from ..middleware.session_middleware import get_current_session

router = APIRouter()

@router.get("/daily-sales")
async def get_daily_sales(
    date: Optional[datetime] = Query(default=None),
    session=Depends(get_current_session)
):
    """Get daily sales report for a specific date."""
    try:
        report_date = date or datetime.now()
        return await order_analytics.get_daily_sales_report(report_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/popular-items")
async def get_popular_items(
    days: int = Query(default=30, ge=1, le=365),
    session=Depends(get_current_session)
):
    """Get popular items based on sales data."""
    try:
        return await order_analytics.get_popular_items(days)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/revenue-trends")
async def get_revenue_trends(
    days: int = Query(default=30, ge=1, le=365),
    session=Depends(get_current_session)
):
    """Get revenue trends over time."""
    try:
        return await order_analytics.get_revenue_trends(days)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
