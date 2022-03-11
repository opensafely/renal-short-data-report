import pathlib

import pandas


path_to_output = pathlib.Path("output")

input_ethnicity = pandas.read_feather(path_to_output / "input_ethnicity.feather")

for path in path_to_output.iterdir():
    if not path.name.startswith("input") or path.name == "input_ethnicity.feather":
        continue

    input_other = pandas.read_feather(path)
    input_other = input_other.merge(input_ethnicity, how="left", on="patient_id")

    # If the old path was "output/input_2021-01-01.feather", then the new
    # path will be "output/input_2021-01-01_merged.feather".
    new_path = path_to_output / f"{input_other.stem}_merged{input_other.suffix}"
    input_other.to_feather(new_path)