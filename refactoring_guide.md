# 리팩토링 가이드 - Spring Boot 개발자를 위한 Python DDD 아키텍처

## 개요
이 문서는 Java/Spring Boot 개발자가 Python FastAPI 프로젝트의 DDD(Domain-Driven Design) 구조를 이해할 수 있도록 작성되었습니다.

## 1. 전체 아키텍처 비교

### Spring Boot (Layered Architecture)
```
src/main/java/com/example/trading/
├── domain/
│   ├── model/          # Entity, VO
│   └── repository/     # Repository Interface
├── infrastructure/
│   └── persistence/    # Repository Impl (JPA)
├── application/
│   └── service/        # @Service
└── interfaces/
    └── api/            # @RestController
```

### Python FastAPI (DDD Architecture)
```
app/
├── domain/             # 핵심 비즈니스 로직 (외부 의존성 없음)
│   ├── models/         # Entity, DTO (Pydantic)
│   └── repositories/   # Repository Interface (ABC)
├── infrastructure/     # 외부 시스템 연동
│   └── persistence/    # Repository 구현체
├── application/        # 비즈니스 로직
│   └── services/       # Service 클래스
└── interfaces/
    └── api/            # FastAPI Router (Controller)
```

## 2. 계층별 상세 설명

### 2.1 Domain Layer (도메인 계층)

#### Spring Boot
```java
// Entity
@Entity
public class Stock {
    @Id
    private String code;
    private String name;
    private Double price;
}

// Repository Interface
public interface StockRepository extends JpaRepository<Stock, String> {
    Optional<Stock> findByCode(String code);
}
```

#### Python (현재 프로젝트)
```python
# app/domain/models.py
from pydantic import BaseModel

class Stock(BaseModel):
    code: str
    name: str
    price: float
    # Pydantic은 자동으로 validation 제공

# app/domain/repositories/stock_repository.py
from abc import ABC, abstractmethod

class StockRepository(ABC):
    @abstractmethod
    def get_stock_price(self, code: str) -> Optional[Stock]:
        pass
```

**핵심 개념:**
- `Pydantic BaseModel` = JPA `@Entity` + DTO
- `ABC (Abstract Base Class)` = Java `interface`
- Domain Layer는 **순수한 비즈니스 로직**만 포함 (외부 의존성 X)

---

### 2.2 Infrastructure Layer (인프라 계층)

#### Spring Boot
```java
@Repository
public class StockRepositoryImpl implements StockRepository {
    @Autowired
    private RestTemplate restTemplate;
    
    @Override
    public Optional<Stock> findByCode(String code) {
        // 외부 API 호출
        return restTemplate.getForObject(...);
    }
}
```

#### Python (현재 프로젝트)
```python
# app/infrastructure/persistence/kis_stock_repository.py
from app.domain.repositories.stock_repository import StockRepository

class KisStockRepository(StockRepository):
    def __init__(self):
        self._client = kis_client  # 외부 API 클라이언트
    
    def get_stock_price(self, code: str) -> Optional[Stock]:
        data = self._client.get_stock_price(code)
        return Stock(**data)
```

**핵심 개념:**
- Infrastructure는 Domain의 **인터페이스를 구현**
- 외부 시스템(KIS API, DB 등)과의 실제 통신 담당
- `@Repository` 역할

---

### 2.3 Application Layer (응용 계층)

#### Spring Boot
```java
@Service
public class TradingService {
    @Autowired
    private StockRepository stockRepository;
    
    public Stock getStockDetail(String code) {
        return stockRepository.findByCode(code)
            .orElseThrow(() -> new NotFoundException());
    }
}
```

#### Python (현재 프로젝트)
```python
# app/application/trading_service.py
class TradingService:
    def __init__(self, stock_repository: StockRepository):
        self._repository = stock_repository  # DI
    
    def get_stock_detail(self, code: str) -> Stock:
        stock = self._repository.get_stock_price(code)
        if not stock:
            raise Exception("Stock not found")
        return stock
```

**핵심 개념:**
- **생성자 주입(Constructor Injection)** 사용
- Repository **인터페이스**에 의존 (구현체에 직접 의존 X)
- `@Service` 역할
- 테스트 시 Mock Repository 주입 가능

---

### 2.4 Interface Layer (인터페이스 계층)

#### Spring Boot
```java
@RestController
@RequestMapping("/api/v1")
public class StockController {
    @Autowired
    private TradingService tradingService;
    
    @GetMapping("/stock/{code}")
    public Stock getStock(@PathVariable String code) {
        return tradingService.getStockDetail(code);
    }
}
```

#### Python (현재 프로젝트)
```python
# app/api/v1/endpoints.py (또는 app/interfaces/api/)
from fastapi import APIRouter
from app.application.trading_service import trading_service

router = APIRouter()

@router.get("/stock/{code}")
def get_stock(code: str):
    return trading_service.get_stock_detail(code)
```

**핵심 개념:**
- `APIRouter` = `@RestController`
- FastAPI는 자동으로 OpenAPI 문서 생성 (Swagger)
- Service Layer를 호출하여 비즈니스 로직 실행

---

## 3. 의존성 주입 (Dependency Injection)

