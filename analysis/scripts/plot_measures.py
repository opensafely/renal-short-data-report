import pandas as pd
import numpy as np
from pathlib import Path
from utilities import *
from variables import tests

if not (OUTPUT_DIR / "figures").exists():
    Path.mkdir(OUTPUT_DIR / "figures")


for i in [
    "cr_cl",
    "creatinine",
    "eGFR",
    "albumin",
    "acr",
    "ckd",
    "ckd_primis_1_5",
]:
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

        if i in ["RRT", "dialysis", "kidney_tx", "ckd", "ckd_primis_1_5"]:
            demographics = []

        else:
            demographics = ["age_band", "sex", "imd", "region"]

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


# ckd by stage

df_ckd_stage = pd.read_csv(
    OUTPUT_DIR / f"joined/measure_ckd_primis_1_5_stage_population_rate.csv",
    parse_dates=["date"],
)
pop = df_ckd_stage.groupby(by=["date"])[["population"]].sum()

df_ckd_stage = df_ckd_stage.drop("population",axis=1)

df_ckd_stage = df_ckd_stage.merge(pop, on="date")


df_ckd_stage["rate"] = df_ckd_stage["ckd_primis_1_5"] / df_ckd_stage["population"]

df_ckd_stage = df_ckd_stage.drop(["value"], axis=1)

df_ckd_stage = df_ckd_stage.replace(np.inf, np.nan)


df_ckd_stage = redact_small_numbers(
    df_ckd_stage, 10,"ckd_primis_1_5", "population", "rate", "date"
)
df_ckd_stage["ckd_primis_stage"] = df_ckd_stage["ckd_primis_stage"].astype(str)

plot_measures(
    df=df_ckd_stage,
    filename=f"plot_ckd_stage",
    title=f"CKD stage",
    column_to_plot="rate",
    y_label="Proportion",
    as_bar=False,
    category="ckd_primis_stage",
)

for d in ["age_band", "ethnicity", "sex"]:
    df_ckd_stage = pd.read_csv(
        OUTPUT_DIR / f"joined/measure_ckd_primis_1_5_stage_population_{d}_rate.csv",
        parse_dates=["date"],
    )
    pop = df_ckd_stage.groupby(by=["date"])[["population"]].sum()

    df_ckd_stage = df_ckd_stage.drop("population",axis=1)

    df_ckd_stage = df_ckd_stage.merge(pop, on="date")


    df_ckd_stage["rate"] = df_ckd_stage["ckd_primis_1_5"] / df_ckd_stage["population"]


    df_ckd_stage = df_ckd_stage.drop(["value"], axis=1)

    df_ckd_stage = df_ckd_stage.replace(np.inf, np.nan)


    df_ckd_stage = redact_small_numbers(
        df_ckd_stage, 10,"ckd_primis_1_5", "population", "rate", "date"
    )

    df_ckd_stage["rate"] = df_ckd_stage["rate"]*100
    early_stage = df_ckd_stage.loc[df_ckd_stage["ckd_primis_stage"].isin([1, 2, 3]),:].groupby(["date", d])[["rate"]].mean().reset_index()
    late_stage = df_ckd_stage.loc[df_ckd_stage["ckd_primis_stage"].isin([4, 5]),:].groupby(["date", d])[["rate"]].mean().reset_index()

    plot_measures(
        df=early_stage,
        filename=f"plot_ckd_early_stage_{d}",
        title=f"Early stage CKD by {d}",
        column_to_plot="rate",
        y_label="Proportion",
        as_bar=False,
        category=d,
    )

    plot_measures(
        df=late_stage,
        filename=f"plot_ckd_late_stage_{d}",
        title=f"Late stage CKD by {d}",
        column_to_plot="rate",
        y_label="Proportion",
        as_bar=False,
        category=d,
    )


for test in tests:
    print(f"TEST: {test}")


    # single reduced egfr
    df = pd.read_csv(
        OUTPUT_DIR / f"joined/measure_{test}_single_egfr_population_rate.csv",
        parse_dates=["date"],
    )

    df = df.loc[df["single_egfr"]==1,:]
    redact_small_numbers(
        df, 10,test, "population", "value", "date"
    )
    
    plot_measures(
        df=df,
        filename=f"plot_single_reduced_egfr_{test}",
        title=f"",
        column_to_plot="value",
        y_label="Proportion",
        as_bar=False,
    )

    df_ckd_stage = pd.read_csv(
        OUTPUT_DIR / f"joined/measure_{test}_biochemical_stage_population_rate.csv",
        parse_dates=["date"],
    )
    
    
    df_ckd_stage_egfr = df_ckd_stage.groupby(by=["ckd_egfr_category", "date"])[[test, "population"]].sum().reset_index()
    df_ckd_stage_egfr["rate"] = (df_ckd_stage_egfr[test]/df_ckd_stage_egfr["population"]) * 100
    
    df_ckd_stage_egfr = df_ckd_stage_egfr.replace(np.inf, np.nan)
    df_ckd_stage_egfr = redact_small_numbers(
        df_ckd_stage_egfr, 10,test, "population", "rate", "date"
    )
   

    plot_measures(
        df=df_ckd_stage_egfr,
        filename=f"plot_ckd_biochemical_stage_{test}_egfr",
        title=f"",
        column_to_plot="rate",
        y_label="Proportion",
        as_bar=False,
        category="ckd_egfr_category",
    )


    df_ckd_stage_acr = df_ckd_stage.groupby(by=["ckd_acr_category", "date"])[[test, "population"]].sum().reset_index()
    df_ckd_stage_acr["rate"] = (df_ckd_stage_acr[test]/df_ckd_stage_acr["population"]) * 100
    
    # df_ckd_stage = df_ckd_stage.replace(np.inf, np.nan)
    df_ckd_stage_acr = redact_small_numbers(
        df_ckd_stage_acr, 10,test, "population", "rate", "date"
    )


    plot_measures(
        df=df_ckd_stage_acr,
        filename=f"plot_ckd_biochemical_stage_{test}_acr",
        title=f"",
        column_to_plot="rate",
        y_label="Proportion",
        as_bar=False,
        category="ckd_acr_category",
    )





