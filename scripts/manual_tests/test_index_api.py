import sys
import os
import pandas as pd
import time

# Path hack
PROJ_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(PROJ_ROOT, 'kis_resources', 'examples_user'))
sys.path.append(os.path.join(PROJ_ROOT, 'kis_resources', 'examples_user', 'domestic_stock'))

import kis_auth as ka
from domestic_stock_functions import inquire_index_price

def test_index_api():
    ka.config_root = PROJ_ROOT
    ka.auth(svr="vps")
    
    print("--- Testing inquire_index_price API (UPJONG) ---")
    
    targets = [
        {"code": "0001", "name": "KOSPI"},
        {"code": "1001", "name": "KOSDAQ"},
        {"code": "2001", "name": "KOSPI 200"}
    ]

    for target in targets:
        print(f"\nChecking {target['name']} ({target['code']})...")
        try:
            df = inquire_index_price(fid_cond_mrkt_div_code="U", fid_input_iscd=target['code'])
            if df is not None and not df.empty:
                print(f"SUCCESS: {target['name']}")
                print(f"Columns: {df.columns.tolist()}")
                if 'bstp_nmix_prpr' in df.columns:
                    print(f"Index Price: {df['bstp_nmix_prpr'].values[0]}")
                    print(f"Change: {df['bstp_nmix_prdy_vrss'].values[0]}")
                    print(f"Rate: {df['bstp_nmix_prdy_ctrt'].values[0]}")
            else:
                print(f"FAILED: {target['name']} (Empty Response)")
        except Exception as e:
            print(f"ERROR: {target['name']} - {str(e)}")
        time.sleep(1)

if __name__ == "__main__":
    test_index_api()
