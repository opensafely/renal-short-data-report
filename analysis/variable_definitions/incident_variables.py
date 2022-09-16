from cohortextractor import patients

from codelists import *

incident_variables = dict(
    # primary care
 # RRT 
    earliest_RRT=patients.with_these_clinical_events(
        codelist=RRT_codelist,
        between=["1901-01-01", "2022-01-01"],
        returning="binary_flag",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.2,
            "date": {"earliest": "1901-01-01", "latest": "today"},
        },
    ),

    earliest_RRT_code=patients.with_these_clinical_events(
        codelist=RRT_codelist,
        between=["1901-01-01", "2022-01-01"],
        returning="code",
        find_first_match_in_period=True,
        return_expectations={
            "incidence": 0.2,
            "category": {"ratios": {"14S2.": 0.5, "7A600": 0.5}},
        },
    ),


    # dialysis 
    earliest_dialysis=patients.with_these_clinical_events(
        codelist=dialysis_codelist,
        between=["1901-01-01", "2022-01-01"],
        returning="binary_flag",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.2,
            "date": {"earliest": "1901-01-01", "latest": "today"},
        },
    ),

    earliest_dialysis_code=patients.with_these_clinical_events(
        codelist=dialysis_codelist,
        between=["1901-01-01", "2022-01-01"],
        returning="code",
        find_first_match_in_period=True,
        return_expectations={
            "incidence": 0.2,
            "category": {"ratios": {"7A602": 0.5, "7A600": 0.5}},
        },
    ),

    # kidney_tx 
    earliest_kidney_tx=patients.with_these_clinical_events(
        codelist=kidney_tx_codelist,
        between=["1901-01-01", "2022-01-01"],
       returning="binary_flag",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.2,
            "date": {"earliest": "1901-01-01", "latest": "today"},
        },
    ),

    earliest_kidney_tx_code=patients.with_these_clinical_events(
        codelist=kidney_tx_codelist,
        between=["1901-01-01", "2022-01-01"],
       returning="code",
        find_first_match_in_period=True,
        return_expectations={
            "incidence": 0.2,
            "category": {"ratios": {"14S2.": 0.5, "7B00.": 0.5}},
        },
    ),


    incident_rrt_date=patients.minimum_of(
        "earliest_dialysis_date", "earliest_kidney_tx_date", "earliest_RRT_date"
        ),


#Picking most recent status
#patients are assigned to the first condition they satisfy
incident_rrt_status = patients.categorised_as(
    {
        "None"      : """
                    (NOT earliest_dialysis) 
                    AND (NOT earliest_kidney_tx) 
                    AND (NOT earliest_RRT)
                    """,
        "Dialysis"  : """
                    earliest_dialysis_date=incident_rrt_date 
                    AND
                    earliest_kidney_tx_date!=incident_rrt_date
                    """,
        "Transplant" : """
                    earliest_kidney_tx_date=incident_rrt_date
                    AND
                    earliest_dialysis_date!=incident_rrt_date 
                    """,
        "RRT_unknown"  : """
                    earliest_dialysis_date=incident_rrt_date 
                    OR
                    earliest_kidney_tx_date=incident_rrt_date
                    OR
                    earliest_RRT_date=incident_rrt_date
                    """,
        "Uncategorised" : "DEFAULT"
    },
    return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "None": 0.6,
                    "Dialysis": 0.1,
                    "Transplant": 0.1,
                    "RRT_unknown": 0.1,
                    "Uncategorised": 0.1,
                }
            },
        },
    ),

# secondary care
 # outpatients
    # tx
    earliest_op_kidney_tx_date = patients.outpatient_appointment_date(
        returning="date",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_procedures=kidney_tx_opcs4_codelist,
        between=["1901-01-01", "today"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1901-01-01", "latest": "today"},
        },
    ),
    # dialysis
    earliest_op_dialysis_date = patients.outpatient_appointment_date(
        returning="date",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_procedures=dialysis_opcs4_codelist,
        between=["1901-01-01", "today"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1901-01-01", "latest": "today"},
        },
    ),
    #RRT
    earliest_op_RRT_date = patients.outpatient_appointment_date(
        returning="date",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_procedures=RRT_opcs4_codelist,
        between=["1901-01-01", "today"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1901-01-01", "latest": "today"},
        },
    ),

