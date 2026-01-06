import pytest
from app.domain.models import Stock

def test_stock_model_validation():
    # TDD: Model validation test
    stock_data = {
        "code": "005930",
        "name": "Samsung",
        "price": 70000.0,
        "change_amount": 500.0,
        "change_rate": 0.7
    }
    stock = Stock(**stock_data)
    assert stock.code == "005930"
    assert stock.price == 70000.0

def test_stock_model_invalid_data():
    # BDD like scenario check
    with pytest.raises(ValueError):
        # Missing required field 'price'
        Stock(code="005930", name="Samsung", change_amount=500.0, change_rate=0.7)
