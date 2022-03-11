import pandas as pd
import os

ethnicity_df = pd.read_feather('output/measures/input_ethnicity.feather')

for file in os.listdir('output/measures'):
    if file.startswith('input_2'):
        file_path = os.path.join('output/measures', file)
        df = pd.read_feather(file_path)
        merged_df = df.merge(ethnicity_df, how='left', on='patient_id')        
        merged_df.to_feather(file_path)
