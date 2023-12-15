import pandas as pd
from pathlib import Path
from utilities import *

Path.mkdir(OUTPUT_DIR / "pub/deciles", parents=True, exist_ok=True)

# 1. for each test, plot deciles charts in total population and at risk population
for i in [
    "creatinine",
    "eGFR",
    "albumin",
    "acr",
    "cr_cl",
]:
    for j in ["population", "at_risk"]:
        df = pd.read_csv(
            OUTPUT_DIR / f"joined/measure_{i}_{j}_rate.csv", parse_dates=["date"]
        )

        total_practices = len(df["practice"].unique())

        df = drop_irrelevant_practices(df)

        practices_included = len(df["practice"].unique())

        table = pd.DataFrame(
            {
                "total_practices": [total_practices],
                "practices_included": [practices_included],
            }
        )
        table.to_csv(OUTPUT_DIR / f"pub/deciles/num_practices_{i}_{j}.csv", index=False)
