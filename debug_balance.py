import sys
import os
import time
import pandas as pd

# Path hack
PROJ_ROOT = '/Users/milk/workspace/open-trading-api'
sys.path.append(os.path.join(PROJ_ROOT, 'examples_user'))
sys.path.append(os.path.join(PROJ_ROOT, 'examples_user', 'domestic_stock'))

import kis_auth as ka
from domestic_stock_functions import inquire_balance

ka.config_root = PROJ_ROOT
ka.auth(svr="vps")
trenv = ka.getTREnv()

print("Checking inquire_balance output2...")
df1, df2 = inquire_balance(
    env_dv="demo",
    cano=trenv.my_acct,
    acnt_prdt_cd=trenv.my_prod,
    afhr_flpr_yn="N",
    inqr_dvsn="02",
    unpr_dvsn="01",
    fund_sttl_icld_yn="N",
    fncg_amt_auto_rdpt_yn="N",
    prcs_dvsn="01"
)

if not df2.empty:
    print("Columns in output2:", df2.columns.tolist())
    # Print values for fields that might be balance
    search_terms = ['amt', 'dnca', 'psbl', 'csh']
    relevant_cols = [c for c in df2.columns if any(term in c.lower() for term in search_terms)]
    print("\nRelevant columns and values:")
    print(df2[relevant_cols].iloc[0].to_dict())
else:
    print("output2 is empty.")
