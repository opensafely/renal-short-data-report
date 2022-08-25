from cohortextractor import (
    StudyDefinition,
    patients,
)

from variable_definitions.ukrr_variables import ukrr_variables
from codelists import *

study = StudyDefinition(
    default_expectations={
        "date": {"earliest": "1900-01-01", "latest": "today"},
        "rate": "uniform",
        "incidence": 0.5,
    },
    # End of the study period
    index_date="2021-12-31",
    population=patients.all(),
    
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
            on_or_before="2022-07-31",
            return_expectations={
                "category": {
                    "ratios": {"1": 0.4, "2": 0.4, "3": 0.2, "4": 0.2, "5": 0.2}
                },
                "incidence": 0.75,
            },
        ),
    ),
    

#########################################################################################################
#       incident RRT dates
########################################################################################################
# primary care
 # RRT 
    earliest_RRT=patients.with_these_clinical_events(
        codelist=RRT_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        ignore_missing_values=True,
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.2,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),


    # dialysis 
    earliest_dialysis=patients.with_these_clinical_events(
        codelist=dialysis_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        ignore_missing_values=True,
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.2,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),

    # kidney_tx 
    earliest_kidney_tx=patients.with_these_clinical_events(
        codelist=kidney_tx_codelist,
        on_or_before="index_date",
       returning="binary_flag",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        ignore_missing_values=True,
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.2,
            "date": {"earliest": "1900-01-01", "latest": "today"},
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
        between=["1900-01-01", "index_date"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    # dialysis
    earliest_op_dialysis_date = patients.outpatient_appointment_date(
        returning="date",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_procedures=dialysis_opcs4_codelist,
        between=["1900-01-01", "index_date"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    #RRT
    earliest_op_RRT_date = patients.outpatient_appointment_date(
        returning="date",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_procedures=RRT_opcs4_codelist,
        between=["1900-01-01", "index_date"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),

# Inpatient
    # tx
    earliest_ip_kidney_tx_diagnosis_date = patients.admitted_to_hospital(
        returning="date_admitted",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=kidney_tx_icd10_codelist,
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    earliest_ip_kidney_tx_procedure_date = patients.admitted_to_hospital(
        returning="date_admitted",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_procedures=kidney_tx_opcs4_codelist,
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    # dialysis
    earliest_ip_dialysis_diagnosis_date = patients.admitted_to_hospital(
        returning="date_admitted",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=dialysis_icd10_codelist,
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    earliest_ip_dialysis_procedure_date = patients.admitted_to_hospital(
        returning="date_admitted",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_procedures=dialysis_opcs4_codelist,
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    #RRT
    earliest_ip_RRT_diagnosis_date = patients.admitted_to_hospital(
        returning="date_admitted",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=RRT_icd10_codelist,
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ), 
    earliest_ip_RRT_procedure_date = patients.admitted_to_hospital(
        returning="date_admitted",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_procedures=RRT_opcs4_codelist,
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
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

    **ukrr_variables
   
)
