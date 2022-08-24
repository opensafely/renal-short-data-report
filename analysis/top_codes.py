import pandas as pd
from pathlib import Path
from utilities import create_top_5_code_table, write_csv, round_values
from variables import tests

codelist_dict = {
    "creatinine": "codelists/ukrr-creatinine-tests.csv",
    "cr_cl": "codelists/ukrr-creatinine-clearance-tests.csv",
    "albumin": "codelists/ukrr-albumin-tests.csv",
    "acr": "codelists/ukrr-albumincreatinine-ratio-acr-tests.csv",
    "eGFR": "codelists/ukrr-egfr-tests.csv"
}

for test in tests:
    code_df = pd.read_csv(f"output/{test}_codes_count.csv")
    codelist = pd.read_csv(codelist_dict[test])
    
    top_5_code_table = create_top_5_code_table(
        df=code_df,
        code_df=codelist,
        code_column="code",
        term_column="term",
        low_count_threshold=7,
        rounding_base=10,
    )
    write_csv(top_5_code_table,  Path(f"output/top_5_code_table_{test}.csv"), index=False)
