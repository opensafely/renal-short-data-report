import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from utilities import OUTPUT_DIR, plot_violin_numeric_value
from redaction_utils import drop_and_round
from upsetplot import plot as upset_plot

df = pd.read_csv(OUTPUT_DIR / "joined/input_2022-07-01.csv.gz")

egfr_subset = df.loc[:, ["ckd_primis_stage", "ckd_egfr_category"]]
acr_subset = df.loc[:, ["ckd_primis_stage", "ckd_acr_category"]]
egfr_acr_subset = df.loc[:, ["ckd_egfr_category", "ckd_acr_category"]]

for i, subset in enumerate([egfr_subset, acr_subset, egfr_acr_subset]):

    if "ckd_egfr_category" in subset.columns:
        subset.loc[subset["ckd_egfr_category"] == "G3b", "ckd_egfr_category"] = "G3"
        subset.loc[subset["ckd_egfr_category"] == "G3a", "ckd_egfr_category"] = "G3"

    if "ckd_primis_stage" in subset.columns:
        subset["ckd_primis_stage"] = df["ckd_primis_stage"].astype(str)

    subset_encoded = pd.get_dummies(subset)
    subset_encoded.rename(
        columns={
            "ckd_primis_stage_1": "Coded G1",
            "ckd_primis_stage_2": "Coded G2",
            "ckd_primis_stage_3": "Coded G3",
            "ckd_primis_stage_4": "Coded G4",
            "ckd_primis_stage_5": "Coded G5",
            "ckd_egfr_category_G1": "Biochemical G1",
            "ckd_egfr_category_G2": "Biochemical G2",
            "ckd_egfr_category_G3": "Biochemical G3",
            "ckd_egfr_category_G4": "Biochemical G4",
            "ckd_egfr_category_G5": "Biochemical G5",
            "ckd_acr_category_A1": "A1",
            "ckd_acr_category_A2": "A2",
            "ckd_acr_category_A3": "A3",
        }
    )

    # don't worry about overlap where both groups are None
    if i == 0:
        if "ckd_primis_stage_nan" in subset_encoded.columns:
            subset_encoded = subset_encoded.loc[
                (
                    (subset_encoded["ckd_egfr_category_Uncategorised"] != 1)
                    & (subset_encoded["ckd_primis_stage_nan"] != 1)
                ),
                :,
            ]
    elif i == 1:
        if "ckd_primis_stage_nan" in subset_encoded.columns:

            subset_encoded = subset_encoded.loc[
                (
                    (subset_encoded["ckd_acr_category_Uncategorised"] != 1)
                    & (subset_encoded["ckd_primis_stage_nan"] != 1)
                ),
                :,
            ]

    else:
        subset_encoded = subset_encoded.loc[
            (
                (subset_encoded["ckd_egfr_category_Uncategorised"] != 1)
                & (subset_encoded["ckd_acr_category_Uncategorised"] != 1)
            ),
            :,
        ]

    counts = subset_encoded.groupby(by=subset_encoded.columns.tolist()).grouper.size()
    counts = drop_and_round(counts)
    counts = (counts/1000)
    print(counts)

    plot = upset_plot(counts, show_counts=True, sort_by="cardinality")
   
    plt.savefig(OUTPUT_DIR / f"ckd_staging_upset_{i}.png")
    plt.clf()


# time from test to code

df_subset = df.loc[
    df["ckd_egfr_category"].isin(["G1", "G2", "G3a", "G3b", "G4", "G5"]), :
]

df_subset["ckd_egfr_category"].replace({"G3a": "G3", "G3b": "G3"}, inplace=True)
df_subset["ckd_primis_stage"].replace(
    {1: "G1", 2: "G2", 3: "G3", 4: "G4", 5: "G5"}, inplace=True
)
df_subset = df_subset.loc[
    df_subset["ckd_egfr_category"] == df_subset["ckd_primis_stage"], :
]

df_subset["ckd_primis_stage_date"] = pd.to_datetime(df_subset["ckd_primis_stage_date"])
df_subset["egfr_numeric_value_history_date"] = pd.to_datetime(
    df_subset["egfr_numeric_value_history_date"]
)

df_subset["time_diff"] = (
    df_subset["ckd_primis_stage_date"] - df_subset["egfr_numeric_value_history_date"]
).dt.days
time_diff = df_subset["time_diff"].dropna()

plot_violin_numeric_value(
    time_diff, "time between biochemical and recorded", "time_diff_ckd", cut=1000
)
