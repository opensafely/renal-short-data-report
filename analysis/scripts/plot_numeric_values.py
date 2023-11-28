import pandas as pd
import numpy as np
from pathlib import Path
from utilities import (
    OUTPUT_DIR,
    match_input_files,
    plot_distribution_numeric_value
)
from variables import tests_extended

Path.mkdir(OUTPUT_DIR / f"pub/numeric_values", parents=True, exist_ok=True)

for test in tests_extended:
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
    numeric_values_combined = np.concatenate(numeric_values)

    percentiles = np.arange(0.01, 0.99, 0.01)
    percentile_values = np.quantile(a=numeric_values_combined, q=percentiles)

    # distribution plot
    plot_distribution_numeric_value(
        percentile_values,
        f"{test} numeric value distribution",
        f"pub/numeric_values/{test}_dist",
    )
