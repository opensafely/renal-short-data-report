import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from utilities import OUTPUT_DIR
from upsetplot import plot as upset_plot


df = pd.read_csv(OUTPUT_DIR / "joined/input_2020-07-01.csv.gz", usecols=["ckd_primis_stage", "ckd_egfr_category", "ckd_acr_category"])

egfr_subset = df.loc[:, ["ckd_primis_stage", "ckd_egfr_category"]]
acr_subset = df.loc[:, ["ckd_primis_stage", "ckd_acr_category"]]
egfr_acr_subset = df.loc[:, ["ckd_egfr_category", "ckd_acr_category"]]

for i, subset in enumerate([egfr_subset, acr_subset, egfr_acr_subset]):
   
    if "ckd_egfr_category" in subset.columns:
        subset.loc[subset["ckd_egfr_category"]=="G3b","ckd_egfr_category"] = "G3"
        subset.loc[subset["ckd_egfr_category"]=="G3a","ckd_egfr_category"] = "G3"
    if "ckd_primis_stage" in subset.columns:
        subset["ckd_primis_stage"] = df["ckd_primis_stage"].astype(str)
    

 
    subset_encoded = pd.get_dummies(subset)
    subset_encoded.rename(columns={
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
        "ckd_egfr_category_None": "Biochemical Missing",
        "ckd_egfr_category_Uncategorised": "Biochemical Uncategorised",
        "ckd_acr_category_None": "A - None",
        "ckd_acr_category_A1": "A1",
        "ckd_acr_category_A2": "A2",
        "ckd_acr_category_A3": "A3",
        "ckd_acr_category_Uncategorised": "A - Uncategorised",
        }
        )

   
    counts = subset_encoded.groupby(by=subset_encoded.columns.tolist()).grouper.size()
    

    upset_plot(counts)
    plt.savefig(OUTPUT_DIR / f"ckd_staging_upset_{i}.png")


