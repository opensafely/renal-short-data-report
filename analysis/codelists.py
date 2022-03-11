from cohortextractor import (
    codelist,
    codelist_from_csv,
)


eGFR_tests_codes = codelist_from_csv(
    "codelists/user-ss808-estimated-glomerular-filtration-rate-egfr-recorded-tests.csv",
    system="snomed",
    column="code",
)

eGFR_values_codes = codelist_from_csv(
    "codelists/user-ss808-estimated-glomerular-filtration-rate-egfr-values.csv", 
    system="snomed", 
    column="code",
)

ethnicity_codes=codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-eth2001.csv",
    system="snomed",
    column="code",
    category_column="grouping_6_id"
)