# Inpatient
    # tx
    earliest_ip_kidney_tx_diagnosis_date = patients.admitted_to_hospital(
        returning="date_admitted",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=kidney_tx_icd10_codelist,
        between=["1901-01-01", "today"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1901-01-01", "latest": "today"},
        },
    ),
    earliest_ip_kidney_tx_procedure_date = patients.admitted_to_hospital(
        returning="date_admitted",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_procedures=kidney_tx_opcs4_codelist,
        between=["1901-01-01", "today"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1901-01-01", "latest": "today"},
        },
    ),
    # dialysis
    earliest_ip_dialysis_diagnosis_date = patients.admitted_to_hospital(
        returning="date_admitted",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=dialysis_icd10_codelist,
        between=["1901-01-01", "today"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1901-01-01", "latest": "today"},
        },
    ),
    earliest_ip_dialysis_procedure_date = patients.admitted_to_hospital(
        returning="date_admitted",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_procedures=dialysis_opcs4_codelist,
        between=["1901-01-01", "today"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1901-01-01", "latest": "today"},
        },
    ),
    #RRT
    earliest_ip_RRT_diagnosis_date = patients.admitted_to_hospital(
        returning="date_admitted",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=RRT_icd10_codelist,
        between=["1901-01-01", "today"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1901-01-01", "latest": "today"},
        },
    ), 
    earliest_ip_RRT_procedure_date = patients.admitted_to_hospital(
        returning="date_admitted",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_procedures=RRT_opcs4_codelist,
        between=["1901-01-01", "today"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1901-01-01", "latest": "today"},
        },
    ),

    incident_rrt_date_secondary=patients.minimum_of(
        "earliest_op_kidney_tx_date", "earliest_op_dialysis_date", "earliest_op_RRT_date",
        "earliest_ip_kidney_tx_diagnosis_date", "earliest_ip_kidney_tx_procedure_date",
        "earliest_ip_dialysis_diagnosis_date", "earliest_ip_dialysis_procedure_date",
        "earliest_ip_RRT_diagnosis_date", "earliest_ip_RRT_procedure_date"
    ),
 
    incident_rrt_status_secondary=patients.categorised_as(
        {
            "None":     """
                        incident_rrt_date_secondary=""
                        """,
            "Dialysis": """
                        (earliest_op_dialysis_date=incident_rrt_date_secondary OR earliest_ip_dialysis_diagnosis_date=incident_rrt_date_secondary OR earliest_ip_dialysis_procedure_date=incident_rrt_date_secondary)
                        AND NOT
                        (earliest_op_kidney_tx_date=incident_rrt_date_secondary OR earliest_ip_kidney_tx_diagnosis_date=incident_rrt_date_secondary OR earliest_ip_kidney_tx_procedure_date=incident_rrt_date_secondary)
                        """,
            "Transplant": """
                        (earliest_op_kidney_tx_date=incident_rrt_date_secondary OR earliest_ip_kidney_tx_diagnosis_date=incident_rrt_date_secondary OR earliest_ip_kidney_tx_procedure_date=incident_rrt_date_secondary)
                        AND NOT
                        (earliest_op_dialysis_date=incident_rrt_date_secondary OR earliest_ip_dialysis_diagnosis_date=incident_rrt_date_secondary OR earliest_ip_dialysis_procedure_date=incident_rrt_date_secondary) 
                        """,
            "RRT_unknown": """
                        (earliest_op_dialysis_date=incident_rrt_date_secondary OR earliest_ip_dialysis_diagnosis_date=incident_rrt_date_secondary OR earliest_ip_dialysis_procedure_date=incident_rrt_date_secondary)
                        OR
                        (earliest_op_kidney_tx_date=incident_rrt_date_secondary OR earliest_ip_kidney_tx_diagnosis_date=incident_rrt_date_secondary OR earliest_ip_kidney_tx_procedure_date=incident_rrt_date_secondary)
                        OR
                        (earliest_op_RRT_date=incident_rrt_date_secondary OR earliest_ip_RRT_diagnosis_date=incident_rrt_date_secondary OR earliest_ip_RRT_procedure_date=incident_rrt_date_secondary)
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
            }
        }
),
)