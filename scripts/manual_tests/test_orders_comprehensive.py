"""
[주문 테스트 스크립트 실행 가이드]

1. 실행 방법:
   터미널에서 아래 명령어를 실행하세요:
   export PYTHONPATH=$(pwd)
   python scripts/manual_tests/test_orders_comprehensive.py

2. 테스트 내용:
   삼성전자(005930)를 대상으로 다음 주문 유형을 순차적으로 테스트합니다.
   - [구매/판매] 지정가 (Limit, 00)
   - [구매/판매] 시장가 (Market, 01)
   - [구매/판매] 장전 시간외 (Pre-Market, 05)
   - [구매/판매] 장후 시간외 (Post-Market, 06)
   - [구매/판매] 시간외 단일가 (Single Price, 07)

3. 예상 결과 (모의투자 환경 기준):
   - 지정가/시장가: 성공 (주문번호 반환)
   - 장전/장후 시간외: 실패 (모의투자 미지원 에러 발생 정상)
   - 시간외 단일가: 성공 (단, 거래시간/유동성에 따라 체결은 안 될 수 있음)
   
4. 주의사항:
   - "초당 거래건수를 초과하였습니다" 에러 발생 시, 스크립트의 time.sleep() 시간을 늘려주세요.
   - 판매 테스트는 계좌에 삼성전자 주식이 있어야 성공합니다.
"""
import sys
import os
import time
sys.path.insert(0, os.getcwd())
from app.infrastructure.kis_client import kis_client

STOCK_CODE = "005930" # Samsung Electronics

def run_order_test(description, order_type, order_dvsn, qty, price=0):
    print(f"\n--- {description} ---")
    print(f"Details: Type={order_type}, Dvsn={order_dvsn}, Qty={qty}, Price={price}")
    
    try:
        # Fetch current price first just to have a reference
        if price == 0 and order_dvsn in ["00", "07"]:
            # If price is needed but 0 provided, fetch current
            stock = kis_client.get_stock_price(STOCK_CODE)
            if stock:
                # For limit order, buy lower / sell higher if we don't want immediate fill?
                # But for testing SUCCESS of placement, we just want to send a valid price.
                price = int(stock['price'])
                print(f"Fetched current price: {price}")
        
        result = kis_client.place_order(STOCK_CODE, qty, price, order_type, order_dvsn)
        
        if "error" in result:
            print(f"FAILED: {result['error']}")
        else:
            # Check if API returned success or specific message
            # KIS API result usually has 'KRX_FWDG_ORD_ORGNO' (Order Number)
            oid = result.get('KRX_FWDG_ORD_ORGNO', 'Unknown')
            msg = result.get('msg1', 'Success')
            print(f"RESULT: {msg} (Order ID: {oid})")
            print(f"Full Response: {result}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    time.sleep(2) # Prevent rate limit

def test_orders():
    print(f"Starting Comprehensive Order Tests for {STOCK_CODE}")
    
    # --- BUY TESTS ---
    run_order_test("1. Buy Limit (00)", "buy", "00", 1) # Price will be auto-fetched
    run_order_test("2. Buy Market (01)", "buy", "01", 1, 0)
    run_order_test("3. Buy Pre-Market Overtime (05)", "buy", "05", 1, 0)
    run_order_test("4. Buy Post-Market Overtime (06)", "buy", "06", 1, 0)
    run_order_test("5. Buy Time-Specific Single Stock (07)", "buy", "07", 1)

    # --- SELL TESTS ---
    # Assuming we have enough holdings. 
    # Current balance check
    bal = kis_client.get_balance()
    holdings = {h['pdno']: int(h['hldg_qty']) for h in bal.get('holdings', [])}
    cur_qty = holdings.get(STOCK_CODE, 0)
    print(f"\nCurrent Holdings of {STOCK_CODE}: {cur_qty}")
    
    if cur_qty < 5:
        print("WARNING: Not enough holdings to test all sell types safely. Some might fail due to insufficient qty.")

    run_order_test("6. Sell Limit (00)", "sell", "00", 1)
    run_order_test("7. Sell Market (01)", "sell", "01", 1, 0)
    run_order_test("8. Sell Pre-Market Overtime (05)", "sell", "05", 1, 0)
    run_order_test("9. Sell Post-Market Overtime (06)", "sell", "06", 1, 0)
    run_order_test("10. Sell Time-Specific Single Stock (07)", "sell", "07", 1)

if __name__ == "__main__":
    test_orders()
