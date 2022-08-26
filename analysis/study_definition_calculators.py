from cohortextractor import StudyDefinition, patients
from codelists import *

study = StudyDefinition(
    default_expectations={
        "date": {"earliest": "2019-01-01", "latest": "today"},
        "rate": "uniform",
        "incidence": 0.5,
    },
    # define study index date
    index_date="2022-07-01",
    population=patients.satisfying(
        """
            registered AND
            NOT died AND
            (age >=18 AND age <=120) AND 
            (sex = 'M' OR sex = 'F')
        """,
        registered=patients.registered_as_of("index_date"),
        died=patients.died_from_any_cause(
            on_or_before="index_date",
            returning="binary_flag",
            return_expectations={"incidence": 0.1},
        ),
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
            "18-19": """ age >= 0 AND age < 20""",
            "20-29": """ age >=  20 AND age < 30""",
            "30-39": """ age >=  30 AND age < 40""",
            "40-49": """ age >=  40 AND age < 50""",
            "50-59": """ age >=  50 AND age < 60""",
            "60-69": """ age >=  60 AND age < 70""",
            "70-79": """ age >=  70 AND age < 80""",
            "80+": """ age >=  80 AND age < 120""",
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "missing": 0.005,
                    "18-19": 0.125,
                    "20-29": 0.125,
                    "30-39": 0.125,
                    "40-49": 0.125,
                    "50-59": 0.125,
                    "60-69": 0.125,
                    "70-79": 0.125,
                    "80+": 0.12,
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

    eGFR_numeric_value = patients.with_these_clinical_events(
                codelist=eGFR_numeric_value_codelist,
                on_or_before = "last_day_of_month(index_date)",
                returning="numeric_value",
                date_format="YYYY-MM-DD",
                include_date_of_match=True,
                return_expectations={
                    "float": {"distribution": "normal", "mean": 45.0, "stddev": 20},
                    "incidence": 0.5,
                },
            ),

    creatinine_clearance_numeric_value = patients.with_these_clinical_events(
                codelist=creatinine_clearance_numeric_value_codelist,
                on_or_before = "last_day_of_month(index_date)",
                returning="numeric_value",
                date_format="YYYY-MM-DD",
                include_date_of_match=True,
                return_expectations={
                    "float": {"distribution": "normal", "mean": 45.0, "stddev": 20},
                    "incidence": 0.5,
                },
            ),

    creatinine_numeric_value = patients.with_these_clinical_events(
            codelist=creatinine_numeric_value_codelist,
            on_or_before = "last_day_of_month(index_date)",
            returning="numeric_value",
            date_format="YYYY-MM-DD",
            include_date_of_match=True,
            return_expectations={
                "float": {"distribution": "normal", "mean": 45.0, "stddev": 20},
                "incidence": 0.5,
            },
        ),

    weight_numeric_value=patients.with_these_clinical_events(
        weight_codelist,
        on_or_before = "last_day_of_month(index_date)",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
                include_date_of_match=True,
        returning="numeric_value",
        return_expectations={
            "incidence": 0.8,
            "float": {"distribution": "normal", "mean": 70.0, "stddev": 10.0},
        },
    ),

    # creatinine numeric value before crcl.
    creatinine_numeric_value_before_crcl = patients.with_these_clinical_events(
                codelist=creatinine_numeric_value_codelist,
                on_or_before="creatinine_clearance_numeric_value_date",
                returning="numeric_value",
                date_format="YYYY-MM-DD",
                include_date_of_match=True,
                return_expectations={
                    "float": {"distribution": "normal", "mean": 45.0, "stddev": 20},
                    "incidence": 0.5,
                },
            ),
    
    creatinine_numeric_value_before_egfr = patients.with_these_clinical_events(
                codelist=creatinine_numeric_value_codelist,
                on_or_before="eGFR_numeric_value_date",
                returning="numeric_value",
                date_format="YYYY-MM-DD",
                include_date_of_match=True,
                return_expectations={
                    "float": {"distribution": "normal", "mean": 45.0, "stddev": 20},
                    "incidence": 0.5,
                },
            ),
    
    weight_before_crcl=patients.with_these_clinical_events(
        weight_codelist,
        on_or_before="creatinine_clearance_numeric_value_date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
                include_date_of_match=True,
        returning="numeric_value",
        return_expectations={
            "incidence": 0.8,
            "float": {"distribution": "normal", "mean": 70.0, "stddev": 10.0},
        },
    ),

  
)