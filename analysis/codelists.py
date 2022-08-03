from cohortextractor import codelist, codelist_from_csv, combine_codelists

acr_codelist = codelist_from_csv(
    "codelists/user-Louis-albumin-to-creatinine-ratio-tests.csv",
    system="snomed",
    column="code",
)
acr_level_codelist = codelist_from_csv(
    "codelists/user-Louis-albumin-to-creatinine-ratio-tests.csv",
    system="snomed",
    column="code",
)
albumin_codelist = codelist_from_csv(
    "codelists/user-Louis-albumin-tests.csv",
    system="snomed",
    column="code",
)

albumin_level_codelist = codelist_from_csv(
    "codelists/user-Louis-albumin-tests.csv",
    system="snomed",
    column="code",
)

cystatin_c_codelist = codelist_from_csv(
    "codelists/user-Louis-cystatin-c-tests.csv",
    system="snomed",
    column="code",
)

cystatin_c_level_codelist = codelist_from_csv(
    "codelists/user-Louis-cystatin-c-tests.csv",
    system="snomed",
    column="code",
)

eGFR_codelist = codelist_from_csv(
    "codelists/user-ss808-estimated-glomerular-filtration-rate-egfr-recorded-tests.csv",
    system="snomed",
    column="code",
)

eGFR_numeric_value_codelist = codelist_from_csv(
    "codelists/user-bangzheng-egfr-value-shortlist.csv",
    system="snomed",
    column="code",
)

ethnicity_codelist = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-eth2001.csv",
    system="snomed",
    column="code",
    category_column="grouping_6_id",
)

creatinine_clearance_codelist = codelist_from_csv(
    "codelists/user-Louis-creatinine-clearance.csv",
    system="snomed",
    column="code",
)

creatinine_clearance_numeric_value_codelist = codelist_from_csv(
    "codelists/user-bangzheng-creatinine-clearance-shortlist.csv",
    system="snomed",
    column="code",
)

creatinine_codelist = codelist_from_csv(
    "codelists/user-bangzheng-creatinine.csv", system="snomed", column="code"
)

creatinine_numeric_value_codelist = codelist_from_csv(
    "codelists/user-bangzheng-creatinine-value-shortlist.csv", system="snomed", column="code"
)

weight_codelist = codelist_from_csv(
    "codelists/opensafely-weight-snomed.csv", system="snomed", column="code"
)

height_codelist = codelist_from_csv(
    "codelists/opensafely-height-snomed.csv", system="snomed", column="code"
)

hypertension_codelist = codelist_from_csv(
    "codelists/opensafely-hypertension-snomed.csv", system="snomed", column="id"
)

diabetes_t1_codelist = codelist_from_csv(
    "codelists/opensafely-type-1-diabetes.csv", system="ctv3", column="CTV3ID"
)

diabetes_t2_codelist = codelist_from_csv(
    "codelists/opensafely-type-2-diabetes.csv", system="ctv3", column="CTV3ID"
)

diabetes_unknown_type_codelist = codelist_from_csv(
    "codelists/opensafely-diabetes-unknown-type.csv", system="ctv3", column="CTV3ID"
)

diabetes_primis_codelist = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-diab.csv", system="snomed", column="code"
)
diabetes_resolved_primis_codelist = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-dmres.csv", system="snomed", column="code"
)

diabetes_any_codelist = combine_codelists(
    diabetes_t1_codelist, diabetes_t2_codelist, diabetes_unknown_type_codelist
)

RRT_codelist = codelist_from_csv(
    "codelists/opensafely-renal-replacement-therapy.csv",
    system="ctv3",
    column="CTV3ID"
)

dialysis_codelist = codelist_from_csv(
    "codelists/opensafely-dialysis.csv",
    system="ctv3",
    column="CTV3ID",
)

kidney_tx_codelist = codelist_from_csv(
    "codelists/opensafely-kidney-transplant.csv",
    system="ctv3",
    column="CTV3ID",
)

all_rrt_codes = combine_codelists(RRT_codelist, dialysis_codelist, kidney_tx_codelist)

ckd_codelist = codelist_from_csv(
    "codelists/opensafely-chronic-kidney-disease-snomed.csv",
    system="snomed",
    column="id"
)

primis_ckd_1_5_codelist = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-ckd15.csv",
    system="snomed",
    column="code"
)

primis_ckd_stage = codelist_from_csv(
    "codelists/user-Louis-ckd-stage.csv",
    system="snomed",
    column="code",
    category_column="stage"
)

primis_ckd_3_5_codelist = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-ckd35.csv",
    system="snomed",
    column="code"
)
#just a single code for this one so haven't created a list
kidney_tx_icd10_codelist=codelist(["Z940"], system="icd10")

kidney_tx_opcs4_codelist = codelist_from_csv(
    "codelists/user-viyaasan-kidney-transplant-opcs-4.csv",
    system="opcs4",
    column="code"
)

dialysis_icd10_codelist = codelist_from_csv(
    "codelists/ukrr-dialysis.csv",
    system="icd10",
    column="code"
)

dialysis_opcs4_codelist = codelist_from_csv(
    "codelists/ukrr-dialysis-opcs-4.csv",
    system="opcs4",
    column="code"
)

#Combining tx and dialysis codelists into RRT codelist, and adding tx failure code
RRT_icd10_codelist = combine_codelists(
    kidney_tx_icd10_codelist,
    dialysis_icd10_codelist,
    codelist(["T861"], system="icd10")
)

#Same for OPCS4, also PD catheter removal and bilateral nephrectomy
RRT_opcs4_codelist = combine_codelists(
    kidney_tx_opcs4_codelist,
    dialysis_opcs4_codelist,
    codelist(["M023", "M026", "M027", "X412"], system="opcs4")
)

#CKD ICD codelist to look at pts in UKRR but not in secondary care
CKD_icd10_codelist = codelist_from_csv(
    "codelists/ukrr-chronic-kidney-disease-icd-10.csv",
    system="icd10",
    column="code"
)
