import pandas as pd
import numpy as np
from pathlib import Path
from utilities import *
from redaction_utils import redact_small_numbers
from variables import tests

if not (OUTPUT_DIR / "figures").exists():
    Path.mkdir(OUTPUT_DIR / "figures")


df = pd.read_csv(
    OUTPUT_DIR / f"measure_incident_ckd_primis_stage_rate.csv", parse_dates=["date"]
)

df = redact_small_numbers(df, 7, 5, "ckd_primis", "population", "value", "date")

plot_measures(
    df=df,
    filename=f"plot_incident_ckd",
    title=f"Incident CKD by Stage",
    column_to_plot="value",
    y_label="Proportion",
    as_bar=False,
    category="ckd_primis_stage",
)





