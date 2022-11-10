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
        "ukrr_ckd2020_0": "Not in UKRR",
        "ukrr_ckd2020_1": "In UKRR",
        "ukrr_ckd2020_Missing": "Missing in UKRR"
    }
    )

counts = stage_subset_encoded.groupby(by=stage_subset_encoded.columns.tolist()).grouper.size()
counts = drop_and_round(counts)

# drop patients where missing from Ukrr and prim care - we don't care about these.
# drop row where index is 1 for "Missing in UKRR" and "Primary Care Stage Missing" if it exists

# if "Primary Care Stage Missing" in counts.index.names:

#     counts = counts.drop(index=1, level="Primary Care Stage Missing", errors="ignore", axis=0)

#save counts to csv
counts.to_csv(OUTPUT_DIR / "ukrr_overlap_stage.csv")

plot = upset_plot(counts, show_counts=True, sort_by="cardinality")
plt.savefig(OUTPUT_DIR / "ukrr_overlap_stage.png")
plt.clf()



#ukrr latest egfr where not null or 0

ukrr_latest_egfr = df["ukrr_ckd2020_egfr"][(df["ukrr_ckd2020_egfr"].notnull()) & (df["ukrr_ckd2020_egfr"]>0)]

# prim care latest egfr in advanced ckd
prim_care_latest_egfr = df["egfr_numeric_value_history"][(df["egfr_numeric_value_history"].notnull()) & (df["egfr_numeric_value_history"]>0) & (df["ckd_primis_stage"]>=4)]

# print(ukrr_latest_egfr.values)
# sns.violinplot(data=ukrr_latest_egfr.values,inner=None)
# plt.title(f"eGFR UKRR (n={len(ukrr_latest_egfr)})")
# plt.ylabel("numeric value")
# plt.savefig(OUTPUT_DIR / f"violin_plot_ukrr_egfr.png")
# plt.clf()

percentiles = np.arange(0.01, 0.99, 0.01)
percentile_values_ukrr = np.quantile(a=ukrr_latest_egfr, q=percentiles)
percentile_values_pc = np.quantile(a=prim_care_latest_egfr, q=percentiles)

violin_df = pd.DataFrame({
    f"UKRR (n={len(ukrr_latest_egfr)})": pd.Series(percentile_values_ukrr),
    f"Primary Care (n={len(prim_care_latest_egfr)})": pd.Series(percentile_values_pc)
})
# show number of values on violin plot

sns.violinplot(data=violin_df, cut=0, inner=None)
plt.title("eGFR UKRR vs Primary Care")
plt.ylabel("numeric value")
plt.savefig(OUTPUT_DIR / f"violin_plot_ukrr_pc_egfr.png")
plt.clf()

ukrr_latest_creatinine = df["ukrr_ckd2020_creat"][(df["ukrr_ckd2020_creat"].notnull())&(df["ukrr_ckd2020_creat"]>0)]
prim_care_latest_creatinine = df["creatinine_numeric_value_history"][(df["creatinine_numeric_value_history"].notnull()) & (df["creatinine_numeric_value_history"]>0) & (df["ckd_primis_stage"]>=4)
]

# sns.violinplot(data=ukrr_latest_creatinine,inner=None)
# plt.title(f"Creatinine UKRR (n={len(ukrr_latest_creatinine)})")
# plt.ylabel("numeric value")
# plt.savefig(OUTPUT_DIR / f"violin_plot_ukrr_creatinine.png")
# plt.clf()

percentiles = np.arange(0.01, 0.99, 0.01)
percentile_values_ukrr = np.quantile(a=ukrr_latest_creatinine, q=percentiles)
percentile_values_pc = np.quantile(a=prim_care_latest_creatinine, q=percentiles)

df = pd.DataFrame({
    f"UKRR (n={len(ukrr_latest_creatinine)})": pd.Series(percentile_values_ukrr),
    f"Primary Care (n={len(prim_care_latest_creatinine)})": pd.Series(percentile_values_pc)
})

sns.violinplot(data=df, cut=0, inner=None)
plt.title("Creatinine UKRR vs Primary Care")
plt.ylabel("numeric value")
plt.savefig(OUTPUT_DIR / f"violin_plot_ukrr_pc_creatinine.png")
plt.clf()