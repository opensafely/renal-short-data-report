import pandas as pd
from pathlib import Path
from utilities import write_csv,OUTPUT_DIR
from redaction_utils import create_top_5_code_table
from variables import tests

codelist_dict = {
    "creatinine": "codelists/ukrr-creatinine-tests.csv",
    "cr_cl": "codelists/ukrr-creatinine-clearance-tests.csv",
    "albumin": "codelists/ukrr-albumin-tests.csv",
    "acr": "codelists/ukrr-albumincreatinine-ratio-acr-tests.csv",
    "eGFR": "codelists/ukrr-egfr-tests.csv"
}

codelist_dict_numeric = {
    "creatinine": "codelists/ukrr-creatinine-tests-level.csv",
    "cr_cl": "codelists/ukrr-creatinine-clearance-tests-level.csv",
    "albumin": "codelists/ukrr-albumin-tests-level.csv",
    "acr": "codelists/ukrr-albumincreatinine-ratio-acr-tests-level.csv",
    "eGFR": "codelists/ukrr-egfr-tests-level.csv"
}

for test in tests:
    code_df = pd.read_csv(f"output/{test}_codes_count.csv")
    codelist = pd.read_csv(codelist_dict[test])
    
    code_df["code"] = code_df["code"].astype(int).astype(str)
    top_5_code_table = create_top_5_code_table(
        df=code_df,
        code_df=codelist,
        code_column="code",
        term_column="term",
        low_count_threshold=7,
        rounding_base=5,
    )
    write_csv(top_5_code_table,  OUTPUT_DIR / f"top_5_code_table_{test}.csv", index=False)


    code_df_numeric = pd.read_csv(f"output/{test}_numeric_value_count.csv")
    codelist_numeric = pd.read_csv(codelist_dict_numeric[test])

    if test != "albumin":
        code_df_numeric.loc["code"] = code_df_numeric["code"].astype(int).astype(str)
    
    top_5_code_table_numeric = create_top_5_code_table(
        df=code_df_numeric,
        code_df=codelist_numeric,
        code_column="code",
        term_column="term",
        low_count_threshold=7,
        rounding_base=5,
    )
    write_csv(top_5_code_table_numeric,  OUTPUT_DIR / f"top_5_code_table_numeric_{test}.csv", index=False)