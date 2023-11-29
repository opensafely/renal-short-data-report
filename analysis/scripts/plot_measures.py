import pandas as pd
import numpy as np
from pathlib import Path
from utilities import *
from redaction_utils import compute_deciles, redact_small_numbers
from variables import tests_extended
import matplotlib.dates as mdates


Path.mkdir(OUTPUT_DIR / "pub.deciles", parents=True, exist_ok=True)
Path.mkdir(OUTPUT_DIR / "pub/deciles/data", parents=True, exist_ok=True)
Path.mkdir(OUTPUT_DIR / "pub/deciles/figures", parents=True, exist_ok=True)
Path.mkdir(OUTPUT_DIR / "pub/tests_by_ckd_stage", parents=True, exist_ok=True)
Path.mkdir(OUTPUT_DIR / "pub/ukrr_testing", parents=True, exist_ok=True)

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

        df = drop_irrelevant_practices(df)

        dfs = {}

        dfs["all"] = df

        for k, df in dfs.items():

            df = df.drop(["value"], axis=1)
            df = df.replace(np.inf, np.nan)

            df_deciles = compute_deciles(df, "date", i)

            df_deciles.to_csv(
                f"output/pub/deciles/data/plot_{i}_{j}_{k}_deciles.csv", index=False
            )

            deciles_chart(
                df,
                filename=f"output/pub/deciles/figures/plot_{i}_{j}_{k}.jpeg",
                period_column="date",
                column="value",
                count_column=i,
                ylabel="Proportion",
            )


# 2. ckd by stage

df_ckd_stage = pd.read_csv(
    OUTPUT_DIR / "joined/input_2023-07-01.csv.gz",
    usecols=[
        "ckd_primis_1_5",
        "ckd_primis_stage",
    ],
)

df_ckd_stage = df_ckd_stage.loc[df_ckd_stage["ckd_primis_1_5"] == 1, :]

ckd_stage  = df_ckd_stage["ckd_primis_stage"]

ckd_stage_count = ckd_stage.value_counts()
ckd_stage_count.rename("count", inplace=True)

ckd_stage_count = ckd_stage_count.apply(lambda x: round(x / 5) * 5)

ckd_proportion = ckd_stage_count / ckd_stage_count.sum()
ckd_proportion.rename("proportion", inplace=True)


df_ckd_stage = pd.concat([ckd_stage_count, ckd_proportion], axis=1)
df_ckd_stage = df_ckd_stage.reset_index()
df_ckd_stage.rename(columns={"index": "ckd_primis_stage"}, inplace=True)

Path.mkdir(OUTPUT_DIR / "pub/ckd_stage", parents=True, exist_ok=True)

df_ckd_stage.to_csv(OUTPUT_DIR / f"pub/ckd_stage/plot_ckd_stage.csv", index=False)

plt.figure(figsize=(12, 8))
plt.bar(df_ckd_stage["ckd_primis_stage"], df_ckd_stage["proportion"] * 100)
plt.xlabel("CKD stage (recorded)")
plt.ylabel("Proportion")
plt.title("CKD stage")
plt.tight_layout()
plt.savefig(f"output/pub/ckd_stage/plot_ckd_stage.jpeg")


# 3. testing rate by ckd stage
for test in tests_extended:
    print(f"TEST: {test}")

    # single reduced egfr
    df = pd.read_csv(
        OUTPUT_DIR / f"joined/measure_{test}_single_egfr_population_rate.csv",
        parse_dates=["date"],
    )
    
    df = df.loc[df["single_egfr"] == 1, :]
    redact_small_numbers(df, 7, 5, test, "population", "value", "date")

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

    df_ckd_stage_egfr = (
        df_ckd_stage.groupby(by=["ckd_egfr_category", "date"])[[test, "population"]]
        .sum()
        .reset_index()
    )
   
    df_ckd_stage_egfr = df_ckd_stage_egfr.replace(np.inf, np.nan)
    df_ckd_stage_egfr = redact_small_numbers(
        df_ckd_stage_egfr, 7, 5, test, "population", "value", "date"
    )

    plot_measures(
        df=df_ckd_stage_egfr,
        filename=f"pub/tests_by_ckd_stage/plot_ckd_biochemical_stage_{test}_egfr",
        title=f"",
        column_to_plot="value",
        y_label="Proportion",
        as_bar=False,
        category="ckd_egfr_category",
    )

    df_ckd_stage_acr = (
        df_ckd_stage.groupby(by=["ckd_acr_category", "date"])[[test, "population"]]
        .sum()
        .reset_index()
    )
  

    # df_ckd_stage = df_ckd_stage.replace(np.inf, np.nan)
    df_ckd_stage_acr = redact_small_numbers(
        df_ckd_stage_acr, 7, 5, test, "population", "value", "date"
    )

    plot_measures(
        df=df_ckd_stage_acr,
        filename=f"plot_ckd_biochemical_stage_{test}_acr",
        title=f"",
        column_to_plot="value",
        y_label="Proportion",
        as_bar=False,
        category="ckd_acr_category",
    )


    df_recorded_stage = pd.read_csv(
        OUTPUT_DIR / f"joined/measure_{test}_stage_population_rate.csv",
        parse_dates=["date"],
    )


    df_recorded_stage = df_recorded_stage.replace(np.inf, np.nan)
    df_recorded_stage = redact_small_numbers(
        df_recorded_stage, 7, 5, test, "population", "value", "date")
    
    plot_measures(
        df=df_recorded_stage,
        filename=f"pub/tests_by_ckd_stage/plot_ckd_recorded_stage_{test}",
        title=f"",
        column_to_plot="value",
        y_label="Proportion",
        as_bar=False,
        category="ckd_primis_stage",
    )

   

