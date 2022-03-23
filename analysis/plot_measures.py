import pandas as pd
import numpy as np
from pathlib import Path
from utilities import *

if not (OUTPUT_DIR / "figures").exists():
    Path.mkdir(OUTPUT_DIR / "figures")

demographics = ["age_band", "sex", "imd", "region"]

for i in ["cr_cl", "creatinine", "eGFR"]:
    for j in ["population", "at_risk"]:
        df = pd.read_csv(
            OUTPUT_DIR / f"joined/measure_{i}_{j}_rate.csv", parse_dates=["date"]
        )
        df = drop_irrelevant_practices(df)

        df["rate"] = df[f"value"] * 100

        df = df.drop(["value"], axis=1)
        df = df.replace(np.inf, np.nan)

        df_deciles = compute_redact_deciles(df, "date", i, "rate")

        deciles_chart(
            df,
            filename=f"output/figures/plot_{i}_{j}.jpeg",
            period_column="date",
            column="rate",
            count_column=i,
            ylabel="Percentage",
        )

        # demographic plots
        for d in demographics:

            df = pd.read_csv(
                OUTPUT_DIR / f"joined/measure_{i}_{d}_{j}_rate.csv",
                parse_dates=["date"],
            )

            if d == "sex":
                df = df[df["sex"].isin(["M", "F"])]

            elif d == "imd":
                df = df[df["imd"] != 0]

            elif d == "age_band":
                df = df[df["age_band"] != "missing"]

            elif d == "region":
                df = df[df["region"].notnull()]

            df["rate"] = df[f"value"] * 100

            df = redact_small_numbers(df, 10, i, j, "rate", "date")

            plot_measures(
                df=df,
                filename=f"plot_{i}_{d}_{j}",
                title=f"{i} by {d}",
                column_to_plot="rate",
                y_label="Proportion",
                as_bar=False,
                category=d,
            )