### Spring Boot
```java
@Configuration
public class AppConfig {
    @Bean
    public StockRepository stockRepository() {
        return new KisStockRepository();
    }
    
    @Bean
    public TradingService tradingService(StockRepository repo) {
        return new TradingService(repo);
    }
}
```

### Python (현재 프로젝트)
```python
# app/application/trading_service.py (하단)
from app.infrastructure.persistence.kis_stock_repository import kis_stock_repository

# 싱글톤 인스턴스 생성
trading_service = TradingService(stock_repository=kis_stock_repository)
```

**핵심 개념:**
- Python은 Spring의 `@Autowired` 대신 **명시적 생성자 주입** 사용
- 싱글톤 패턴으로 인스턴스 관리
- 테스트 시 다른 구현체 주입 가능

---

## 4. 테스트 (TDD/BDD)

### Spring Boot
```java
@SpringBootTest
public class TradingServiceTest {
    @MockBean
    private StockRepository stockRepository;
    
    @Autowired
    private TradingService tradingService;
    
    @Test
    public void testGetStockDetail() {
        // Given
        Stock mock = new Stock("005930", "삼성전자", 70000.0);
        when(stockRepository.findByCode("005930"))
            .thenReturn(Optional.of(mock));
        
        // When
        Stock result = tradingService.getStockDetail("005930");
        
        // Then
        assertEquals("삼성전자", result.getName());
    }
}
```

### Python (현재 프로젝트)
```python
# tests/test_trading_service.py
import pytest
from app.application.trading_service import TradingService

class MockStockRepository(StockRepository):
    def get_stock_price(self, code: str):
        return Stock(code="005930", name="삼성전자", price=70000.0, ...)

def test_get_stock_detail():
    # Given
    mock_repo = MockStockRepository()
    service = TradingService(stock_repository=mock_repo)
    
    # When
    result = service.get_stock_detail("005930")
    
    # Then
    assert result.name == "삼성전자"
```

**핵심 개념:**
- `pytest` = JUnit
- Mock 클래스 직접 구현 (또는 `unittest.mock` 사용)
- Given-When-Then 패턴 동일

---

## 5. 디자인 패턴 적용

### 5.1 Repository Pattern
- **목적**: 데이터 접근 로직을 캡슐화
- **구현**: `StockRepository` 인터페이스 + `KisStockRepository` 구현체
- **장점**: 외부 API를 DB로 교체해도 Service 코드 변경 불필요

### 5.2 Dependency Injection
- **목적**: 느슨한 결합(Loose Coupling)
- **구현**: 생성자를 통한 인터페이스 주입
- **장점**: 테스트 용이성, 유연성

### 5.3 Singleton Pattern
- **목적**: 전역 인스턴스 관리
- **구현**: 모듈 레벨에서 인스턴스 생성
- **장점**: Spring의 `@Bean`과 유사한 효과

---

## 6. Root 디렉토리 스크립트 설명

### 이전 구조 (혼란스러움)
```
open-trading-api/
├── debug_balance.py      # 잔고 조회 테스트
├── debug_price.py        # 가격 조회 테스트
├── check_indices.py      # 지수 조회 테스트
└── domestic_trading_test.py  # 주문 테스트
```

### 현재 구조 (정리됨)
```
open-trading-api/
├── scripts/
│   └── manual_tests/     # 수동 테스트 스크립트 모음
│       ├── debug_balance.py
│       ├── debug_price.py
│       ├── check_indices.py
│       └── domestic_trading_test.py
├── app/                  # 실제 구현 코드
└── tests/                # 자동화된 단위 테스트
```

**스크립트 실행 방법:**
```bash
# 잔고 조회 테스트
python scripts/manual_tests/debug_balance.py

# 가격 조회 테스트
python scripts/manual_tests/debug_price.py
```

---

## 7. 점진적 리팩토링 전략

현재 프로젝트는 **핵심 기능(주문, 조회)만 리팩토링**되었습니다.
나머지 기능은 점진적으로 개선할 수 있습니다.

### 완료된 리팩토링
- ✅ `get_stock_detail()` - Repository 패턴 적용
- ✅ `get_order_book()` - Repository 패턴 적용
- ✅ `execute_order()` - Repository 패턴 적용
- ✅ 단위 테스트 작성

### TODO (향후 개선)
- ⏳ `get_market_indices()` - MarketRepository 생성
- ⏳ `get_transaction_rankings()` - MarketRepository 생성
- ⏳ 통합 테스트 추가
- ⏳ Redis 캐싱 적용

---

## 8. 주요 차이점 요약

| 항목 | Spring Boot | Python FastAPI |
|------|-------------|----------------|
| **DI 컨테이너** | `@Autowired`, `@Bean` | 명시적 생성자 주입 |
| **인터페이스** | `interface` | `ABC` (Abstract Base Class) |
| **Entity** | JPA `@Entity` | Pydantic `BaseModel` |
| **테스트** | JUnit, Mockito | pytest, unittest.mock |
| **문서화** | Swagger (수동 설정) | OpenAPI (자동 생성) |

---

## 9. 참고 자료

- **DDD**: Eric Evans - Domain-Driven Design
- **Clean Architecture**: Robert C. Martin
- **Python Type Hints**: [PEP 484](https://peps.python.org/pep-0484/)
- **FastAPI 공식 문서**: https://fastapi.tiangolo.com/
- **pytest 공식 문서**: https://docs.pytest.org/
