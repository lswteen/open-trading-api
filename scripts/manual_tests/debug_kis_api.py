import sys
import os
import pandas as pd

# Path hack
PROJ_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(PROJ_ROOT, 'kis_resources', 'examples_user'))
sys.path.append(os.path.join(PROJ_ROOT, 'kis_resources', 'examples_user', 'domestic_stock'))

import kis_auth as ka
from domestic_stock_functions import volume_rank, inquire_price

def debug_apis():
    ka.config_root = PROJ_ROOT
    ka.auth(svr="vps")
    
    print("--- Debugging volume_rank ---")
    df = volume_rank(
        fid_cond_mrkt_div_code="J", 
        fid_cond_scr_div_code="20171", 
        fid_input_iscd="0000", 
        fid_div_cls_code="0", 
        fid_blng_cls_code="0", 
        fid_trgt_cls_code="111111111", 
        fid_trgt_exls_cls_code="0000000000", 
        fid_input_price_1="", 
        fid_input_price_2="", 
        fid_vol_cnt="", 
        fid_input_date_1=""
    )
    if df is not None and not df.empty:
        print("Columns in volume_rank:", df.columns.tolist())
        print("First row:", df.iloc[0].to_dict())
    else:
        print("volume_rank response is empty")

    print("\n--- Debugging inquire_price for Stock ---")
    stock_df = inquire_price(env_dv="demo", fid_cond_mrkt_div_code="J", fid_input_iscd="005930")
    if not stock_df.empty:
        print("Stock 005930 price found:", stock_df['stck_prpr'].values[0])
    else:
        print("Stock 005930 price NOT found")

    print("\n--- Debugging inquire_price for Indices ---")
    kospi = inquire_price(env_dv="demo", fid_cond_mrkt_div_code="U", fid_input_iscd="0001")
    if not kospi.empty:
        print("KOSPI price found:", kospi['stck_prpr'].values[0])
    else:
        print("KOSPI NOT found")

if __name__ == "__main__":
    debug_apis()
