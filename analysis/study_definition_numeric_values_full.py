from cohortextractor import StudyDefinition, patients, codelist
from variable_definitions.test_variables import path_tests
from variable_definitions.test_variables import codelists


def create_path_variables(path_tests):
    def make_variable(test):
        return {
            f"{test}_numeric_value_full": patients.with_these_clinical_events(
                codelist=codelists[test],
                between=["index_date", "last_day_of_month(index_date)"],
                returning="numeric_value",
                return_expectations={
                    "float": {"distribution": "normal", "mean": 45.0, "stddev": 20},
                    "incidence": 0.5,
                },
            ),

        }

    variables = {}
    for test in path_tests:
        variables.update(make_variable(test))
    return variables


study = StudyDefinition(
    default_expectations={
        "date": {"earliest": "2019-01-01", "latest": "today"},
        "rate": "uniform",
        "incidence": 0.5,
    },
    # define study index date
    index_date="2019-01-01",
    population=patients.all(),
    **create_path_variables(path_tests)
)
