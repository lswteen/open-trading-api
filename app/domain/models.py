from pydantic import BaseModel
from typing import Optional

class Stock(BaseModel):
    code: str
    name: str
    price: float
    change_amount: float
    change_rate: float

class Order(BaseModel):
    stock_code: str
    quantity: int
    price: float
    order_type: str  # 'buy' or 'sell'
