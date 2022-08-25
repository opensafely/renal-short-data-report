from cohortextractor import patients

from codelists import *

comorbidity_variables = dict(
    diabetes=patients.satisfying(
        """
        (
            diabetes_any_primis AND
            (NOT diabetes_resolved)
        ) 
    
        OR

        (
            diabetes_any_primis AND
            diabetes_resolved AND
            (diabetes_resolved_date < diabetes_any_date) OR (diabetes_resolved_date < diabetes_primis_date)
        )

        """,
        diabetes_any=patients.with_these_clinical_events(
            codelist=diabetes_any_codelist,
            on_or_before="index_date",
            returning="binary_flag",
            date_format="YYYY-MM-DD",
            include_date_of_match=True,
            return_expectations={
                "incidence": 0.5,
                "date": {"earliest": "1900-01-01", "latest": "today"},
            },
        ),
        diabetes_primis=patients.with_these_clinical_events(
            codelist=diabetes_primis_codelist,
            on_or_before="index_date",
            returning="binary_flag",
            date_format="YYYY-MM-DD",
            include_date_of_match=True,
            return_expectations={
                "incidence": 0.5,
                "date": {"earliest": "1900-01-01", "latest": "today"},
            },
        ),
        diabetes_any_primis=patients.satisfying(
            """
            diabetes_any OR diabetes_primis
            """
        ),
        diabetes_resolved=patients.with_these_clinical_events(
            codelist=diabetes_resolved_primis_codelist,
            on_or_before="index_date",
            returning="binary_flag",
            date_format="YYYY-MM-DD",
            include_date_of_match=True,
            return_expectations={
                "incidence": 0.5,
                "date": {"earliest": "1900-01-01", "latest": "today"},
            },
        ),
    ),
    hypertension=patients.with_these_clinical_events(
        codelist=hypertension_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        return_expectations={
            "incidence": 0.5,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    at_risk=patients.satisfying(
        """
        diabetes
        OR
        hypertension
        """
    ),
)