# 4. plot rate of each test fop those biochem stage 3-5, vs primis recorded 3-5 vs single reduced egfr

for test in tests_extended:
    single_egfr = pd.read_csv(
        OUTPUT_DIR / f"joined/measure_{test}_single_egfr_population_rate.csv",
        parse_dates=["date"],
    )
    single_egfr = single_egfr.loc[single_egfr["single_egfr"] == 1, :]
    single_egfr = single_egfr.drop(
        [
            "single_egfr",
        ],
        axis=1,
    )

    primis_stage = pd.read_csv(
        OUTPUT_DIR / f"joined/measure_{test}_stage_population_rate.csv",
        parse_dates=["date"],
    )
    primis_stage = primis_stage.loc[primis_stage["ckd_primis_stage"].isin([3, 4, 5]), :]
    primis_stage = (
        primis_stage.groupby(by=["date"])[[test, "population"]].sum().reset_index()
    )
    primis_stage["value"] = primis_stage[test] / primis_stage["population"]

    ckd_stage = pd.read_csv(
        OUTPUT_DIR / f"joined/measure_{test}_biochemical_stage_population_rate.csv",
        parse_dates=["date"],
    )
    ckd_stage = ckd_stage.loc[
        ckd_stage["ckd_egfr_category"].isin(["G3a", "G3b", "G4", "G5"]), :
    ]
    ckd_stage = ckd_stage.groupby(by=["date"])[[test, "population"]].sum().reset_index()
    ckd_stage["value"] = ckd_stage[test] / ckd_stage["population"]

    # now plot on the same axis
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(
        single_egfr["date"],
        single_egfr["value"],
        label="Single reduced eGFR",
        color="red",
    )
    ax.plot(
        primis_stage["date"],
        primis_stage["value"],
        label="CKD stage (recorded)",
        color="blue",
    )
    ax.plot(
        ckd_stage["date"],
        ckd_stage["value"],
        label="CKD stage (biochemical)",
        color="green",
    )

    x_labels = sorted(single_egfr["date"])

    ax.set_xticks(x_labels)
    ax.set_xticklabels(x_labels, rotation="vertical")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.set_ylabel("Proportion")
    ax.set_xlabel("Date")
    ax.margins(x=0)
    ax.grid(True)

    ax.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(f"output/pub/tests_by_ckd_stage/plot_{test}_single_biochem_stage.jpeg")
    plt.close()

# 5.  plot rate of testing in those at risk in the general pop not in UKRR vs those that are in UKRR


# # 2019_prevalence a prevalence cohort of patients alive and on RRT in December 2019
# # 2020_prevalence a prevalence cohort of patients alive and on RRT in December 2020
# # 2021_prevalence a prevalence cohort of patients alive and on RRT in December 2021
# # 2020_incidence an incidence cohort of patients who started RRT in 2020
# # 2020_ckd a snapshot prevalence cohort of patient with Stage 4 or 5 CKD who were reported to the UKRR to be under renal care in December 2020


measures = {}

for path in Path("output/joined").glob("input_20*.csv.gz"):
    df = pd.read_csv(path)
    date = get_date_input_file(path.name)

    # if the file is between Jan 2020 and end of Dec 2020,
    # should flag as in UKRR if flag is 1 in 2019_prevalence

    # if the file is between Jan 2021 and end of Dec 2021,
    # should flag as in UKRR if flag is 1 in 2020_prevalence

    # if the file is between Jan 2022 and end of Dec 2022,
    # should flag as in UKRR if flag is 1 in 2021_prevalence
    year = date.split("-")[0]

    if year in ["2020", "2021", "2022"]:
        if year == "2020":
            df["in_ukrr"] = df["ukrr_2019"]

        elif year == "2021":
            df["in_ukrr"] = df["ukrr_2020"]

        elif year == "2022":
            df["in_ukrr"] = df["ukrr_2021"]

        df = df.loc[(df["at_risk"] == 1), :]

        for test in tests_extended:
            if test not in measures:
                measures[test] = {"not_ukrr": {}, "ukrr": {}}

            measures[test]["not_ukrr"][date] = (
                df.loc[df["in_ukrr"] == 0, test].sum(),
                len(df.loc[df["in_ukrr"] == 0, :]),
            )
            measures[test]["ukrr"][date] = (
                df.loc[df["in_ukrr"] == 1, test].sum(),
                len(df.loc[df["in_ukrr"] == 1, :]),
            )

# convert measures to 3 dataframes - one for each test. columns = numerator, denominator, date, group

for test in tests_extended:
    df_total = pd.DataFrame()
    df_ukrr = pd.DataFrame()

    for date in measures[test]["not_ukrr"].keys():
        df_total = pd.concat(
            [
                df_total,
                pd.DataFrame(
                    {
                        "numerator": measures[test]["not_ukrr"][date][0],
                        "denominator": measures[test]["not_ukrr"][date][1],
                        "date": date,
                        "group": "not_ukrr",
                    },
                    index=[0],
                ),
            ]
        )

        df_ukrr = pd.concat(
            [
                df_ukrr,
                pd.DataFrame(
                    {
                        "numerator": measures[test]["ukrr"][date][0],
                        "denominator": measures[test]["ukrr"][date][1],
                        "date": date,
                        "group": "ukrr",
                    },
                    index=[0],
                ),
            ]
        )

        combined = pd.concat([df_total, df_ukrr])

        combined.to_csv(
            f"output/pub/ukrr_testing/plot_{test}_total_ukrr.csv", index=False
        )

        plot_measures(
            df=combined,
            filename=f"pub/ukrr_testing/plot_{test}_total_ukrr",
            title=f"",
            column_to_plot="numerator",
            y_label="Proportion",
            as_bar=False,
            category="group",
        )
