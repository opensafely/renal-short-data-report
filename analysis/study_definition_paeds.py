# only interested in population as at 1/1/2020 as only have 31/12/2019 prevalent cohort for paeds
# keeping 1st of the month to be consistent with other study definition

from cohortextractor import StudyDefinition, patients

from ukrr_variables import ukrr_variables
from codelists import *

demographics = ["age_band", "sex", "region", "imd", "ethnicity"]

study = StudyDefinition(
    default_expectations={
        "date": {"earliest": "2019-01-01", "latest": "today"},
        "rate": "uniform",
        "incidence": 0.5,
    },
    # define study index date
    index_date="2020-01-01",
    population=patients.satisfying(
        """
            registered AND
            NOT died AND
            (age <18) AND 
            (sex = 'M' OR sex = 'F')
        """,
        registered=patients.registered_as_of("index_date"),
        died=patients.died_from_any_cause(
            on_or_before="index_date",
            returning="binary_flag",
            return_expectations={"incidence": 0.1},
        ),
    ),
    practice=patients.registered_practice_as_of(
        "index_date",
        returning="pseudo_id",
        return_expectations={
            "int": {"distribution": "normal", "mean": 25, "stddev": 5},
            "incidence": 0.5,
        },
    ),
    age=patients.age_as_of(
        "index_date",
        return_expectations={
            "rate": "universal",
            "int": {"distribution": "population_ages"},
        },
    ),
    age_band=patients.categorised_as(
        {
            "missing": "DEFAULT",
            "0-3": """ age >= 0 AND age < 4""",
            "4-7": """ age >=  4 AND age < 8""",
            "8-11": """ age >=  8 AND age < 12""",
            "12-15": """ age >=  12 AND age < 16""",
            "16-17": """ age >=  16 AND age < 18""",
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "missing": 0.005,
                    "0-3": 0.199,
                    "4-7": 0.199,
                    "8-11": 0.199,
                    "12-15": 0.199,
                    "16-17": 0.199,
                }
            },
        },
    ),
    sex=patients.sex(
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"M": 0.49, "F": 0.5, "U": 0.01}},
        }
    ),
    region=patients.registered_practice_as_of(
        "index_date",
        returning="nuts1_region_name",
        return_expectations={
            "category": {
                "ratios": {
                    "North East": 0.1,
                    "North West": 0.1,
                    "Yorkshire and the Humber": 0.1,
                    "East Midlands": 0.1,
                    "West Midlands": 0.1,
                    "East of England": 0.1,
                    "London": 0.2,
                    "South East": 0.2,
                }
            }
        },
    ),
    imd=patients.categorised_as(
        {
            "0": "DEFAULT",
            "1": """index_of_multiple_deprivation >=0 AND index_of_multiple_deprivation < 32844*1/5""",
            "2": """index_of_multiple_deprivation >= 32844*1/5 AND index_of_multiple_deprivation < 32844*2/5""",
            "3": """index_of_multiple_deprivation >= 32844*2/5 AND index_of_multiple_deprivation < 32844*3/5""",
            "4": """index_of_multiple_deprivation >= 32844*3/5 AND index_of_multiple_deprivation < 32844*4/5""",
            "5": """index_of_multiple_deprivation >= 32844*4/5 AND index_of_multiple_deprivation < 32844""",
        },
        index_of_multiple_deprivation=patients.address_as_of(
            "index_date",
            returning="index_of_multiple_deprivation",
            round_to_nearest=100,
        ),
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "0": 0.05,
                    "1": 0.19,
                    "2": 0.19,
                    "3": 0.19,
                    "4": 0.19,
                    "5": 0.19,
                }
            },
        },
    ),

        # Ethnicity
    ethnicity=patients.categorised_as(
        {
            "Missing": "DEFAULT",
            "White": "eth='1' OR (NOT eth AND ethnicity_sus='1')",
            "Mixed": "eth='2' OR (NOT eth AND ethnicity_sus='2')",
            "South Asian": "eth='3' OR (NOT eth AND ethnicity_sus='3')",
            "Black": "eth='4' OR (NOT eth AND ethnicity_sus='4')",
            "Other": "eth='5' OR (NOT eth AND ethnicity_sus='5')",
        },
        return_expectations={
            "category": {
                "ratios": {
                    "White": 0.2,
                    "Mixed": 0.2,
                    "South Asian": 0.2,
                    "Black": 0.2,
                    "Other": 0.2,
                }
            },
            "incidence": 0.4,
        },
        ethnicity_sus=patients.with_ethnicity_from_sus(
            returning="group_6",
            use_most_frequent_code=True,
            return_expectations={
                "category": {
                    "ratios": {"1": 0.2, "2": 0.2, "3": 0.2, "4": 0.2, "5": 0.2}
                },
                "incidence": 0.4,
            },
        ),
        eth=patients.with_these_clinical_events(
            ethnicity_codelist,
            returning="category",
            find_last_match_in_period=True,
            on_or_before="index_date",
            return_expectations={
                "category": {
                    "ratios": {"1": 0.4, "2": 0.4, "3": 0.2, "4": 0.2, "5": 0.2}
                },
                "incidence": 0.75,
            },
        ),
    ),

    ### Renal variables ###
   
    ckd=patients.with_these_clinical_events(
        codelist=ckd_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.5,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ckd_code=patients.with_these_clinical_events(
        codelist=ckd_codelist,
        on_or_before="index_date",
        returning="code",
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"238318009": 0.5, "864311000000105": 0.5}},
        },
    ),
    ckd_primis_1_5=patients.with_these_clinical_events(
        codelist=primis_ckd_1_5_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.5,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ckd_primis_1_5_code=patients.with_these_clinical_events(
        codelist=primis_ckd_1_5_codelist,
        on_or_before="index_date",
        returning="code",
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"238318009": 0.5, "864311000000105": 0.5}},
        },
    ),
    ckd_primis_stage=patients.with_these_clinical_events(
        codelist=primis_ckd_stage,
        on_or_before="index_date",
        returning="category",
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"1": 0.5, "2": 0.5}},
        },
    ),
    # RRT
    RRT=patients.with_these_clinical_events(
        codelist=RRT_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.2,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    RRT_code=patients.with_these_clinical_events(
        codelist=RRT_codelist,
        on_or_before="index_date",
        returning="code",
        return_expectations={
            "category": {"ratios": {"14S2.": 0.5, "7A600": 0.5}},
            "incidence": 0.2,
        },
    ),
    # dialysis
    # defaults to the lastest match
    dialysis=patients.with_these_clinical_events(
        codelist=dialysis_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.2,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    dialysis_code=patients.with_these_clinical_events(
        codelist=dialysis_codelist,
        on_or_before="index_date",
        returning="code",
        return_expectations={
            "category": {"ratios": {"7A602": 0.5, "7A600": 0.5}},
            "incidence": 0.2,
        },
    ),
    # kidney_tx
    # defaults to the lastest match
    kidney_tx=patients.with_these_clinical_events(
        codelist=kidney_tx_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.2,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    kidney_tx_code=patients.with_these_clinical_events(
        codelist=kidney_tx_codelist,
        on_or_before="index_date",
        returning="code",
        return_expectations={
            "category": {"ratios": {"14S2.": 0.5, "7B00.": 0.5}},
            "incidence": 0.2,
        },
    ),
    latest_renal_date=patients.maximum_of(
        "dialysis_date", "kidney_tx_date", "RRT_date", "ckd_date", "ckd_primis_1_5_date"
    ),
    latest_rrt_date=patients.maximum_of("dialysis_date", "kidney_tx_date", "RRT_date"),
    # Picking most recent status
    # patients are assigned to the first condition they satisfy, so define RRT modalities first
    latest_renal_status=patients.categorised_as(
        {
            "None": """
                        (NOT dialysis) 
                        AND (NOT kidney_tx) 
                        AND (NOT RRT)
                        AND (NOT ckd_primis_1_5)
                        AND (NOT ckd)
                        """,
            "Dialysis": """
                        dialysis_date=latest_renal_date 
                        AND
                        kidney_tx_date!=latest_renal_date
                        """,
            "Transplant": """
                        kidney_tx_date=latest_renal_date
                        AND
                        dialysis_date!=latest_renal_date 
                        """,
            "RRT_unknown": """
                        dialysis_date=latest_renal_date 
                        OR
                        kidney_tx_date=latest_renal_date
                        OR
                        RRT_date=latest_renal_date
                        """,
            "CKD5": """
                        ckd_primis_1_5_date=latest_renal_date
                        AND
                        ckd_primis_stage="5"
                        """,
            "CKD4": """
                        ckd_primis_1_5_date=latest_renal_date
                        AND
                        ckd_primis_stage="4"
                        """,
            "CKD3": """
                        ckd_primis_1_5_date=latest_renal_date
                        AND
                        ckd_primis_stage="3"
                        """,
            "CKD2": """
                        ckd_primis_1_5_date=latest_renal_date
                        AND
                        ckd_primis_stage="2"
                        """,
            "CKD1": """
                        ckd_primis_1_5_date=latest_renal_date
                        AND
                        ckd_primis_stage="1"
                        """,
            "CKD_unknown": """
                        ckd_primis_1_5_date=latest_renal_date
                        OR
                        ckd_date=latest_renal_date
                        """,
            "Uncategorised": "DEFAULT",
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "None": 0.4,
                    "Dialysis": 0.1,
                    "Transplant": 0.1,
                    "RRT_unknown": 0.1,
                    "CKD5": 0.1,
                    "CKD4": 0.05,
                    "CKD3": 0.05,
                    "CKD2": 0.04,
                    "CKD1": 0.04,
                    "CKD_unknown": 0.01,
                    "Uncategorised": 0.01,
                }
            },
        },
    ),
    latest_rrt_status=patients.categorised_as(
        {
            "None": """
                        (NOT dialysis) 
                        AND (NOT kidney_tx) 
                        AND (NOT RRT)
                        """,
            "Dialysis": """
                        dialysis_date=latest_rrt_date 
                        AND
                        kidney_tx_date!=latest_rrt_date
                        """,
            "Transplant": """
                        kidney_tx_date=latest_rrt_date
                        AND
                        dialysis_date!=latest_rrt_date 
                        """,
            "RRT_unknown": """
                        dialysis_date=latest_rrt_date 
                        OR
                        kidney_tx_date=latest_rrt_date
                        OR
                        RRT_date=latest_rrt_date
                        """,
            "Uncategorised": "DEFAULT",
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "None": 0.39,
                    "Dialysis": 0.25,
                    "Transplant": 0.25,
                    "RRT_unknown": 0.1,
                    "Uncategorised": 0.01,
                }
            },
        },
    ),
    ### Secondary care codes ####
    # outpatients
    # can't retrieve code for outpat appointments
    # can't look for diagnoses, only procedures
    # can also look for nephrology appointments
    op_kidney_tx=patients.outpatient_appointment_date(
        returning="binary_flag",
        with_these_procedures=kidney_tx_opcs4_codelist,
        between=["1900-01-01", "index_date"],
        return_expectations={
            "incidence": 0.3,
        },
    ),
    op_kidney_tx_date=patients.outpatient_appointment_date(
        returning="date",
        date_format="YYYY-MM-DD",
        with_these_procedures=kidney_tx_opcs4_codelist,
        between=["1900-01-01", "index_date"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    op_dialysis=patients.outpatient_appointment_date(
        returning="binary_flag",
        with_these_procedures=dialysis_opcs4_codelist,
        between=["1900-01-01", "index_date"],
        return_expectations={
            "incidence": 0.3,
        },
    ),
    op_dialysis_date=patients.outpatient_appointment_date(
        returning="date",
        date_format="YYYY-MM-DD",
        with_these_procedures=dialysis_opcs4_codelist,
        between=["1900-01-01", "index_date"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    op_RRT=patients.outpatient_appointment_date(
        returning="binary_flag",
        with_these_procedures=RRT_opcs4_codelist,
        between=["1900-01-01", "index_date"],
        return_expectations={
            "incidence": 0.3,
        },
    ),
    op_RRT_date=patients.outpatient_appointment_date(
        returning="date",
        date_format="YYYY-MM-DD",
        with_these_procedures=RRT_opcs4_codelist,
        between=["1900-01-01", "index_date"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    op_renal=patients.outpatient_appointment_date(
        returning="binary_flag",
        with_these_treatment_function_codes=codelist(["361"], system=None),
        between=["1900-01-01", "index_date"],
        return_expectations={
            "incidence": 0.3,
        },
    ),
    op_renal_date=patients.outpatient_appointment_date(
        returning="date",
        date_format="YYYY-MM-DD",
        with_these_treatment_function_codes=codelist(["361"], system=None),
        between=["1900-01-01", "index_date"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    # inpatients
    # consider adding: retrieve primary diagnosis, treatment function code, days in critical care (to indicate acute dialysis)
    ip_kidney_tx_diagnosis=patients.admitted_to_hospital(
        returning="binary_flag",
        find_last_match_in_period=True,
        with_these_diagnoses=kidney_tx_icd10_codelist,
        on_or_before="index_date",
        return_expectations={
            "incidence": 0.3,
        },
    ),
    ip_kidney_tx_diagnosis_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=kidney_tx_icd10_codelist,
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_kidney_tx_procedure=patients.admitted_to_hospital(
        returning="binary_flag",
        find_last_match_in_period=True,
        with_these_procedures=kidney_tx_opcs4_codelist,
        on_or_before="index_date",
        return_expectations={
            "incidence": 0.3,
        },
    ),
    ip_kidney_tx_procedure_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_procedures=kidney_tx_opcs4_codelist,
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_dialysis_diagnosis=patients.admitted_to_hospital(
        returning="binary_flag",
        find_last_match_in_period=True,
        with_these_diagnoses=dialysis_icd10_codelist,
        on_or_before="index_date",
        return_expectations={
            "incidence": 0.3,
        },
    ),
    ip_dialysis_diagnosis_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=dialysis_icd10_codelist,
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_dialysis_procedure=patients.admitted_to_hospital(
        returning="binary_flag",
        find_last_match_in_period=True,
        with_these_procedures=dialysis_opcs4_codelist,
        on_or_before="index_date",
        return_expectations={
            "incidence": 0.3,
        },
    ),
    ip_dialysis_procedure_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_procedures=dialysis_opcs4_codelist,
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_RRT_diagnosis=patients.admitted_to_hospital(
        returning="binary_flag",
        find_last_match_in_period=True,
        with_these_diagnoses=RRT_icd10_codelist,
        on_or_before="index_date",
        return_expectations={
            "incidence": 0.3,
        },
    ),
    ip_RRT_diagnosis_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=RRT_icd10_codelist,
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_RRT_procedure=patients.admitted_to_hospital(
        returning="binary_flag",
        find_last_match_in_period=True,
        with_these_procedures=RRT_opcs4_codelist,
        on_or_before="index_date",
        return_expectations={
            "incidence": 0.3,
        },
    ),
    ip_RRT_procedure_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_procedures=RRT_opcs4_codelist,
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_renal=patients.admitted_to_hospital(
        returning="binary_flag",
        find_last_match_in_period=True,
        with_admission_treatment_function_code="361",
        between=["1900-01-01", "index_date"],
        return_expectations={
            "incidence": 0.3,
        },
    ),
    ip_renal_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_admission_treatment_function_code="361",
        between=["1900-01-01", "index_date"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    latest_rrt_date_secondary=patients.maximum_of(
        "op_kidney_tx_date",
        "op_dialysis_date",
        "op_RRT_date",
        "ip_kidney_tx_diagnosis_date",
        "ip_kidney_tx_procedure_date",
        "ip_dialysis_diagnosis_date",
        "ip_dialysis_procedure_date",
        "ip_RRT_diagnosis_date",
        "ip_RRT_procedure_date",
    ),
    # categorised as will assign patients to the first condition they satisfy, so subsequent conditions only apply to patients not already categorised.
    latest_rrt_status_secondary=patients.categorised_as(
        {
            "None": """
                        (NOT op_kidney_tx) 
                        AND (NOT op_dialysis) 
                        AND (NOT op_RRT)
                        AND (NOT ip_kidney_tx_diagnosis)
                        AND (NOT ip_kidney_tx_procedure)
                        AND (NOT ip_dialysis_diagnosis)
                        AND (NOT ip_dialysis_procedure)
                        AND (NOT ip_RRT_diagnosis)
                        AND (NOT ip_RRT_procedure)
                        """,
            "Dialysis": """
                        (op_dialysis_date=latest_rrt_date_secondary OR ip_dialysis_diagnosis_date=latest_rrt_date_secondary OR ip_dialysis_procedure_date=latest_rrt_date_secondary)
                        AND NOT
                        (op_kidney_tx_date=latest_rrt_date_secondary OR ip_kidney_tx_diagnosis_date=latest_rrt_date_secondary OR ip_kidney_tx_procedure_date=latest_rrt_date_secondary)
                        """,
            "Transplant": """
                        (op_kidney_tx_date=latest_rrt_date_secondary OR ip_kidney_tx_diagnosis_date=latest_rrt_date_secondary OR ip_kidney_tx_procedure_date=latest_rrt_date_secondary)
                        AND NOT
                        (op_dialysis_date=latest_rrt_date_secondary OR ip_dialysis_diagnosis_date=latest_rrt_date_secondary OR ip_dialysis_procedure_date=latest_rrt_date_secondary) 
                        """,
            "RRT_unknown": """
                        (op_dialysis_date=latest_rrt_date_secondary OR ip_dialysis_diagnosis_date=latest_rrt_date_secondary OR ip_dialysis_procedure_date=latest_rrt_date_secondary)
                        OR
                        (op_kidney_tx_date=latest_rrt_date_secondary OR ip_kidney_tx_diagnosis_date=latest_rrt_date_secondary OR ip_kidney_tx_procedure_date=latest_rrt_date_secondary)
                        OR
                        (op_RRT_date=latest_rrt_date_secondary OR ip_RRT_diagnosis_date=latest_rrt_date_secondary OR ip_RRT_procedure_date=latest_rrt_date_secondary)
                        """,
            "Uncategorised": "DEFAULT",
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "None": 0.39,
                    "Dialysis": 0.25,
                    "Transplant": 0.25,
                    "RRT_unknown": 0.1,
                    "Uncategorised": 0.01,
                }
            },
        },
    ),
    # CKD ICD 10 codes
    ip_ckd1_diagnosis_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=codelist(["N181"], system="icd10"),
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_ckd2_diagnosis_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=codelist(["N182"], system="icd10"),
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_ckd3_diagnosis_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=codelist(["N183"], system="icd10"),
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_ckd4_diagnosis_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=codelist(["N184"], system="icd10"),
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_ckd5_diagnosis_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=codelist(["N185"], system="icd10"),
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_ckd_unknown_diagnosis_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=codelist(["N18", "N189"], system="icd10"),
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    latest_ckd_date_secondary=patients.maximum_of(
        "ip_ckd1_diagnosis_date",
        "ip_ckd2_diagnosis_date",
        "ip_ckd3_diagnosis_date",
        "ip_ckd4_diagnosis_date",
        "ip_ckd5_diagnosis_date",
        "ip_ckd_unknown_diagnosis_date",
    ),
    # Picking most recent CKD status from ICD codes
    # patients are assigned to the first condition they satisfy, so define RRT modalities first
    latest_ckd_status_secondary=patients.categorised_as(
        {
            "RRT": """
                        latest_rrt_status_secondary != "None"
                        """,
            "None": """
                        latest_ckd_date_secondary=""
                        """,
            "CKD5": """
                        ip_ckd5_diagnosis_date=latest_ckd_date_secondary
                        """,
            "CKD4": """
                        ip_ckd4_diagnosis_date=latest_ckd_date_secondary
                        """,
            "CKD3": """
                        ip_ckd3_diagnosis_date=latest_ckd_date_secondary
                        """,
            "CKD2": """
                        ip_ckd2_diagnosis_date=latest_ckd_date_secondary
                        """,
            "CKD1": """
                        ip_ckd1_diagnosis_date=latest_ckd_date_secondary
                        """,
            "CKD_unknown": """
                        ip_ckd_unknown_diagnosis_date=latest_ckd_date_secondary
                        """,
            "Uncategorised": "DEFAULT",
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "None": 0.3,
                    "RRT": 0.1,
                    "CKD5": 0.1,
                    "CKD4": 0.1,
                    "CKD3": 0.1,
                    "CKD2": 0.1,
                    "CKD1": 0.1,
                    "CKD_unknown": 0.09,
                    "Uncategorised": 0.01,
                }
            },
        },
    ),

 **ukrr_variables

)

