import pandas as pd
import numpy as np
from utilities import (
    OUTPUT_DIR,
    match_input_files,
    plot_boxplot_numeric_value,
    plot_violin_numeric_value,
    plot_violin_numeric_value_combined
)
from variables import tests

combined_data = []
combined_data_df = pd.DataFrame(
    {"test": pd.Series([]),
    "value": pd.Series([])}
)
for test in tests:
    numeric_values = []
    for file in (OUTPUT_DIR / "joined").iterdir():
        if match_input_files(file.name):
            df = pd.read_csv(
                (OUTPUT_DIR / "joined") / file.name, usecols=[f"{test}_numeric_value"]
            )
            numeric_values.append(
                np.array(
                    df.loc[
                        (
                            (df[f"{test}_numeric_value"].notnull())
                            & (df[f"{test}_numeric_value"] > 0)
                        ),
                        f"{test}_numeric_value",
                    ]
                )
            )
    combined_data.append(np.concatenate(numeric_values))
    numeric_values_combined = np.concatenate(numeric_values)

    # boxplot

    plot_boxplot_numeric_value(
        numeric_values_combined,
        f"{test} numeric value distribution",
        f"{test}_dist",
    )

    # violin plot

    plot_violin_numeric_value(
        numeric_values_combined,
        f"{test} numeric value distribution",
        f"{test}_dist_violin",
    )

    percentiles = np.arange(0.01, 0.99, 0.01)
    percentile_values = np.quantile(a=numeric_values_combined, q=percentiles)

    combined_data_df = pd.concat([combined_data_df, pd.DataFrame({"test": pd.Series([test]*len(percentile_values)), "value": percentile_values})])
            

combined_data_df = combined_data_df.replace({"albumin": "Albumin", "acr": "ACR", "creatinine": "Creatinine", "egfr": "eGFR", "cr_cl": "Creatine Clearance"})

plot_violin_numeric_value_combined(
        combined_data_df,  
        f"Numeric value distribution",
        f"combined_dist_violin")


