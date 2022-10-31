import pandas as pd

from utilities import OUTPUT_DIR, match_input_files, get_date_input_file

for file in (OUTPUT_DIR / "joined").iterdir():
    if match_input_files(file.name):
        df = pd.read_csv((OUTPUT_DIR / "joined") / file.name)
        date = get_date_input_file(file.name)

        acr_df = pd.read_csv(OUTPUT_DIR / f"input_numeric_values_full_{date}.csv.gz")

        merged_df = df.merge(acr_df, how="left", on="patient_id")
       
        # keep the new acr values.
        # merged_df = merged_df.drop([
        #     "creatinine_numeric_value_full_x",
        #     "cr_crl_numeric_value_full_x",
        #     "albumin_numeric_value_full_x",
        #     "acr_numeric_value_full_x",
        #     "eGFR_numeric_value_full_x",
        #     ], axis=1)
        
        # merged_df = merged_df.rename(columns={"creatinine_numeric_value_full_y": "creatinine_numeric_value_ful", "cr_crl_numeric_value_full_y": "cr_crl_numeric_value_full","albumin_numeric_value_full_y": "albumin_numeric_value_full", "acr_numeric_value_full_y": "acr_numeric_value_full", "acr_numeric_value_full_y": "acr_numeric_value_full", "eGFR_numeric_value_full_y": "eGFR_numeric_value_full_x"})
        merged_df.loc[:, ["creatinine_numeric_value_full", "cr_cl_numeric_value_full", "albumin_numeric_value_full", "acr_numeric_value_full", "eGFR_numeric_value_full"]] = merged_df.loc[:, ["creatinine_numeric_value_full", "cr_cl_numeric_value_full", "albumin_numeric_value_full", "acr_numeric_value_full", "eGFR_numeric_value_full"]].fillna(0)

        merged_df.to_csv(OUTPUT_DIR / "joined" / file.name, index=False)