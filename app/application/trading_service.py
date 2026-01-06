from app.infrastructure.kis_client import kis_client
from app.domain.models import Stock

class TradingService:
    def get_stock_detail(self, code: str) -> Stock:
        data = kis_client.get_stock_price(code)
        if not data:
            raise Exception("Stock not found")
        return Stock(**data)

    def execute_order(self, code: str, qty: int, price: float, order_type: str):
        return kis_client.place_order(code, qty, price, order_type)

trading_service = TradingService()
