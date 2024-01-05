import pandas as pd
from pathlib import Path
from utilities import OUTPUT_DIR
from redaction_utils import drop_and_round

# Read the data
df = pd.read_csv(
    OUTPUT_DIR / "joined/input_2023-07-01.csv.gz",
    usecols=[
        "ckd_primis_stage",
        "ckd_egfr_category",
        "latest_rrt_status",
        "ckd_acr_category"
    ],
    dtype={
        "ckd_primis_stage": "str",
        "ckd_egfr_category": "str",
        "latest_rrt_status": "str",
    },
)

# Fill missing values
df = df.fillna("Missing")

# Drop anyone with stage 1 or 2 who dont have stage A2 or A3 for ACR results. set their egfr_category to Uncategorised
df.loc[
    (
        (
            (df["ckd_egfr_category"] == "G1") | (df["ckd_egfr_category"] == "G2")
        ) &
        (
            (df["ckd_acr_category"] != "A2") & (df["ckd_acr_category"] != "A3")
        )
    )
    ,
    "ckd_egfr_category",
] = "Uncategorised"

# Count the overlap of the different categories
counts = df.groupby(
    ["ckd_primis_stage", "ckd_egfr_category", "latest_rrt_status"]
).size()

counts = drop_and_round(counts)

# rename the columns
counts = counts.reset_index().rename(columns={0: "count"})

output_dir = OUTPUT_DIR / "pub/ckd_overlap"
Path.mkdir(output_dir, parents=True, exist_ok=True)

counts.to_csv(output_dir / f"ckd_staging_overlap_combined.csv", index=False)
