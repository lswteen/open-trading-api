"""
TradingService 단위 테스트 (TDD/BDD)

이 파일은 Spring Boot의 @SpringBootTest 또는 단위 테스트에 해당합니다.
예: @Test public void testGetStockDetail()

TDD/BDD 원칙:
- Mock을 사용하여 외부 의존성 격리
- 비즈니스 로직만 테스트
- Given-When-Then 패턴 사용
"""
import pytest
from unittest.mock import Mock
from app.application.trading_service import TradingService
from app.domain.models import Stock, Order
from app.domain.repositories.stock_repository import StockRepository


class MockStockRepository(StockRepository):
    """
    테스트용 Mock Repository
    
    Spring Boot 비유:
    @MockBean
    private StockRepository stockRepository;
    """
    
    def __init__(self):
        self.mock_data = {}
    
    def get_stock_price(self, code: str):
        """Mock 데이터 반환"""
        if code in self.mock_data:
            return Stock(**self.mock_data[code])
        return None
    
    def get_order_book(self, code: str):
        return {"asks": [], "bids": []}
    
    def get_stock_chart(self, code: str):
        return []
    
    def place_order(self, order: Order):
        return {"success": True, "order_id": "12345"}
    
    def get_balance(self):
        return {"cash": 1000000}


class TestTradingService:
    """
    TradingService 테스트 클래스
    
    Spring Boot 비유:
    @SpringBootTest
    public class TradingServiceTest
    """
    
    def setup_method(self):
        """
        각 테스트 전에 실행되는 설정
        
        Spring Boot 비유:
        @BeforeEach
        public void setup()
        """
        self.mock_repo = MockStockRepository()
        self.service = TradingService(stock_repository=self.mock_repo)
    
    def test_get_stock_detail_success(self):
        """
        Given: 종목 코드 "005930"에 대한 Mock 데이터가 있을 때
        When: get_stock_detail을 호출하면
        Then: Stock 엔티티가 반환되어야 함
        
        Spring Boot 비유:
        @Test
        public void testGetStockDetailSuccess()
        """
        # Given
        self.mock_repo.mock_data["005930"] = {
            "code": "005930",
            "name": "삼성전자",
            "price": 70000.0,
            "change_amount": 1000.0,
            "change_rate": 1.45,
            "overtime_price": 0.0,
            "overtime_change": 0.0,
            "overtime_rate": 0.0
        }
        
        # When
        result = self.service.get_stock_detail("005930")
        
        # Then
        assert result is not None
        assert result.code == "005930"
        assert result.name == "삼성전자"
        assert result.price == 70000.0
    
    def test_get_stock_detail_not_found(self):
        """
        Given: 존재하지 않는 종목 코드일 때
        When: get_stock_detail을 호출하면
        Then: Exception이 발생해야 함
        """
        # Given: mock_data에 아무것도 없음
        
        # When & Then
        with pytest.raises(Exception, match="Stock not found"):
            self.service.get_stock_detail("999999")
    
    def test_execute_order(self):
        """
        Given: 주문 정보가 주어졌을 때
        When: execute_order를 호출하면
        Then: Repository의 place_order가 호출되고 결과가 반환되어야 함
        """
        # When
        result = self.service.execute_order(
            code="005930",
            qty=10,
            price=70000.0,
            order_type="buy",
            order_dvsn="00"
        )
        
        # Then
        assert result["success"] is True
        assert "order_id" in result
    
    def test_caching_behavior(self):
        """
        Given: 동일한 종목을 두 번 조회할 때
        When: 첫 번째 조회 후 Mock 데이터를 변경하고 다시 조회하면
        Then: 캐시된 데이터가 반환되어야 함 (TTL 내)
        """
        # Given
        self.mock_repo.mock_data["005930"] = {
            "code": "005930",
            "name": "삼성전자",
            "price": 70000.0,
            "change_amount": 1000.0,
            "change_rate": 1.45,
            "overtime_price": 0.0,
            "overtime_change": 0.0,
            "overtime_rate": 0.0
        }
        
        # When
        first_result = self.service.get_stock_detail("005930")
        
        # Mock 데이터 변경
        self.mock_repo.mock_data["005930"]["price"] = 80000.0
        
        second_result = self.service.get_stock_detail("005930")
        
        # Then: 캐시로 인해 첫 번째 가격이 유지됨
        assert first_result.price == 70000.0
        assert second_result.price == 70000.0  # 캐시된 값


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
