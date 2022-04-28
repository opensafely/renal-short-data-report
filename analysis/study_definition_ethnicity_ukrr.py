from cohortextractor import (
    StudyDefinition,
    patients,
)

from ukrr_variables import ukrr_variables
from codelists import *

study = StudyDefinition(
    default_expectations={
        "date": {"earliest": "1900-01-01", "latest": "today"},
        "rate": "uniform",
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
            on_or_before="index_date",
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

    earliest_renal_date=patients.minimum_of(
        "earliest_dialysis_date", "earliest_kidney_tx_date", "earliest_RRT_date"
        ),


#Picking most recent status
#patients are assigned to the first condition they satisfy, so define RRT modalities first
earliest_renal_status = patients.categorised_as(
    {
        "None"      : """
                    (NOT earliest_dialysis) 
                    AND (NOT earliest_kidney_tx) 
                    AND (NOT earliest_RRT)
                    """,
        "Dialysis"  : """
                    earliest_dialysis_date=earliest_renal_date 
                    AND
                    earliest_kidney_tx_date!=earliest_renal_date
                    """,
        "Transplant" : """
                    earliest_kidney_tx_date=earliest_renal_date
                    AND
                    earliest_dialysis_date!=earliest_renal_date 
                    """,
        "RRT_unknown"  : """
                    dialysis_date=earliest_renal_date 
                    OR
                    kidney_tx_date=earliest_renal_date
                    OR
                    RRT_date=earliest_renal_date
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

    **ukrr_variables
   
)
