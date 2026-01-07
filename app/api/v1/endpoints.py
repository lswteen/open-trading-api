from fastapi import APIRouter, HTTPException
from app.application.trading_service import trading_service
from app.domain.models import Stock, Order

router = APIRouter()

@router.get("/indices")
def get_indices():
    try:
        return trading_service.get_market_indices()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/top-stocks")
def get_top_stocks(market: str = "J"):
    try:
        return trading_service.get_market_top_stocks(market)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/index-chart/{code}")
def get_index_chart(code: str):
    try:
        return trading_service.get_index_chart(code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transaction-rankings")
def get_transaction_rankings():
    try:
        return trading_service.get_transaction_rankings()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search")
def search_stocks(q: str):
    try:
        return trading_service.find_stocks(q)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stock/{code}", response_model=Stock)
def get_stock(code: str):
    try:
        return trading_service.get_stock_detail(code)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/stock/{code}/hoga")
def get_hoga(code: str):
    try:
        return trading_service.get_order_book(code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stock/{code}/chart")
def get_stock_chart(code: str):
    try:
        return trading_service.get_stock_chart(code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/balance")
def get_balance():
    try:
        return trading_service.get_balance()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/order")
def create_order(order: Order):
    try:
        return trading_service.execute_order(
            order.stock_code, order.quantity, order.price, order.order_type, order.order_dvsn
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
