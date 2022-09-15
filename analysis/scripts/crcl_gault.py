import pandas as pd
import seaborn as sns
import numpy as np
import json
import matplotlib.pyplot as plt
from venn import venn
from utilities import OUTPUT_DIR

df = pd.read_csv(OUTPUT_DIR / "input_calculators_calculated.csv.gz", parse_dates = ["creatinine_numeric_value_date", "creatinine_clearance_numeric_value_date"])

subset = df.loc[df["creatinine_numeric_value_date"] > "2021-07-01",:]
subset_with_crcl = subset.loc[subset["creatinine_clearance_numeric_value_date"] >= subset["creatinine_numeric_value_date"],:]


with open(OUTPUT_DIR / "creatinine_vs_crlc.json", "w") as f:
    json.dump({"creatinine_last_year": len(subset), "crcl on or after creatinine": len(subset_with_crcl)}, f)

    

latest_crcl_calculated = df["cg"][df["cg"].notnull()]
latest_crcl_recorded = df["creatinine_clearance_numeric_value"][df["creatinine_clearance_numeric_value"].notnull()
]

percentiles = np.arange(0.01, 0.99, 0.01)
percentile_values_crcl_calculated = np.quantile(a=latest_crcl_calculated, q=percentiles)
percentile_values_crcl_recorded = np.quantile(a=latest_crcl_recorded, q=percentiles)

violin_df = pd.DataFrame({
    "Calculated": pd.Series(percentile_values_crcl_calculated),
    "Recorded": pd.Series(percentile_values_crcl_recorded)
})

sns.violinplot(data=violin_df, cut=0, inner=None)
plt.title("CrCl Calculated vs Recorded")
plt.ylabel("numeric value")
plt.savefig(OUTPUT_DIR / f"violin_plot_crcl_recorded_vs_calculated.png")
plt.clf()


people_recorded = df.loc[((df["creatinine_clearance_numeric_value"].notnull()) & (df["creatinine_clearance_numeric_value"]> 0)),:]
people_calculated = df.loc[((df["cg"].notnull()) & (df["cg"]> 0)),:]

venn({"Recorded": set(people_recorded["patient_id"]),
"Calculated": set(people_calculated["patient_id"])})
plt.savefig(OUTPUT_DIR / f"venn_crcl_recorded_vs_calculated.png")
plt.clf()
