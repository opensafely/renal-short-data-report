import pandas as pd
import argparse
import glob
import pathlib
from collections import Counter

def create_table_1(paths, demographics):

    demographics_dict = {d: {} for d in demographics}
    demographics_dict_total = {d: {} for d in demographics}
    
    for path in paths:
        df = pd.read_csv(path, usecols=demographics + ["patient_id"])
        
        for i, row in df.iterrows():
            for d in demographics:
                if row[d]:
                    patient_id = row["patient_id"]
                
                    demographics_dict[d][patient_id] = row[d]
                

    for d in demographics:
        counts = dict(Counter([v for k, v in demographics_dict[d].items()]))
        demographics_dict_total[d] = counts
    
    reformed_dict = {}
    reformed_dict["total"] = sum(demographics_dict_total[demographics[0]].values())
    for outerKey, innerDict in demographics_dict_total.items():
        for innerKey, values in innerDict.items():
            
            reformed_dict[(outerKey,
                        innerKey)] = values

    
    return pd.DataFrame(reformed_dict, index=[0]).T

def get_path(*args):
    return pathlib.Path(*args).resolve()

def match_paths(pattern):
    return [get_path(x) for x in sorted(glob.glob(pattern))]

def parse_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "--study_def_paths",
        dest="study_def_paths",
        required=True,
        type=match_paths,
        help="Glob pattern for matching input files",
    )

    parser.add_argument(
        "--demographics",
        dest="demographics",
        required=True,
        help="List of strings representing variables to include",
    )
    
    return parser.parse_args()


def main():
    args = parse_args()
    paths = args.study_def_paths
    demographics = args.demographics.split(",")
  
    table_1 = create_table_1(paths, demographics)
    table_1.to_csv("output/table_1.csv")
   

    
main()