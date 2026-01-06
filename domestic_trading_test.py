import sys
import os
import logging
import time
import pandas as pd

# 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
functions_path = os.path.join(current_dir, 'examples_user', 'domestic_stock')
sys.path.append(functions_path)
sys.path.append(os.path.join(current_dir, 'examples_user'))

import kis_auth as ka
from domestic_stock_functions import *

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_trading_test():
    # 1. 인증 (모의투자)
    logger.info("Step 1: Authenticating (Paper Trading)...")
    ka.auth(svr="vps")
    trenv = ka.getTREnv()
    time.sleep(1) # 대역폭 제한회피

    # 2. 종목 및 현재가 조회
    target_stock_code = "005930" # 삼성전자
    logger.info(f"Step 2: Fetching Price for {target_stock_code}")
    
    price_data = inquire_price(env_dv="demo", fid_cond_mrkt_div_code="J", fid_input_iscd=target_stock_code)
    
    if not price_data.empty:
        current_price = int(price_data['stck_prpr'].values[0])
        print("\n--- [종목 시세 정보] ---")
        print(f"종목코드: {target_stock_code}")
        print(f"현재가: {current_price}원")
        print(f"전일대비: {price_data['prdy_vrss'].values[0]}원 ({price_data['prdy_ctrt'].values[0]}%)")
    else:
        logger.error("Failed to fetch price data.")
        return

    time.sleep(1)

    # 3. 주식 주문 (매수 테스트)
    # 실제 주문을 실행하려면 아래 False를 True로 변경하세요
    test_buy = False 
    if test_buy:
        logger.info(f"Step 3: Executing Buy Order (Cash) for {target_stock_code} - 1 share")
        # 지정가(00)로 현재가 1주 매수 주문
        buy_res = order_cash(
            env_dv="demo",
            ord_dv="buy",
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            pdno=target_stock_code,
            ord_dvsn="00", # 지정가
            ord_qty="1",
            ord_unpr=str(current_price),
            excg_id_dvsn_cd="KRX"
        )
        if not buy_res.empty:
            print("\n--- [매수 주문 결과] ---")
            print(buy_res)
    else:
        print("\n[알림] Step 3: 매수 주문 영역입니다. 실제 주문을 넣으려면 코드에서 test_buy = True 로 변경해 주세요.")

    time.sleep(1)

    # 4. 잔고 조회
    logger.info("Step 4: Fetching Account Balance")
    balance1, balance2 = inquire_balance(
        env_dv="demo",
        cano=trenv.my_acct,
        acnt_prdt_cd=trenv.my_prod,
        afhr_flpr_yn="N",
        inqr_dvsn="02", # 종목별
        unpr_dvsn="01",
        fund_sttl_icld_yn="N",
        fncg_amt_auto_rdpt_yn="N",
        prcs_dvsn="00"
    )
    
    print("\n--- [계좌 잔고 현황] ---")
    if balance1 is not None and not balance1.empty:
        # 보유 종목 리스트 출력
        cols = ['pdno', 'prdt_name', 'hldg_qty', 'pchs_avg_pric', 'stck_prpr', 'evlu_pfls_amt']
        available_cols = [c for c in cols if c in balance1.columns]
        print(balance1[available_cols])
    else:
        print("현재 보유 중인 종목이 없습니다.")

    if balance2 is not None and not balance2.empty:
        print("\n--- [총 자산 요약] ---")
        print(f"총 평가 금액: {balance2['tot_evlu_amt'].values[0]}원")
        print(f"주문 가능 금액: {balance2['dnca_tot_amt'].values[0]}원")

if __name__ == "__main__":
    run_trading_test()
