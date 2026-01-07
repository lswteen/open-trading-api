from app.infrastructure.kis_client import kis_client
from app.domain.models import Stock
import time

class TradingService:
    def __init__(self):
        self._cache = {}
        self._cache_ttl = 30  # 30 seconds

    def _get_cached_data(self, cache_key, fetch_func, *args, **kwargs):
        now = time.time()
        cached_entry = self._cache.get(cache_key)
        
        # 1. Return fresh from cache if within TTL
        if cached_entry:
            data, timestamp = cached_entry
            if now - timestamp < self._cache_ttl:
                return data
        
        # 2. Try to fetch fresh data
        try:
            fresh_data = fetch_func(*args, **kwargs)
            # Basic validation: ensure we don't cache completely empty/None results as 'good'
            # (Though some APIs might legitimately return empty lists, user said '정상일 경우만')
            if fresh_data is not None:
                if isinstance(fresh_data, (dict, list)) and not fresh_data:
                    # If empty but we have old data, return old data
                    if cached_entry: return cached_entry[0]
                
                self._cache[cache_key] = (fresh_data, now)
                return fresh_data
        except Exception as e:
            print(f"Cache refresh error for {cache_key}: {e}")

        # 3. Fallback to stale data if fresh fetch failed or returned nothing
        if cached_entry:
            return cached_entry[0]
        return None

    def get_market_indices(self):
        return self._get_cached_data("market_indices", kis_client.get_indices)

    def get_market_top_stocks(self, market: str = "J"):
        return self._get_cached_data(f"top_stocks_{market}", kis_client.get_top_stocks, market)

    def get_index_chart(self, code: str):
        return self._get_cached_data(f"index_chart_{code}", kis_client.get_index_chart, code)

    def get_transaction_rankings(self):
        return self._get_cached_data("transaction_rankings", kis_client.get_transaction_rankings)

    def find_stocks(self, query: str):
        return kis_client.search_stock(query)

    def get_stock_detail(self, code: str) -> Stock:
        # User wants detail view to be fast, so use cache (even if slightly stale)
        data = self._get_cached_data(f"stock_detail_{code}", kis_client.get_stock_price, code)
        if not data:
            raise Exception("Stock not found")
        return Stock(**data)

    def get_order_book(self, code: str):
        # Order book changes fast, so use a shorter TTL or just the global one? 
        # For now, stick to global but ensure stale fallback works.
        return self._get_cached_data(f"order_book_{code}", kis_client.get_order_book, code)

    def get_stock_chart(self, code: str):
        return self._get_cached_data(f"stock_chart_{code}", kis_client.get_stock_chart, code)

    def get_balance(self):
        return kis_client.get_balance()

    def execute_order(self, code: str, qty: int, price: float, order_type: str, order_dvsn: str = "00"):
        return kis_client.place_order(code, qty, price, order_type, order_dvsn)

trading_service = TradingService()
