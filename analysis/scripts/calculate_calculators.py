import pandas as pd
import numpy as np
from variables import tests
from utilities import (
    OUTPUT_DIR,
)

from utilities import cockcroft_gault, ckd_epi

df = pd.read_csv((OUTPUT_DIR) / "input_calculators.csv.gz", parse_dates=["weight_numeric_value_date", "creatinine_numeric_value_date"])

def apply_cg(row):

    cg = cockcroft_gault(row["sex"], row["age"], row["weight_numeric_value"], row["weight_numeric_value_date"],row["creatinine_numeric_value"], row["creatinine_numeric_value_date"], "2022-04-01")
    row["cg"] = cg
    return row
df = df.apply(apply_cg, axis=1)


def apply_ckd_epi(row):

    ckd = ckd_epi(row["sex"], row["age"],row["creatinine_numeric_value"], row["creatinine_numeric_value_date"], "2022-04-01")
    row["ckd_epi"] = ckd
    return row

df = df.apply(apply_ckd_epi, axis=1)
df.to_csv(OUTPUT_DIR / "input_calculators_calculated.csv.gz", index=False)



