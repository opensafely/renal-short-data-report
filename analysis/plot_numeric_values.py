import pandas as pd
import numpy as np
from utilities import (
    OUTPUT_DIR,
    match_input_files,
    get_date_input_file,
    plot_boxplot_numeric_value,
    plot_violin_numeric_value,
)
from variables import tests

numeric_values = {}
for test in tests:
    numeric_values[test] = []
numeric_values_creatinine = []
numeric_values_cr_cl = []
numeric_values_egfr = []

for file in (OUTPUT_DIR / "joined").iterdir():
    if match_input_files(file.name):
        df = pd.read_csv((OUTPUT_DIR / "joined") / file.name)
        date = get_date_input_file(file.name)
        for test in tests:
            numeric_values[test].append(np.array(df[f"{test}_numeric_value"]))

for test in tests:
    numeric_values_combined = np.concatenate(numeric_values[test])

    # boxplot

    plot_boxplot_numeric_value(
        numeric_values_combined[numeric_values_combined > 0],
        f"{test} numeric value distribution",
        f"{test}_dist",
    )

    # violin plot

    plot_violin_numeric_value(
        numeric_values_combined[numeric_values_combined > 0],
        f"{test} numeric value distribution",
        f"{test}_dist_violin",
    )
