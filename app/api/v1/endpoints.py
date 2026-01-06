from fastapi import APIRouter, HTTPException
from app.application.trading_service import trading_service
from app.domain.models import Stock, Order

router = APIRouter()

@router.get("/stock/{code}", response_model=Stock)
def get_stock(code: str):
    try:
        return trading_service.get_stock_detail(code)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/order")
def create_order(order: Order):
    try:
        return trading_service.execute_order(
            order.stock_code, order.quantity, order.price, order.order_type
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
