import sys
import os
import pandas as pd
import time

# Path hack
PROJ_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(PROJ_ROOT, 'kis_resources', 'examples_user'))
sys.path.append(os.path.join(PROJ_ROOT, 'kis_resources', 'examples_user', 'domestic_stock'))

import kis_auth as ka
from domestic_stock_functions import inquire_price

def check_indices():
    ka.config_root = PROJ_ROOT
    ka.auth(svr="vps")
    
    print("--- Testing Index Retrieval (Demo Environment) ---")
    
    # KOSPI: market_div 'U', code '0001'
    # Alternate: market_div 'J', code '001' (sometimes sectors are under J)
    
    targets = [
        {"div": "U", "code": "0001", "name": "KOSPI (U)"},
        {"div": "U", "code": "1001", "name": "KOSDAQ (U)"},
        {"div": "J", "code": "001", "name": "KOSPI (J)"},
        {"div": "J", "code": "101", "name": "KOSDAQ (J)"}
    ]

    for target in targets:
        print(f"\nChecking {target['name']}...")
        try:
            df = inquire_price(
                env_dv="demo", 
                fid_cond_mrkt_div_code=target['div'], 
                fid_input_iscd=target['code']
            )
            if df is not None and not df.empty:
                print(f"SUCCESS: {target['name']}")
                print(f"Columns: {df.columns.tolist()}")
                if 'stck_prpr' in df.columns:
                    print(f"Price: {df['stck_prpr'].values[0]}")
            else:
                print(f"FAILED: {target['name']} (Empty Response)")
        except Exception as e:
            print(f"ERROR: {target['name']} - {str(e)}")
        time.sleep(1)

if __name__ == "__main__":
    check_indices()
