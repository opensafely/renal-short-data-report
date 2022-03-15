from cohortextractor import codelist_from_csv

creatinine_clearance_codelist = codelist_from_csv(
    "codelists/user-Louis-creatinine-clearance.csv",
    system="snomed",
    column="code",
)

creatinine_clearance_level_codelist = codelist_from_csv(
    "codelists/user-Louis-creatinine-clearance.csv",
    system="snomed",
    column="code",
)

height_codes_snomed = codelist_from_csv(
    "codelists/opensafely-height-snomed.csv",
    system="snomed",
    column='code'
)
weight_codes_snomed = codelist_from_csv(
    "codelists/opensafely-weight-snomed.csv",
    system="snomed",
    column='code'
)
