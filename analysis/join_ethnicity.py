import pandas as pd
import os
import re
from pathlib import Path

OUTPUT_DIR = Path("output")


ethnicity_df = pd.read_csv('output/input_ethnicity.csv.gz')

def match_input_files(file: str) -> bool:
    """Checks if file name has format outputted by cohort extractor"""
    pattern = r"^input_20\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])_joined\.csv.gz"
    return True if re.match(pattern, file) else False



def get_date_input_file(file: str) -> str:
    """Gets the date in format YYYY-MM-DD from input file name string"""
    # check format
    if not match_input_files(file):
        raise Exception("Not valid input file format")

    else:
        date = result = re.search(r"input_(.*)_joined\.csv.gz", file)
        return date.group(1)

for file in OUTPUT_DIR.iterdir():
    if match_input_files(file.name):
        
        date = get_date_input_file(file.name)
        df = pd.read_csv(OUTPUT_DIR / file.name)
        merged_df = df.merge(ethnicity_df, how='left', on='patient_id')  
        print(file.name)      
        merged_df.to_csv(OUTPUT_DIR / f'input_joined_{date}.csv.gz')
