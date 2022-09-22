import pandas as pd

from utilities import OUTPUT_DIR, match_input_files, get_date_input_file

for file in (OUTPUT_DIR / "joined").iterdir():
    if match_input_files(file.name):
        df = pd.read_csv((OUTPUT_DIR / "joined") / file.name)
        date = get_date_input_file(file.name)

        acr_df = pd.read_csv(OUTPUT_DIR / f"input_acr_{date}.csv.gz")

        merged_df = df.merge(acr_df, how="left", on="patient_id")
     
        # keep the new acr values.
        merged_df = merged_df.drop([
            "acr_x",
            "acr_date_x",
            "acr_code_x",
            "acr_count_x",
            "acr_numeric_value_x",
            "acr_operator_x"
            ], axis=1)
        merged_df = merged_df.rename(columns={"acr_y": "acr", "acr_date_y": "acr_date","acr_code_y": "acr_code", "acr_count_y": "acr_count", "acr_numeric_value_y": "acr_numeric_value", "acr_operator": "acr_operator"})

        merged_df.to_csv(OUTPUT_DIR / "joined" / file.name)