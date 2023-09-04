import pandas as pd
import numpy as np
from pathlib import Path
from utilities import *
from redaction_utils import compute_redact_deciles, redact_small_numbers
from variables import tests

if not (OUTPUT_DIR / "figures").exists():
    Path.mkdir(OUTPUT_DIR / "figures")


#for each test, plot deciles charts in total population and at risk population
for i in [
    "creatinine",
    "eGFR",
    "albumin",
    "ckd",
    "ckd_primis_1_5",
]:
    for j in ["population", "at_risk"]:

        if i == "ckd_primis_1_5":
            df = pd.read_csv(
                OUTPUT_DIR / f"joined/measure_{i}_stage_{j}_practice_rate.csv",
                parse_dates=["date"],
            )

        else:
            df = pd.read_csv(
                OUTPUT_DIR / f"joined/measure_{i}_{j}_rate.csv", parse_dates=["date"]
            )
        
        df = drop_irrelevant_practices(df)

        dfs = {}

        if i == "ckd_primis_1_5":
            # plot rate separarely for stage 1-2 and 3-5
            df_subset_1_2 = df.loc[df["ckd_primis_stage"].isin([1, 2]), :]
            df_subset_3_5 = df.loc[df["ckd_primis_stage"].isin([3, 4, 5]), :]
            
            dfs["stage_1_2"] = df_subset_1_2
            dfs["stage_3_5"] = df_subset_3_5
        
        else:
            dfs["all"] = df


        for k, df in dfs.items():
           

            df["rate"] = df[f"value"] * 100

            df = df.drop(["value"], axis=1)
            df = df.replace(np.inf, np.nan)
            
            df_deciles = compute_redact_deciles(df, "date", i, "rate")

            deciles_chart(
                df,
                filename=f"output/figures/plot_{i}_{j}_{k}.jpeg",
                period_column="date",
                column="rate",
                count_column=i,
                ylabel="Percentage",
            )

            if i in ["ckd", "ckd_primis_1_5"]:
                demographics = []

            else:
                demographics = ["age_band", "sex", "imd", "region"]

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

                df = redact_small_numbers(df, 7, 5, i, j, "rate", "date")

                plot_measures(
                    df=df,
                    filename=f"plot_{i}_{d}_{j}_{k}",
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
    df_ckd_stage, 7, 5,"ckd_primis_1_5", "population", "rate", "date"
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
        df_ckd_stage, 7, 5,"ckd_primis_1_5", "population", "rate", "date"
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
        df, 7, 5,test, "population", "value", "date"
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
        df_ckd_stage_egfr, 7, 5,test, "population", "rate", "date"
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
        df_ckd_stage_acr, 7, 5,test, "population", "rate", "date"
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



# plot rate of each test fop those biochem stage 3-5, vs primis recorded 3-5 vs single reduced egfr

for test in tests:

    single_egfr = pd.read_csv(
        OUTPUT_DIR / f"joined/measure_{test}_single_egfr_population_rate.csv",
        parse_dates=["date"],
    )
    single_egfr = single_egfr.loc[single_egfr["single_egfr"]==1,:]
    single_egfr = single_egfr.drop(["single_egfr",], axis=1)

    primis_stage = pd.read_csv(
        OUTPUT_DIR / f"joined/measure_{test}_stage_population_rate.csv",
        parse_dates=["date"],
    )
    primis_stage = primis_stage.loc[primis_stage["ckd_primis_stage"].isin([3, 4, 5]), :]
    primis_stage = primis_stage.groupby(by=["date"])[[test, "population"]].sum().reset_index()
    primis_stage["value"] = (primis_stage[test]/primis_stage["population"])



    ckd_stage = pd.read_csv(
        OUTPUT_DIR / f"joined/measure_{test}_biochemical_stage_population_rate.csv",
        parse_dates=["date"],
    )
    ckd_stage = ckd_stage.loc[ckd_stage["ckd_egfr_category"].isin(["G3a", "G3b", "G4", "G5"]), :]
    ckd_stage = ckd_stage.groupby(by=["date"])[[test, "population"]].sum().reset_index()
    ckd_stage["value"] = (ckd_stage[test]/ckd_stage["population"])

    # now plot on the same axis
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(
        single_egfr["date"],
        single_egfr["value"]*1000,
        label="Single reduced eGFR",
        color="red",
    )
    ax.plot(
        primis_stage["date"],
        primis_stage["value"]*1000,
        label="CKD stage (PRIMIS)",
        color="blue",
    )
    ax.plot(
        ckd_stage["date"],
        ckd_stage["value"]*1000,
        label="CKD stage (biochemical)",
        color="green",
    )

    x_labels = sorted(single_egfr["date"].dt.strftime("%Y-%m-%d").unique())
    ax.set_xticks(x_labels)
    ax.set_xticklabels(x_labels, rotation='vertical')
    ax.set_ylabel("Rate per 1000")
    ax.set_xlabel("Date")
    ax.margins(x=0)
    ax.grid(True)

    ax.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(f"output/figures/plot_{test}_single_biochem_stage.jpeg")
    plt.close()


# plot rate of testing in those at risk in the general pop not in UKRR vs those that are in UKRR


# 2019_prevalence a prevalence cohort of patients alive and on RRT in December 2019
# 2020_prevalence a prevalence cohort of patients alive and on RRT in December 2020
# 2021_prevalence a prevalence cohort of patients alive and on RRT in December 2021
# 2020_incidence an incidence cohort of patients who started RRT in 2020
# 2020_ckd a snapshot prevalence cohort of patient with Stage 4 or 5 CKD who were reported to the UKRR to be under renal care in December 2020



measures = {

}

for path in Path("output/joined").glob("input_20*.csv.gz"):

    df = pd.read_csv(path)
    date = get_date_input_file(path.name)

    # if the file is between Jan 2020 and end of Dec 2020,
    # should flag as in UKRR if flag is 1 in 2019_prevalence

    # if the file is between Jan 2021 and end of Dec 2021,
    # should flag as in UKRR if flag is 1 in 2020_prevalence

    # if the file is between Jan 2022 and end of Dec 2022,
    # should flag as in UKRR if flag is 1 in 2021_prevalence
    year = date.split('-')[0]
 
    if year in ["2020", "2021", "2022"]:

        if year == "2020":
            df["in_ukrr"] = df["ukrr_2019"]
        
        elif year == "2021":
            df["in_ukrr"] = df["ukrr_2020"]

        elif year == "2022":
            df["in_ukrr"] = df["ukrr_2021"]

   
        df = df.loc[(df["at_risk"]==1),:]

 
        for test in tests:
            if test not in measures:
                measures[test] = {"not_ukrr": {}, "ukrr": {}}

            measures[test]["not_ukrr"][date] = (df.loc[df["in_ukrr"]==0, test].sum(), len(df.loc[df["in_ukrr"]==0, :]))
            measures[test]["ukrr"][date] = (df.loc[df["in_ukrr"]==1, test].sum(), len(df.loc[df["in_ukrr"]==1, :]))

# convert measures to 3 dataframes - one for each test. columns = numerator, denominator, date, group

for test in tests:
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

        combined.to_csv(f"output/figures/plot_{test}_total_ukrr.csv", index=False)

        plot_measures(
            df=combined,
            filename=f"plot_{test}_total_ukrr",
            title=f"",
            column_to_plot="numerator",
            y_label="Proportion",
            as_bar=False,
            category="group",
        )