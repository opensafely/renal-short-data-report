from cohortextractor import (
   codelist,
   codelist_from_csv,
   combine_codelists
)


eGFR_codelist = codelist_from_csv(
    "codelists/user-ss808-estimated-glomerular-filtration-rate-egfr-recorded-tests.csv",
    system="snomed",
    column="code"
)

eGFR_level_codelist = codelist_from_csv(
    "codelists/user-ss808-estimated-glomerular-filtration-rate-egfr-values.csv", 
    system="snomed", 
    column="code",
)

ethnicity_codelist = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-eth2001.csv",
    system="snomed",
    column="code",
    category_column="grouping_6_id"
)
  
creatinine_clearance_codelist = codelist_from_csv(
    "codelists/user-Louis-creatinine-clearance.csv",
    system="snomed",
    column="code",
)

creatinine_clearance_level_codelist = codelist_from_csv(
    "codelists/user-Louis-creatinine-clearance-level.csv",
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

height_codelist = codelist_from_csv(
    "codelists/opensafely-height-snomed.csv",
    system="snomed",
    column='code'
)

hypertension_codelist = codelist_from_csv(
    "codelists/opensafely-hypertension-snomed.csv", 
    system="snomed",
    column="id"
)

diabetes_t1_codelist = codelist_from_csv(
   "codelists/opensafely-type-1-diabetes.csv", 
   system="ctv3", 
   column="CTV3ID"
)

diabetes_t2_codelist = codelist_from_csv(
    "codelists/opensafely-type-2-diabetes.csv", 
    system="ctv3", 
    column="CTV3ID"
)

diabetes_unknown_type_codelist = codelist_from_csv(
    "codelists/opensafely-diabetes-unknown-type.csv", 
    system="ctv3", 
    column="CTV3ID"
)

diabetes_primis_codelist = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-diab.csv",
    system="snomed",
    column="code"
)
diabetes_resolved_primis_codelist = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-dmres.csv",
    system="snomed",
    column="code"
)

diabetes_any_codelist = combine_codelists(
    diabetes_t1_codelist,
    diabetes_t2_codelist,
    diabetes_unknown_type_codelist
)

