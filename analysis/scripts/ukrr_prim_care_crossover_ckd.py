import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from utilities import OUTPUT_DIR, plot_distribution_numeric_value
from redaction_utils import drop_and_round, round_values


Path.mkdir(OUTPUT_DIR / "pub/ukrr_pc_overlap", parents=True, exist_ok=True)

df = pd.read_csv(
    OUTPUT_DIR / "joined/input_2020-12-01.csv.gz",
    usecols=[
        "ckd_primis_stage",
        "ukrr_2020",
        "ukrr_ckd2020",
        "ukrr_ckd2020_creat",
        "ukrr_ckd2020_egfr",
        "egfr_numeric_value_history",
        "creatinine_numeric_value_history",
    ],
)

# Overlap between those in ukkr_ckd2020 and those with ckd stage using primis
stage_subset = df.loc[:, ["ckd_primis_stage", "ukrr_ckd2020"]]
stage_subset = stage_subset.fillna("Missing")
stage_subset = stage_subset.loc[stage_subset["ukrr_ckd2020"] == 1]
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
        "ukrr_ckd2020_Missing": "Missing in UKRR",
    }
)

counts = stage_subset_encoded.groupby(
    by=stage_subset_encoded.columns.tolist()
).grouper.size()
counts = drop_and_round(counts)

counts.to_csv(OUTPUT_DIR / "pub/ukrr_pc_overlap/ukrr_overlap_stage.csv")


# Overlap between those in ukkr_2020 and those with ckd stage using primis
stage_subset_rrt = df.loc[:, ["ckd_primis_stage", "ukrr_2020"]]
stage_subset_rrt = stage_subset_rrt.fillna("Missing")
stage_subset_rrt = stage_subset_rrt.loc[stage_subset_rrt["ukrr_2020"] == 1]
stage_subset_rrt["ckd_primis_stage"] = stage_subset_rrt["ckd_primis_stage"].astype(str)
stage_subset_rrt["ukrr_2020"] = stage_subset_rrt["ukrr_2020"].astype(str)
stage_subset_rrt_encoded = pd.get_dummies(stage_subset_rrt)

stage_subset_rrt_encoded = stage_subset_rrt_encoded.rename(
    columns={
        "ckd_primis_stage_1.0": "Primary Care Stage 1",
        "ckd_primis_stage_2.0": "Primary Care Stage 2",
        "ckd_primis_stage_3.0": "Primary Care Stage 3",
        "ckd_primis_stage_4.0": "Primary Care Stage 4",
        "ckd_primis_stage_5.0": "Primary Care Stage 5",
        "ckd_primis_stage_Missing": "Primary Care Stage Missing",
        "ukrr_2020_0": "Not in UKRR",
        "ukrr_2020_1": "In UKRR",
        "ukrr_2020_Missing": "Missing in UKRR",
    }
)

counts = stage_subset_rrt_encoded.groupby(
    by=stage_subset_rrt_encoded.columns.tolist()
).grouper.size()
counts = drop_and_round(counts)

counts.to_csv(OUTPUT_DIR / "pub/ukrr_pc_overlap/ukrr_rrt_overlap_stage.csv")


# ukrr latest egfr where not null or 0

ukrr_latest_egfr = df["ukrr_ckd2020_egfr"][
    (df["ukrr_ckd2020_egfr"].notnull()) & (df["ukrr_ckd2020_egfr"] > 0)
]


# prim care latest egfr in (for patients in UKRR)
prim_care_latest_egfr = df["egfr_numeric_value_history"][
    (df["ukrr_2020"].notnull())
    & (df["egfr_numeric_value_history"].notnull())
    & (df["egfr_numeric_value_history"] > 0)
    & (df["ckd_primis_stage"] >= 4)
    & ((df["ukrr_ckd2020_egfr"].notnull()) & (df["ukrr_ckd2020_egfr"] > 0))
]


#ukrr_latest_egfr, prim_care_latest_egfr


plot_distribution_numeric_value(
    {"UKRR": ukrr_latest_egfr, "Primary Care": prim_care_latest_egfr},
    "eGFR UKRR vs Primary Care",
    "pub/ukrr_pc_overlap/dist_plot_ukrr_pc_egfr",
    0,
    60,
    5,
    True
)

ukrr_latest_creatinine = df["ukrr_ckd2020_creat"][
    (df["ukrr_ckd2020_creat"].notnull()) & (df["ukrr_ckd2020_creat"] > 0)
]
prim_care_latest_creatinine = df["creatinine_numeric_value_history"][
    (df["ukrr_2020"].notnull())
    & (df["creatinine_numeric_value_history"].notnull())
    & (df["creatinine_numeric_value_history"] > 0)
    & (df["ckd_primis_stage"] >= 4)
    & ((df["ukrr_ckd2020_creat"].notnull()) & (df["ukrr_ckd2020_creat"] > 0))
]

# table with the number of results in each category
counts_table = pd.DataFrame(
    {
        "egfr UKRR (n=)": [round(len(ukrr_latest_egfr) / 5) * 5],
        "egfr Primary Care (n=)": [round(len(prim_care_latest_egfr) / 5) * 5],
        "creatinine UKRR (n=)": [round(len(ukrr_latest_creatinine) / 5) * 5],
        "creatinine Primary Care (n=)": [round(len(prim_care_latest_creatinine) / 5) * 5],
    }
)


counts_table.to_csv(
    OUTPUT_DIR / "pub/ukrr_pc_overlap/ukrr_pc_counts_table.csv", index=False
)

plot_distribution_numeric_value(
    {"UKRR": ukrr_latest_creatinine, "Primary Care": prim_care_latest_creatinine},
    "Creatinine UKRR vs Primary Care",
    "pub/ukrr_pc_overlap/dist_plot_ukrr_pc_creatinine",
    50,
    500,
    10,
    True
)