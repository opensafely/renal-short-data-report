from cohortextractor import (
    StudyDefinition,
    patients,
)

from codelists import ethnicity_codes

study = StudyDefinition(
    default_expectations={
        "date": {"earliest": "1900-01-01", "latest": "today"},
        "rate": "uniform",
    },
    # End of the study period
    index_date="2021-12-31",
    population=patients.all(),
    # Ethnicity
    ethnicity=patients.with_these_clinical_events(
        ethnicity_codes,
        returning="category",
        find_last_match_in_period=True, # most recent code
        on_or_before="index_date",
        return_expectations={
            "category": {"ratios": {"1": 0.2, "2": 0.2, "3": 0.2, "4": 0.2, "5": 0.2}},
            "incidence": 0.75,
        },
    ),
)
