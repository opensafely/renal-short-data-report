from cohortextractor import StudyDefinition, patients

from codelists import *

def generate_expectations_codes(codelist, incidence=0.5):
    expectations = {str(x): (1-incidence) / len(codelist) for x in codelist}
    expectations[None] = incidence
    return expectations

study = StudyDefinition(
    default_expectations={
        "date": {"earliest": "2019-01-01", "latest": "today"},
        "rate": "uniform",
        "incidence": 0.5,
    },
    # define study index date
    index_date="2019-01-01",
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
        age=patients.age_as_of(
            "index_date",
            return_expectations={
                "rate": "universal",
                "int": {"distribution": "population_ages"},
            },
        ),
        sex=patients.sex(
            return_expectations={
                "rate": "universal",
                "category": {"ratios": {"M": 0.49, "F": 0.5, "U": 0.01}},
            }
        ),
    ),
    acr = patients.with_these_clinical_events(
                codelist=acr_codelist,
                between=["index_date", "last_day_of_month(index_date)"],
                returning="binary_flag",
                date_format="YYYY-MM-DD",
                include_date_of_match=True,
                return_expectations={
                    "incidence": 0.5,
                    "date": {"earliest": "1900-01-01", "latest": "today"},
                },
        ),
    acr_code = patients.with_these_clinical_events(
        codelist=acr_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={
            "rate": "universal",
            "category": {"ratios": generate_expectations_codes(acr_codelist)},
        },
    ),
    acr_count = patients.with_these_clinical_events(
        codelist=acr_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="number_of_matches_in_period",
        return_expectations={
            "int": {"distribution": "poisson", "mean": 2},
            "incidence": 0.2,
        },
    ),
    acr_numeric_value = patients.with_these_clinical_events(
        codelist=acr_level_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="numeric_value",
        return_expectations={
            "float": {"distribution": "normal", "mean": 45.0, "stddev": 20},
            "incidence": 0.5,
        },
    ),
    acr_operator = patients.comparator_from(
        "acr_numeric_value",
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {  # ~, =, >= , > , < , <=
                    None: 0.10,
                    "~": 0.05,
                    "=": 0.65,
                    ">=": 0.05,
                    ">": 0.05,
                    "<": 0.05,
                    "<=": 0.05,
                }
            },
            "incidence": 0.80,
        },
    ),
)

