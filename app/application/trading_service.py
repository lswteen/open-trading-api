"""
Trading Service (Application Layer)

이 파일은 Spring Boot의 @Service 클래스에 해당합니다.
예: @Service public class TradingService

Application Layer는:
- 비즈니스 로직을 담당
- Domain의 Repository Interface에 의존 (구현체에 직접 의존 X)
- 의존성 주입(DI)을 통해 테스트 가능성 확보
"""
from app.domain.repositories.stock_repository import StockRepository
from app.domain.models import Stock
import time


class TradingService:
    """
    주식 거래 비즈니스 로직을 담당하는 서비스
    
    Spring Boot 비유:
    - @Service 클래스
    - Repository를 생성자 주입으로 받음 (@Autowired)
    - 캐싱 등의 부가 기능 제공
    """
    
    def __init__(self, stock_repository: StockRepository):
        """
        생성자 주입 (Constructor Injection)
        
        Args:
            stock_repository: StockRepository 인터페이스 구현체
            
        Spring Boot 비유:
        @Autowired
        public TradingService(StockRepository stockRepository) {
            this.stockRepository = stockRepository;
        }
        """
        self._repository = stock_repository
        self._cache = {}
        self._cache_ttl = 30  # 30 seconds
    
    def _get_cached_data(self, cache_key, fetch_func, *args, **kwargs):
        """
        캐싱 로직
        
        Note: 실제 프로덕션에서는 Redis 등 외부 캐시 사용 권장
        """
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
            if fresh_data is not None:
                if isinstance(fresh_data, (dict, list)) and not fresh_data:
                    if cached_entry: 
                        return cached_entry[0]
                
                self._cache[cache_key] = (fresh_data, now)
                return fresh_data
        except Exception as e:
            print(f"Cache refresh error for {cache_key}: {e}")
        
        # 3. Fallback to stale data
        if cached_entry:
            return cached_entry[0]
        return None
    
    def get_stock_detail(self, code: str) -> Stock:
        """
        종목 상세 정보 조회
        
        Repository를 통해 데이터를 가져오고 캐싱 적용
        """
        def fetch_stock_data(c):
            """Helper function to fetch and convert Stock to dict"""
            stock = self._repository.get_stock_price(c)
            if stock:
                # Pydantic model을 dict로 변환
                return stock.model_dump()
            return None
        
        data = self._get_cached_data(
            f"stock_detail_{code}", 
            fetch_stock_data,
            code
        )
        if not data:
            raise Exception("Stock not found")
        return Stock(**data)
    
    def get_order_book(self, code: str):
        """호가 정보 조회"""
        return self._get_cached_data(
            f"order_book_{code}", 
            self._repository.get_order_book, 
            code
        )
    
    def get_stock_chart(self, code: str):
        """차트 데이터 조회"""
        return self._get_cached_data(
            f"stock_chart_{code}", 
            self._repository.get_stock_chart, 
            code
        )
    
    def get_balance(self):
        """계좌 잔고 조회"""
        return self._repository.get_balance()
    
    def execute_order(self, code: str, qty: int, price: float, order_type: str, order_dvsn: str = "00"):
        """
        주문 실행
        
        Order 엔티티를 생성하여 Repository에 전달
        """
        from app.domain.models import Order
        
        order = Order(
            stock_code=code,
            quantity=qty,
            price=price,
            order_type=order_type,
            order_dvsn=order_dvsn
        )
        return self._repository.place_order(order)
    
    # 기존 메서드들 (kis_client 직접 호출하던 부분들)
    # 이들도 Repository 패턴으로 리팩토링 가능하지만, 
    # 우선 핵심 기능만 리팩토링하고 점진적으로 개선
    def get_market_indices(self):
        """시장 지수 조회 (TODO: Repository 패턴 적용)"""
        from app.infrastructure.kis_client import kis_client
        return self._get_cached_data("market_indices", kis_client.get_indices)
    
    def get_market_top_stocks(self, market: str = "J"):
        """거래대금 상위 종목 (TODO: Repository 패턴 적용)"""
        from app.infrastructure.kis_client import kis_client
        return self._get_cached_data(f"top_stocks_{market}", kis_client.get_top_stocks, market)
    
    def get_index_chart(self, code: str):
        """지수 차트 (TODO: Repository 패턴 적용)"""
        from app.infrastructure.kis_client import kis_client
        return self._get_cached_data(f"index_chart_{code}", kis_client.get_index_chart, code)
    
    def get_transaction_rankings(self):
        """거래 순위 (TODO: Repository 패턴 적용)"""
        from app.infrastructure.kis_client import kis_client
        return self._get_cached_data("transaction_rankings", kis_client.get_transaction_rankings)
    
    def find_stocks(self, query: str):
        """종목 검색 (TODO: Repository 패턴 적용)"""
        from app.infrastructure.kis_client import kis_client
        return kis_client.search_stock(query)


# 싱글톤 인스턴스 생성 (Spring의 @Bean과 유사)
# 실제 구현체를 주입
from app.infrastructure.persistence.kis_stock_repository import kis_stock_repository
trading_service = TradingService(stock_repository=kis_stock_repository)

