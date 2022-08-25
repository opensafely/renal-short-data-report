from cohortextractor import patients

from codelists import *

secondary_care_variables = dict(
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
)
