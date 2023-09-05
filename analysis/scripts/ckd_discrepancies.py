import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from upsetplot import plot as upset_plot

from utilities import OUTPUT_DIR, plot_distribution_numeric_value
from redaction_utils import drop_and_round


df = pd.read_csv(OUTPUT_DIR / "joined/input_2022-07-01.csv.gz")

egfr_subset = df.loc[:, ["ckd_primis_stage", "ckd_egfr_category"]]
acr_subset = df.loc[:, ["ckd_primis_stage", "ckd_acr_category"]]
egfr_acr_subset = df.loc[:, ["ckd_egfr_category", "ckd_acr_category"]]
dialysis_subset = df.loc[:, ["ckd_primis_stage", "ckd_egfr_category", "latest_rrt_status"]]


combined = df.loc[:, ["ckd_primis_stage", "ckd_egfr_category", "ckd_acr_category"]]
combined = combined.fillna("Missing")
combined["ckd_primis_stage"] = combined["ckd_primis_stage"].astype(str)
combined["ckd_egfr_category"] = combined["ckd_egfr_category"].astype(str)
combined["ckd_acr_category"] = combined["ckd_acr_category"].astype(str)
combined_encoded = pd.get_dummies(combined)

mapping = columns={
            "ckd_primis_stage_1": "Coded G1",
            "ckd_primis_stage_2": "Coded G2",
            "ckd_primis_stage_3": "Coded G3",
            "ckd_primis_stage_4": "Coded G4",
            "ckd_primis_stage_5": "Coded G5",
            "ckd_primis_stage_Missing": "Primary Care Stage Missing",
            "ckd_egfr_category_Uncategorised": "Biochemical Undefined",
            "ckd_egfr_category_G1": "Biochemical G1",
            "ckd_egfr_category_G2": "Biochemical G2",
            "ckd_egfr_category_G3a": "Biochemical G3a",
            "ckd_egfr_category_G3b": "Biochemical G3b",
            "ckd_egfr_category_G4": "Biochemical G4",
            "ckd_egfr_category_G5": "Biochemical G5",
            "ckd_acr_category_A1": "A1",
            "ckd_acr_category_A2": "A2",
            "ckd_acr_category_A3": "A3",
            "ckd_acr_category_Uncategorised": "ACR Undefined",
            "latest_rrt_status": "Latest RRT status",
        }

combined_encoded = combined_encoded.rename(columns=mapping)

counts = combined_encoded.groupby(by=combined_encoded.columns.tolist()).grouper.size()
counts = drop_and_round(counts)


counts_dialysis = dialysis_subset.groupby(by=dialysis_subset.columns.tolist()).grouper.size()
counts_dialysis = drop_and_round(counts_dialysis)

counts_dialysis.to_csv(OUTPUT_DIR / f"ckd_rrt_upset.csv")

counts.to_csv(OUTPUT_DIR / f"ckd_staging_upset_combined.csv")

# for patients with bioechmical 4/5 who are not coded 4/5, what is their rrt status?
counts_dialysis = counts_dialysis.reset_index()

biochem_4_5_not_coded = counts_dialysis.loc[
    (counts_dialysis["ckd_egfr_category"].isin(["G4", "G5"])) & ~(counts_dialysis["ckd_primis_stage"].isin([4, 5])), :
]

biochem_4_5_not_coded = biochem_4_5_not_coded.rename(columns=mapping)
biochem_4_5_not_coded = biochem_4_5_not_coded.rename(columns={"ckd_primis_stage": "Primary Care Stage", "ckd_egfr_category": "Biochemical Stage", "latest_rrt_status": "Latest RRT status"})

biochem_4_5_not_coded.to_csv(OUTPUT_DIR / f"biochem_4_5_not_coded.csv")



for i, subset in enumerate([egfr_subset, acr_subset, egfr_acr_subset]):

    subset =  subset.fillna("Missing")
   
    if "ckd_primis_stage" in subset.columns:
        subset["ckd_primis_stage"] = df["ckd_primis_stage"].astype(str)


    
    subset_encoded = pd.get_dummies(subset)
    subset_encoded = subset_encoded.rename(
        columns=mapping
    )

    if i == 0:
        if "Primary Care Stage Missing" in subset_encoded.columns:
            subset_encoded = subset_encoded.loc[
                (
                    (subset_encoded["Biochemical Undefined"] != 1)
                    & (subset_encoded["Primary Care Stage Missing"] != 1)
                ),
                :,
            ]
    elif i == 1:
        if "Primary Care Stage Missing" in subset_encoded.columns:

            subset_encoded = subset_encoded.loc[
                (
                    (subset_encoded["ACR Undefined"] != 1)
                    & (subset_encoded["Primary Care Stage Missing"] != 1)
                ),
                :,
            ]

    elif i == 2:
        subset_encoded = subset_encoded.loc[
            (
                (subset_encoded["Biochemical Undefined"] != 1)
                & (subset_encoded["ACR Undefined"] != 1)
            ),
            :,
        ]
    
     
    
    

    counts = subset_encoded.groupby(by=subset_encoded.columns.tolist()).grouper.size()
    counts = drop_and_round(counts)
    
    counts.to_csv(OUTPUT_DIR / f"ckd_staging_upset_{i}.csv")
    plot = upset_plot(counts, show_counts=True, sort_by="cardinality")
   
    plt.savefig(OUTPUT_DIR / f"ckd_staging_upset_{i}.png")
    plt.clf()

    counts = counts.reset_index()

    counts = counts.rename(columns={0: "count"})

    counts = counts.rename(columns=mapping)

    if i == 0:
        row_key = "Coded"
        col_key = "Biochemical"

    elif i == 1:
        row_key = "Coded"
        col_key = "A"
    
    else:
        row_key = "Biochemical"
        col_key = "A"

    rows = [col for col in counts.columns if row_key in col]
    cols = [col for col in counts.columns if col_key in col]

    grid = np.zeros((len(rows), len(cols)))
    
    for x, row in enumerate(rows):
        for y, col in enumerate(cols):
           
            value = counts.loc[
                (counts[row] == 1) & (counts[col] == 1), "count"
            ].values
            if value:
                value = value[0]
            else:
                value = 0
            grid[x, y] = value
        
    
    if grid.any():
        sns.heatmap(grid, cmap="Blues", annot=True, fmt="g", xticklabels=cols, yticklabels=rows)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / f"ckd_staging_{i}_heatmap.png")
        plt.clf()

        # save grid
        grid_df = pd.DataFrame(grid, index=rows, columns=cols)
        grid_df.to_csv(OUTPUT_DIR / f"ckd_staging_{i}_heatmap.csv")


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



plot_distribution_numeric_value(
    time_diff, "time between biochemical and recorded", "time_diff_ckd"
)