import sys
import os
import time
import pandas as pd

# Path hack
PROJ_ROOT = '/Users/milk/workspace/open-trading-api'
sys.path.append(os.path.join(PROJ_ROOT, 'examples_user'))
sys.path.append(os.path.join(PROJ_ROOT, 'examples_user', 'domestic_stock'))

import kis_auth as ka
from domestic_stock_functions import inquire_asking_price_exp_ccn

ka.config_root = PROJ_ROOT
ka.auth(svr="vps")

print("Checking inquire_asking_price_exp_ccn...")
df1, df2 = inquire_asking_price_exp_ccn(env_dv="demo", fid_cond_mrkt_div_code="J", fid_input_iscd="005930")
if not df1.empty:
    print("Columns in output1:", df1.columns.tolist())
    name_fields = [c for c in df1.columns if 'name' in c.lower() or 'nm' in c.lower() or 'isnm' in c.lower()]
    print("Possible name fields in output1:", name_fields)
    if name_fields:
        print("Values:", df1[name_fields].iloc[0].to_dict())

if not df2.empty:
    print("\nColumns in output2:", df2.columns.tolist())
    name_fields = [c for c in df2.columns if 'name' in c.lower() or 'nm' in c.lower() or 'isnm' in c.lower()]
    print("Possible name fields in output2:", name_fields)
    if name_fields:
        print("Values:", df2[name_fields].iloc[0].to_dict())
