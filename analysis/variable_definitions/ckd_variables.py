from cohortextractor import patients

from codelists import *

ckd_variables = dict(
    ckd=patients.with_these_clinical_events(
        codelist=ckd_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.5,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ckd_code=patients.with_these_clinical_events(
        codelist=ckd_codelist,
        on_or_before="index_date",
        returning="code",
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"238318009": 0.5, "864311000000105": 0.5}},
        },
    ),
    ckd_primis_1_5=patients.with_these_clinical_events(
        codelist=primis_ckd_1_5_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.5,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ckd_primis_1_5_code=patients.with_these_clinical_events(
        codelist=primis_ckd_1_5_codelist,
        on_or_before="index_date",
        returning="code",
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"238318009": 0.5, "864311000000105": 0.5}},
        },
    ),
    ckd_primis_stage=patients.with_these_clinical_events(
        codelist=primis_ckd_stage,
        on_or_before="index_date",
        returning="category",
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "1": 0.2,
                    "2": 0.2,
                    "3": 0.2,
                    "4": 0.2,
                    "5": 0.1,
                }
            },
        },
    ),
    ckd_primis_stage_date=patients.date_of("ckd_primis_1_5", date_format="YYYY-MM-DD"),
    ckd_acr_category=patients.categorised_as(
        {
            "None": """
                acr_numeric_value_history=0
                """,
            "A1": """
                acr_numeric_value_history < 3 AND
                acr_numeric_value_history > 0 AND
                NOT acr_operator = ">" AND
                NOT acr_operator = ">=" AND
                NOT acr_operator = "<" AND
                NOT acr_operator = "<="
                """,
            "A2": """
                acr_numeric_value_history > 3 AND
                acr_numeric_value_history < 30 AND
                NOT acr_operator = ">" AND
                NOT acr_operator = ">=" AND
                NOT acr_operator = "<" AND
                NOT acr_operator = "<="
                """,
            "A3": """
                acr_numeric_value_history > 30 AND
                NOT acr_operator = "<" AND
                NOT acr_operator = "<="
                """,
            "Uncategorised": "DEFAULT",
        },
        acr_numeric_value_history=patients.with_these_clinical_events(
            codelist=acr_level_codelist,
            on_or_before="last_day_of_month(index_date)",
            returning="numeric_value",
            date_format="YYYY-MM-DD",
            include_date_of_match=True,
            return_expectations={
                "incidence": 0.5,
                "float": {"distribution": "normal", "mean": 25, "stddev": 5},
                "date": {"earliest": "1900-01-01", "latest": "today"},
            },
        ),
        acr_numeric_value_history_operator=patients.comparator_from(
            "acr_numeric_value_history",
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
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "A1": 0.2,
                    "A2": 0.2,
                    "A3": 0.1,
                    "Uncategorised": 0.1,
                    "None": 0.4,
                }
            },
        },
    ),
    egfr_numeric_value_history=patients.with_these_clinical_events(
        codelist=eGFR_numeric_value_codelist,
        on_or_before="last_day_of_month(index_date)",
        returning="numeric_value",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.5,
            "float": {"distribution": "normal", "mean": 25, "stddev": 5},
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    egfr_numeric_value_history_operator=patients.comparator_from(
        "egfr_numeric_value_history",
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
    egfr_numeric_value_90_before=patients.with_these_clinical_events(
        codelist=eGFR_numeric_value_codelist,
        on_or_before="egfr_numeric_value_history_date",
        returning="numeric_value",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.5,
            "float": {"distribution": "normal", "mean": 25, "stddev": 5},
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    egfr_numeric_value_90_before_operator=patients.comparator_from(
        "egfr_numeric_value_90_before",
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
    single_egfr=patients.satisfying(
        """
        egfr_numeric_value_history > 0 AND
        egfr_numeric_value_history < 60 AND
        NOT egfr_numeric_value_history_operator = "<" AND
        NOT egfr_numeric_value_history_operator = "<=" AND
        NOT egfr_numeric_value_history_operator = ">" AND
        NOT egfr_numeric_value_history_operator = ">=" AND
        (
            (
                egfr_numeric_value_90_before = 0 OR
                egfr_numeric_value_90_before >=60
            ) AND
            (
                NOT egfr_numeric_value_90_before_operator = "<" AND
                NOT egfr_numeric_value_90_before_operator = "<="
            )
        )
        """,
    ),
    ckd_egfr_category=patients.categorised_as(
        {
            "None": """
                egfr_numeric_value_history=0
                """,
            "G1": """
                egfr_numeric_value_history >= 90 AND
                egfr_numeric_value_90_before >= 90 AND
                NOT egfr_numeric_value_history_operator = "<" AND
                NOT egfr_numeric_value_history_operator = "<=" AND
                NOT egfr_numeric_value_90_before_operator = "<" AND
                NOT egfr_numeric_value_90_before_operator = "<="
                """,
            "G2": """
                egfr_numeric_value_history >= 60 AND
                egfr_numeric_value_history < 90 AND
                egfr_numeric_value_90_before >= 60 AND
                egfr_numeric_value_90_before < 90 AND
                NOT egfr_numeric_value_history_operator = "<" AND
                NOT egfr_numeric_value_history_operator = "<=" AND
                NOT egfr_numeric_value_90_before_operator = "<" AND
                NOT egfr_numeric_value_90_before_operator = "<=" AND
                NOT egfr_numeric_value_history_operator = ">" AND
                NOT egfr_numeric_value_history_operator = ">=" AND
                NOT egfr_numeric_value_90_before_operator = ">" AND
                NOT egfr_numeric_value_90_before_operator = ">="
                """,
            "G3a": """
                egfr_numeric_value_history >= 45 AND
                egfr_numeric_value_history < 60 AND
                egfr_numeric_value_90_before >= 45 AND
                egfr_numeric_value_90_before < 60 AND
                NOT egfr_numeric_value_history_operator = "<" AND
                NOT egfr_numeric_value_history_operator = "<=" AND
                NOT egfr_numeric_value_90_before_operator = "<" AND
                NOT egfr_numeric_value_90_before_operator = "<=" AND
                NOT egfr_numeric_value_history_operator = ">" AND
                NOT egfr_numeric_value_history_operator = ">=" AND
                NOT egfr_numeric_value_90_before_operator = ">" AND
                NOT egfr_numeric_value_90_before_operator = ">="
                """,
            "G3b": """
                egfr_numeric_value_history >= 30 AND
                egfr_numeric_value_history < 45 AND
                egfr_numeric_value_90_before >= 30 AND
                egfr_numeric_value_90_before < 45 AND
                NOT egfr_numeric_value_history_operator = "<" AND
                NOT egfr_numeric_value_history_operator = "<=" AND
                NOT egfr_numeric_value_90_before_operator = "<" AND
                NOT egfr_numeric_value_90_before_operator = "<=" AND
                NOT egfr_numeric_value_history_operator = ">" AND
                NOT egfr_numeric_value_history_operator = ">=" AND
                NOT egfr_numeric_value_90_before_operator = ">" AND
                NOT egfr_numeric_value_90_before_operator = ">="
                """,
            "G4": """
                egfr_numeric_value_history >= 15 AND
                egfr_numeric_value_history < 30 AND
                egfr_numeric_value_90_before >= 15 AND
                egfr_numeric_value_90_before < 30 AND
                NOT egfr_numeric_value_history_operator = "<" AND
                NOT egfr_numeric_value_history_operator = "<=" AND
                NOT egfr_numeric_value_90_before_operator = "<" AND
                NOT egfr_numeric_value_90_before_operator = "<=" AND
                NOT egfr_numeric_value_history_operator = ">" AND
                NOT egfr_numeric_value_history_operator = ">=" AND
                NOT egfr_numeric_value_90_before_operator = ">" AND
                NOT egfr_numeric_value_90_before_operator = ">="
                """,
            "G5": """
                egfr_numeric_value_history > 0 AND
                egfr_numeric_value_history < 15 AND
                egfr_numeric_value_90_before > 0 AND
                egfr_numeric_value_90_before < 15 AND
                NOT egfr_numeric_value_history_operator = "<" AND
                NOT egfr_numeric_value_history_operator = "<=" AND
                NOT egfr_numeric_value_90_before_operator = "<" AND
                NOT egfr_numeric_value_90_before_operator = "<=" AND
                NOT egfr_numeric_value_history_operator = ">" AND
                NOT egfr_numeric_value_history_operator = ">=" AND
                NOT egfr_numeric_value_90_before_operator = ">" AND
                NOT egfr_numeric_value_90_before_operator = ">="
                """,
            "Uncategorised": "DEFAULT",
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "G1": 0.3,
                    "G2": 0.1,
                    "G3a": 0.1,
                    "G3b": 0.1,
                    "G4": 0.1,
                    "Uncategorised": 0.05,
                    "None": 0.25,
                }
            },
        },
    ),
)
