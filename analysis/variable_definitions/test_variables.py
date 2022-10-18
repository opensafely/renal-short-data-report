from cohortextractor import patients
path_tests = ["creatinine", "cr_cl", "albumin", "acr", "eGFR"]
from codelists import *

def generate_expectations_codes(codelist, incidence=0.5):
    expectations = {str(x): (1-incidence) / len(codelist) for x in codelist}
    expectations[None] = incidence
    return expectations

codelists = {
    "creatinine": creatinine_codelist,
    "cr_cl": creatinine_clearance_codelist,
    "albumin": albumin_codelist,
    "acr": acr_codelist,
    "eGFR": eGFR_codelist,
}

codelists_numeric = {
    "creatinine": creatinine_numeric_value_codelist,
    "cr_cl": creatinine_clearance_numeric_value_codelist,
    "albumin": albumin_level_codelist,
    "acr": acr_level_codelist,
    "eGFR": eGFR_numeric_value_codelist,
}


def create_path_variables(path_tests):
    def make_variable(test):
        return {
            f"{test}": patients.with_these_clinical_events(
                codelist=codelists[test],
                between=["index_date", "last_day_of_month(index_date)"],
                returning="binary_flag",
                date_format="YYYY-MM-DD",
                include_date_of_match=True,
                return_expectations={
                    "incidence": 0.5,
                    "date": {"earliest": "1900-01-01", "latest": "today"},
                },
            ),
            f"{test}_code": patients.with_these_clinical_events(
                codelist=codelists[test],
                between=["index_date", "last_day_of_month(index_date)"],
                returning="code",
                return_expectations={
                    "rate": "universal",
                    "category": {"ratios": generate_expectations_codes(codelists[test])},
                },
            ),
            f"{test}_count": patients.with_these_clinical_events(
                codelist=codelists[test],
                between=["index_date", "last_day_of_month(index_date)"],
                returning="number_of_matches_in_period",
                return_expectations={
                    "int": {"distribution": "poisson", "mean": 2},
                    "incidence": 0.2,
                },
            ),
            f"{test}_numeric_value": patients.with_these_clinical_events(
                codelist=codelists_numeric[test],
                between=["index_date", "last_day_of_month(index_date)"],
                returning="numeric_value",
                return_expectations={
                    "float": {"distribution": "normal", "mean": 45.0, "stddev": 20},
                    "incidence": 0.5,
                },
            ),
            f"{test}_operator": patients.comparator_from(
                f"{test}_numeric_value",
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
        }

    variables = {}
    for test in path_tests:
        variables.update(make_variable(test))
    return variables

test_variables = dict(
    **create_path_variables(path_tests),
    height=patients.with_these_clinical_events(
        height_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        find_last_match_in_period=True,
        returning="numeric_value",
        return_expectations={
            "incidence": 0.8,
            "float": {"distribution": "normal", "mean": 70.0, "stddev": 10.0},
        },
    ),
    weight=patients.with_these_clinical_events(
        weight_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        find_last_match_in_period=True,
        returning="numeric_value",
        return_expectations={
            "incidence": 0.8,
            "float": {"distribution": "normal", "mean": 70.0, "stddev": 10.0},
        },
    ),
    # weight in 6 months before creatinine
    weight_before_creatinine=patients.with_these_clinical_events(
        weight_codelist,
        between=["creatinine_date - 6 months", "creatinine_date"],
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        returning="binary_flag",
        return_expectations={
            "incidence": 0.8,
        },
    ),
)
