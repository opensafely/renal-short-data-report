import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utilities import OUTPUT_DIR, match_input_files, get_date_input_file

numeric_values_creatinine = []
numeric_values_cr_cl = []
numeric_values_egfr = []

for file in (OUTPUT_DIR / "joined").iterdir():
    if match_input_files(file.name):
        df = pd.read_csv((OUTPUT_DIR / "joined") / file.name)
        date = get_date_input_file(file.name)
        numeric_values_creatinine.append(np.array(df["creatinine_numeric_value"]))
        numeric_values_cr_cl.append(np.array(df["cr_cl_numeric_value"]))
        numeric_values_egfr.append(np.array(df["eGFR_numeric_value"]))

numeric_values_creatinine = np.concatenate(numeric_values_creatinine)
numeric_values_cr_cl = np.concatenate(numeric_values_cr_cl)
numeric_values_egfr = np.concatenate(numeric_values_egfr)


def plot_boxplot_numeric_value(x, title, filename):
    plt.boxplot(x, showfliers=False)
    plt.title(title)
    plt.ylabel("count")
    plt.xlabel("numeric_value")
    plt.savefig(f"output/{filename}.jpeg")
    plt.clf()


plot_boxplot_numeric_value(
    numeric_values_creatinine,
    "Creatinine numeric value distribution",
    "creatinine_dist",
)
plot_boxplot_numeric_value(
    numeric_values_cr_cl,
    "Creatinine clearance numeric value distribution",
    "creatinine_clearance_dist",
)
plot_boxplot_numeric_value(
    numeric_values_egfr, "eGFR numeric value distribution", "egfr_dist"
)