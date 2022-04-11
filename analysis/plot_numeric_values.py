import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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

def plot_violin_numeric_value(x, title, filename):
    """Plots a violin plot from an array of numeric values. Controls for disclosure by
    calculating percentiles and using this to generate the plots rather than the raw values. 
    This will be sufficient for large the majority of populations. Limits the range of plotted data
    to the top and bottom quantile using `cut=0`.

    """

    percentiles = np.arange(0.01, 0.99, 0.01)
    percentile_values = np.quantile(a=x, q=percentiles)
    figure_output = sns.violinplot(data=percentile_values, cut=0)
    plt.title(title)
    plt.ylabel("numeric value")
    plt.savefig(f"output/{filename}.jpeg")
    plt.clf()

plot_violin_numeric_value(numeric_values_egfr, "eGFR numeric value distribution", "egfr_dist_violin")
plot_violin_numeric_value(numeric_values_creatinine, "creatinine numeric value distribution", "creatinine_dist_violin")
plot_violin_numeric_value(numeric_values_cr_cl, "creatinine clearance numeric value distribution", "cr_cl_dist_violin")

# Plots for numeric values >0

plot_violin_numeric_value(numeric_values_egfr[numeric_values_egfr>0], "eGFR numeric value distribution", "egfr_dist_violin")
plot_violin_numeric_value(numeric_values_creatinine[numeric_values_creatinine>0], "creatinine numeric value distribution", "creatinine_dist_violin")
plot_violin_numeric_value(numeric_values_cr_cl[numeric_values_cr_cl>0], "creatinine clearance numeric value distribution", "cr_cl_dist_violin")