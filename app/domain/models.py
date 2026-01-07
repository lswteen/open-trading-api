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
    order_dvsn: str = "00" # '00': 지정가, '01': 시장가
