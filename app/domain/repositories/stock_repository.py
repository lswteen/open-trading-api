"""
Stock Repository Interface (Domain Layer)

이 파일은 Spring Boot의 Repository Interface에 해당합니다.
예: public interface StockRepository extends JpaRepository<Stock, String>

Domain Layer는 Infrastructure에 의존하지 않습니다.
구체적인 구현(KIS API 호출)은 Infrastructure Layer에서 담당합니다.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from app.domain.models import Stock, Order


class StockRepository(ABC):
    """
    주식 데이터 접근을 위한 Repository Interface
    
    Spring Boot 비유:
    - @Repository 인터페이스
    - 실제 구현체는 Infrastructure Layer에 위치
    """
    
    @abstractmethod
    def get_stock_price(self, code: str) -> Optional[Stock]:
        """
        종목 현재가 조회
        
        Args:
            code: 종목코드 (예: "005930")
            
        Returns:
            Stock 엔티티 또는 None
        """
        pass
    
    @abstractmethod
    def get_order_book(self, code: str) -> Dict:
        """
        호가 정보 조회
        
        Args:
            code: 종목코드
            
        Returns:
            호가 데이터 (asks, bids)
        """
        pass
    
    @abstractmethod
    def get_stock_chart(self, code: str) -> List[Dict]:
        """
        차트 데이터 조회
        
        Args:
            code: 종목코드
            
        Returns:
            시계열 차트 데이터
        """
        pass
    
    @abstractmethod
    def place_order(self, order: Order) -> Dict:
        """
        주문 실행
        
        Args:
            order: 주문 엔티티
            
        Returns:
            주문 결과
        """
        pass
    
    @abstractmethod
    def get_balance(self) -> Dict:
        """
        계좌 잔고 조회
        
        Returns:
            잔고 정보
        """
        pass
