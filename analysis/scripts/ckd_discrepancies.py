import pandas as pd
from pathlib import Path
from utilities import OUTPUT_DIR, plot_distribution_numeric_value
from redaction_utils import drop_and_round


df = pd.read_csv(
    OUTPUT_DIR / "joined/input_2023-07-01.csv.gz",
    usecols=[
        "ckd_primis_stage",
        "ckd_egfr_category",
        "latest_rrt_status",
    ],
    dtype={
        "ckd_primis_stage": "str",
        "ckd_egfr_category": "str",
        "latest_rrt_status": "str",
    },
)
df = df.fillna("Missing")

encoded = pd.get_dummies(df)

mapping = columns = {
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
    "latest_rrt_status": "Latest RRT status",
}

encoded = encoded.rename(columns=mapping)

counts = encoded.groupby(by=encoded.columns.tolist()).grouper.size()
counts = drop_and_round(counts)

Path.mkdir(OUTPUT_DIR / "pub/ckd_overlap", parents=True, exist_ok=True)

counts.to_csv(OUTPUT_DIR / f"pub/ckd_overlap/ckd_staging_overlap_combined.csv")