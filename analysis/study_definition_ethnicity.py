from cohortextractor import (
    StudyDefinition,
    patients,
)

from codelists import ethnicity_codelist

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
)
