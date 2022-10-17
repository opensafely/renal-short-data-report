import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from upsetplot import plot as upset_plot
from utilities import OUTPUT_DIR
from redaction_utils import drop_and_round
import seaborn as sns
import numpy as np


df = pd.read_csv(OUTPUT_DIR / "joined/input_2020-12-01.csv.gz", usecols=["ckd_primis_stage", "ukrr_ckd2020", "ukrr_ckd2020_creat", "ukrr_ckd2020_egfr", "egfr_numeric_value_history", "creatinine_numeric_value_history"])

# Overlap between those in ukkr_ckd2020 and those with ckd stage using primis
stage_subset = df.loc[:,["ckd_primis_stage", "ukrr_ckd2020"]]
stage_subset =  stage_subset.fillna("Missing")
stage_subset["ckd_primis_stage"] = stage_subset["ckd_primis_stage"].astype(str)
stage_subset["ukrr_ckd2020"] = stage_subset["ukrr_ckd2020"].astype(str)
stage_subset_encoded = pd.get_dummies(stage_subset)

stage_subset_encoded = stage_subset_encoded.rename(
    columns={
        "ckd_primis_stage_1.0": "Primary Care Stage 1",
        "ckd_primis_stage_2.0": "Primary Care Stage 2",
        "ckd_primis_stage_3.0": "Primary Care Stage 3",
        "ckd_primis_stage_4.0": "Primary Care Stage 4",
        "ckd_primis_stage_5.0": "Primary Care Stage 5",
        "ckd_primis_stage_Missing": "Primary Care Stage Missing",
        "ukrr_ckd2020_0.0": "Not in UKRR",
        "ukrr_ckd2020_1.0": "In UKRR",
        "ukrr_ckd2020_Missing": "Missing in UKRR"
    }
    )

counts = stage_subset_encoded.groupby(by=stage_subset_encoded.columns.tolist()).grouper.size()
counts = drop_and_round(counts)
plot = upset_plot(counts, show_counts=True, sort_by="cardinality")
plt.savefig(OUTPUT_DIR / "ukrr_overlap_stage.png")
plt.clf()




ukrr_latest_egfr = df["ukrr_ckd2020_egfr"][df["ukrr_ckd2020_egfr"].notnull()]
prim_care_latest_egfr = df["egfr_numeric_value_history"][df["egfr_numeric_value_history"].notnull()
]
percentiles = np.arange(0.01, 0.99, 0.01)
percentile_values_ukrr = np.quantile(a=ukrr_latest_egfr, q=percentiles)
percentile_values_pc = np.quantile(a=prim_care_latest_egfr, q=percentiles)

violin_df = pd.DataFrame({
    "UKRR": pd.Series(percentile_values_ukrr),
    "Primary Care": pd.Series(percentile_values_pc)
})

sns.violinplot(data=violin_df, cut=0, inner=None)
plt.title("eGFR UKRR vs Primary Care")
plt.ylabel("numeric value")
plt.savefig(OUTPUT_DIR / f"violin_plot_ukrr_pc_egfr.png")
plt.clf()

ukrr_latest_creatinine = df["ukrr_ckd2020_creat"][df["ukrr_ckd2020_creat"].notnull()]
prim_care_latest_creatinine = df["creatinine_numeric_value_history"][df["creatinine_numeric_value_history"].notnull()
]
percentiles = np.arange(0.01, 0.99, 0.01)
percentile_values_ukrr = np.quantile(a=ukrr_latest_creatinine, q=percentiles)
percentile_values_pc = np.quantile(a=prim_care_latest_creatinine, q=percentiles)

df = pd.DataFrame({
    "UKRR": pd.Series(percentile_values_ukrr),
    "Primary Care": pd.Series(percentile_values_pc)
})

sns.violinplot(data=df, cut=0, inner=None)
plt.title("Creatinine UKRR vs Primary Care")
plt.ylabel("numeric value")
plt.savefig(OUTPUT_DIR / f"violin_plot_ukrr_pc_creatinine.png")
plt.clf()