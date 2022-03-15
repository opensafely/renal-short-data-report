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

creatinine_codelist=codelist_from_csv(
        "codelists/user-bangzheng-creatinine.csv", 
        system="snomed",
        column="code"
)

weight_codelist = codelist_from_csv(
    "codelists/opensafely-weight-snomed.csv",
    system="snomed",
    column='code'
)
