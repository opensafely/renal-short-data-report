from cohortextractor import StudyDefinition, patients, Measure

from codelists import *

demographics = ["age_band", "sex", "region", "imd", "ethnicity"]
path_tests = ["creatinine", "cr_cl", "albumin", "acr", "eGFR"]

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
                    "category": {
                        "ratios": {"1000731000000107": 0.5, "1000981000000109": 0.5}
                    },
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
    ),
    practice=patients.registered_practice_as_of(
        "index_date",
        returning="pseudo_id",
        return_expectations={
            "int": {"distribution": "normal", "mean": 25, "stddev": 5},
            "incidence": 0.5,
        },
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
    region=patients.registered_practice_as_of(
        "index_date",
        returning="nuts1_region_name",
        return_expectations={
            "category": {
                "ratios": {
                    "North East": 0.1,
                    "North West": 0.1,
                    "Yorkshire and the Humber": 0.1,
                    "East Midlands": 0.1,
                    "West Midlands": 0.1,
                    "East of England": 0.1,
                    "London": 0.2,
                    "South East": 0.2,
                }
            }
        },
    ),
    imd=patients.categorised_as(
        {
            "0": "DEFAULT",
            "1": """index_of_multiple_deprivation >=0 AND index_of_multiple_deprivation < 32844*1/5""",
            "2": """index_of_multiple_deprivation >= 32844*1/5 AND index_of_multiple_deprivation < 32844*2/5""",
            "3": """index_of_multiple_deprivation >= 32844*2/5 AND index_of_multiple_deprivation < 32844*3/5""",
            "4": """index_of_multiple_deprivation >= 32844*3/5 AND index_of_multiple_deprivation < 32844*4/5""",
            "5": """index_of_multiple_deprivation >= 32844*4/5 AND index_of_multiple_deprivation < 32844""",
        },
        index_of_multiple_deprivation=patients.address_as_of(
            "index_date",
            returning="index_of_multiple_deprivation",
            round_to_nearest=100,
        ),
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "0": 0.05,
                    "1": 0.19,
                    "2": 0.19,
                    "3": 0.19,
                    "4": 0.19,
                    "5": 0.19,
                }
            },
        },
    ),
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
    **create_path_variables(path_tests),
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
        egfr_numeric_value_history=patients.with_these_clinical_events(
            codelist=eGFR_numeric_value_codelist,
            on_or_before="last_day_of_month(index_date)",
            returning="numeric_value",
            date_format="YYYY-MM-DD",
            include_date_of_match=True,
            return_expectations={
                "incidence": 0.5,
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
            "category": {"ratios": {"1": 0.5, "2": 0.5}},
        },
    ),
    # RRT
    RRT=patients.with_these_clinical_events(
        codelist=RRT_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.2,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    RRT_code=patients.with_these_clinical_events(
        codelist=RRT_codelist,
        on_or_before="index_date",
        returning="code",
        return_expectations={
            "category": {"ratios": {"14S2.": 0.5, "7A600": 0.5}},
            "incidence": 0.2,
        },
    ),
    # dialysis
    # defaults to the lastest match
    dialysis=patients.with_these_clinical_events(
        codelist=dialysis_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.2,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    dialysis_code=patients.with_these_clinical_events(
        codelist=dialysis_codelist,
        on_or_before="index_date",
        returning="code",
        return_expectations={
            "category": {"ratios": {"7A602": 0.5, "7A600": 0.5}},
            "incidence": 0.2,
        },
    ),
    # kidney_tx
    # defaults to the lastest match
    kidney_tx=patients.with_these_clinical_events(
        codelist=kidney_tx_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.2,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    kidney_tx_code=patients.with_these_clinical_events(
        codelist=kidney_tx_codelist,
        on_or_before="index_date",
        returning="code",
        return_expectations={
            "category": {"ratios": {"14S2.": 0.5, "7B00.": 0.5}},
            "incidence": 0.2,
        },
    ),
    latest_renal_date=patients.maximum_of(
        "dialysis_date",
        "kidney_tx_date",
        "RRT_date",
        "ckd_date",
        "ckd_primis_1_5_date",
    ),
    latest_rrt_date=patients.maximum_of("dialysis_date", "kidney_tx_date", "RRT_date"),
    # Picking most recent status
    # patients are assigned to the first condition they satisfy, so define RRT modalities first
    latest_renal_status=patients.categorised_as(
        {
            "None": """
                        (NOT dialysis) 
                        AND (NOT kidney_tx) 
                        AND (NOT RRT)
                        AND (NOT ckd_primis_1_5)
                        AND (NOT ckd)
                        """,
            "Dialysis": """
                        dialysis_date=latest_renal_date 
                        AND
                        kidney_tx_date!=latest_renal_date
                        """,
            "Transplant": """
                        kidney_tx_date=latest_renal_date
                        AND
                        dialysis_date!=latest_renal_date 
                        """,
            "RRT_unknown": """
                        dialysis_date=latest_renal_date 
                        OR
                        kidney_tx_date=latest_renal_date
                        OR
                        RRT_date=latest_renal_date
                        """,
            "CKD5": """
                        ckd_primis_1_5_date=latest_renal_date
                        AND
                        ckd_primis_stage="5"
                        """,
            "CKD4": """
                        ckd_primis_1_5_date=latest_renal_date
                        AND
                        ckd_primis_stage="4"
                        """,
            "CKD3": """
                        ckd_primis_1_5_date=latest_renal_date
                        AND
                        ckd_primis_stage="3"
                        """,
            "CKD2": """
                        ckd_primis_1_5_date=latest_renal_date
                        AND
                        ckd_primis_stage="2"
                        """,
            "CKD1": """
                        ckd_primis_1_5_date=latest_renal_date
                        AND
                        ckd_primis_stage="1"
                        """,
            "CKD_unknown": """
                        ckd_primis_1_5_date=latest_renal_date
                        OR
                        ckd_date=latest_renal_date
                        """,
            "Uncategorised": "DEFAULT",
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "None": 0.4,
                    "Dialysis": 0.1,
                    "Transplant": 0.1,
                    "RRT_unknown": 0.1,
                    "CKD5": 0.1,
                    "CKD4": 0.05,
                    "CKD3": 0.05,
                    "CKD2": 0.04,
                    "CKD1": 0.04,
                    "CKD_unknown": 0.01,
                    "Uncategorised": 0.01,
                }
            },
        },
    ),
    latest_rrt_status=patients.categorised_as(
        {
            "None": """
                        (NOT dialysis) 
                        AND (NOT kidney_tx) 
                        AND (NOT RRT)
                        """,
            "Dialysis": """
                        dialysis_date=latest_rrt_date 
                        AND
                        kidney_tx_date!=latest_rrt_date
                        """,
            "Transplant": """
                        kidney_tx_date=latest_rrt_date
                        AND
                        dialysis_date!=latest_rrt_date 
                        """,
            "RRT_unknown": """
                        dialysis_date=latest_rrt_date 
                        OR
                        kidney_tx_date=latest_rrt_date
                        OR
                        RRT_date=latest_rrt_date
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
            },
        },
    ),
    ### Secondary care codes ####
    # outpatients
    # can't retrieve code for outpat appointments
    # can't look for diagnoses, only procedures
    # can also look for nephrology appointments
    op_kidney_tx=patients.outpatient_appointment_date(
        returning="binary_flag",
        with_these_procedures=kidney_tx_opcs4_codelist,
        between=["1900-01-01", "index_date"],
        return_expectations={
            "incidence": 0.3,
        },
    ),
    op_kidney_tx_date=patients.outpatient_appointment_date(
        returning="date",
        date_format="YYYY-MM-DD",
        with_these_procedures=kidney_tx_opcs4_codelist,
        between=["1900-01-01", "index_date"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    op_dialysis=patients.outpatient_appointment_date(
        returning="binary_flag",
        with_these_procedures=dialysis_opcs4_codelist,
        between=["1900-01-01", "index_date"],
        return_expectations={
            "incidence": 0.3,
        },
    ),
    op_dialysis_date=patients.outpatient_appointment_date(
        returning="date",
        date_format="YYYY-MM-DD",
        with_these_procedures=dialysis_opcs4_codelist,
        between=["1900-01-01", "index_date"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    op_RRT=patients.outpatient_appointment_date(
        returning="binary_flag",
        with_these_procedures=RRT_opcs4_codelist,
        between=["1900-01-01", "index_date"],
        return_expectations={
            "incidence": 0.3,
        },
    ),
    op_RRT_date=patients.outpatient_appointment_date(
        returning="date",
        date_format="YYYY-MM-DD",
        with_these_procedures=RRT_opcs4_codelist,
        between=["1900-01-01", "index_date"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    op_renal=patients.outpatient_appointment_date(
        returning="binary_flag",
        with_these_treatment_function_codes=codelist(["361"], system=None),
        between=["1900-01-01", "index_date"],
        return_expectations={
            "incidence": 0.3,
        },
    ),
    op_renal_date=patients.outpatient_appointment_date(
        returning="date",
        date_format="YYYY-MM-DD",
        with_these_treatment_function_codes=codelist(["361"], system=None),
        between=["1900-01-01", "index_date"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    # inpatients
    # consider adding: retrieve primary diagnosis, treatment function code, days in critical care (to indicate acute dialysis)
    ip_kidney_tx_diagnosis=patients.admitted_to_hospital(
        returning="binary_flag",
        find_last_match_in_period=True,
        with_these_diagnoses=kidney_tx_icd10_codelist,
        on_or_before="index_date",
        return_expectations={
            "incidence": 0.3,
        },
    ),
    ip_kidney_tx_diagnosis_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=kidney_tx_icd10_codelist,
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_kidney_tx_procedure=patients.admitted_to_hospital(
        returning="binary_flag",
        find_last_match_in_period=True,
        with_these_procedures=kidney_tx_opcs4_codelist,
        on_or_before="index_date",
        return_expectations={
            "incidence": 0.3,
        },
    ),
    ip_kidney_tx_procedure_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_procedures=kidney_tx_opcs4_codelist,
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_dialysis_diagnosis=patients.admitted_to_hospital(
        returning="binary_flag",
        find_last_match_in_period=True,
        with_these_diagnoses=dialysis_icd10_codelist,
        on_or_before="index_date",
        return_expectations={
            "incidence": 0.3,
        },
    ),
    ip_dialysis_diagnosis_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=dialysis_icd10_codelist,
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_dialysis_procedure=patients.admitted_to_hospital(
        returning="binary_flag",
        find_last_match_in_period=True,
        with_these_procedures=dialysis_opcs4_codelist,
        on_or_before="index_date",
        return_expectations={
            "incidence": 0.3,
        },
    ),
    ip_dialysis_procedure_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_procedures=dialysis_opcs4_codelist,
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_RRT_diagnosis=patients.admitted_to_hospital(
        returning="binary_flag",
        find_last_match_in_period=True,
        with_these_diagnoses=RRT_icd10_codelist,
        on_or_before="index_date",
        return_expectations={
            "incidence": 0.3,
        },
    ),
    ip_RRT_diagnosis_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=RRT_icd10_codelist,
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_RRT_procedure=patients.admitted_to_hospital(
        returning="binary_flag",
        find_last_match_in_period=True,
        with_these_procedures=RRT_opcs4_codelist,
        on_or_before="index_date",
        return_expectations={
            "incidence": 0.3,
        },
    ),
    ip_RRT_procedure_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_procedures=RRT_opcs4_codelist,
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_renal=patients.admitted_to_hospital(
        returning="binary_flag",
        find_last_match_in_period=True,
        with_admission_treatment_function_code="361",
        between=["1900-01-01", "index_date"],
        return_expectations={
            "incidence": 0.3,
        },
    ),
    ip_renal_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_admission_treatment_function_code="361",
        between=["1900-01-01", "index_date"],
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    latest_rrt_date_secondary=patients.maximum_of(
        "op_kidney_tx_date",
        "op_dialysis_date",
        "op_RRT_date",
        "ip_kidney_tx_diagnosis_date",
        "ip_kidney_tx_procedure_date",
        "ip_dialysis_diagnosis_date",
        "ip_dialysis_procedure_date",
        "ip_RRT_diagnosis_date",
        "ip_RRT_procedure_date",
    ),
    # categorised as will assign patients to the first condition they satisfy, so subsequent conditions only apply to patients not already categorised.
    latest_rrt_status_secondary=patients.categorised_as(
        {
            "None": """
                        (NOT op_kidney_tx) 
                        AND (NOT op_dialysis) 
                        AND (NOT op_RRT)
                        AND (NOT ip_kidney_tx_diagnosis)
                        AND (NOT ip_kidney_tx_procedure)
                        AND (NOT ip_dialysis_diagnosis)
                        AND (NOT ip_dialysis_procedure)
                        AND (NOT ip_RRT_diagnosis)
                        AND (NOT ip_RRT_procedure)
                        """,
            "Dialysis": """
                        (op_dialysis_date=latest_rrt_date_secondary OR ip_dialysis_diagnosis_date=latest_rrt_date_secondary OR ip_dialysis_procedure_date=latest_rrt_date_secondary)
                        AND NOT
                        (op_kidney_tx_date=latest_rrt_date_secondary OR ip_kidney_tx_diagnosis_date=latest_rrt_date_secondary OR ip_kidney_tx_procedure_date=latest_rrt_date_secondary)
                        """,
            "Transplant": """
                        (op_kidney_tx_date=latest_rrt_date_secondary OR ip_kidney_tx_diagnosis_date=latest_rrt_date_secondary OR ip_kidney_tx_procedure_date=latest_rrt_date_secondary)
                        AND NOT
                        (op_dialysis_date=latest_rrt_date_secondary OR ip_dialysis_diagnosis_date=latest_rrt_date_secondary OR ip_dialysis_procedure_date=latest_rrt_date_secondary) 
                        """,
            "RRT_unknown": """
                        (op_dialysis_date=latest_rrt_date_secondary OR ip_dialysis_diagnosis_date=latest_rrt_date_secondary OR ip_dialysis_procedure_date=latest_rrt_date_secondary)
                        OR
                        (op_kidney_tx_date=latest_rrt_date_secondary OR ip_kidney_tx_diagnosis_date=latest_rrt_date_secondary OR ip_kidney_tx_procedure_date=latest_rrt_date_secondary)
                        OR
                        (op_RRT_date=latest_rrt_date_secondary OR ip_RRT_diagnosis_date=latest_rrt_date_secondary OR ip_RRT_procedure_date=latest_rrt_date_secondary)
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
            },
        },
    ),
    # CKD ICD 10 codes
    ip_ckd1_diagnosis_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=codelist(["N181"], system="icd10"),
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_ckd2_diagnosis_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=codelist(["N182"], system="icd10"),
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_ckd3_diagnosis_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=codelist(["N183"], system="icd10"),
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_ckd4_diagnosis_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=codelist(["N184"], system="icd10"),
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_ckd5_diagnosis_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=codelist(["N185"], system="icd10"),
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    ip_ckd_unknown_diagnosis_date=patients.admitted_to_hospital(
        returning="date_admitted",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        with_these_diagnoses=codelist(["N18", "N189"], system="icd10"),
        on_or_before="index_date",
        return_expectations={
            "rate": "uniform",
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    latest_ckd_date_secondary=patients.maximum_of(
        "ip_ckd1_diagnosis_date",
        "ip_ckd2_diagnosis_date",
        "ip_ckd3_diagnosis_date",
        "ip_ckd4_diagnosis_date",
        "ip_ckd5_diagnosis_date",
        "ip_ckd_unknown_diagnosis_date",
    ),
    # Picking most recent CKD status from ICD codes
    # patients are assigned to the first condition they satisfy, so define RRT modalities first
    latest_ckd_status_secondary=patients.categorised_as(
        {
            "RRT": """
                        latest_rrt_status_secondary != "None"
                        """,
            "None": """
                        latest_ckd_date_secondary=""
                        """,
            "CKD5": """
                        ip_ckd5_diagnosis_date=latest_ckd_date_secondary
                        """,
            "CKD4": """
                        ip_ckd4_diagnosis_date=latest_ckd_date_secondary
                        """,
            "CKD3": """
                        ip_ckd3_diagnosis_date=latest_ckd_date_secondary
                        """,
            "CKD2": """
                        ip_ckd2_diagnosis_date=latest_ckd_date_secondary
                        """,
            "CKD1": """
                        ip_ckd1_diagnosis_date=latest_ckd_date_secondary
                        """,
            "CKD_unknown": """
                        ip_ckd_unknown_diagnosis_date=latest_ckd_date_secondary
                        """,
            "Uncategorised": "DEFAULT",
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "None": 0.3,
                    "RRT": 0.1,
                    "CKD5": 0.1,
                    "CKD4": 0.1,
                    "CKD3": 0.1,
                    "CKD2": 0.1,
                    "CKD1": 0.1,
                    "CKD_unknown": 0.09,
                    "Uncategorised": 0.01,
                }
            },
        },
    ),
)


measures = []

for pop in ["population", "at_risk"]:
    for test in path_tests:

        measures.extend(
            [
                Measure(
                    id=f"{test}_{pop}_rate",
                    numerator=test,
                    denominator=pop,
                    group_by=["practice"],
                ),
                Measure(
                    id=f"{test}_code_{pop}_rate",
                    numerator=test,
                    denominator=pop,
                    group_by=[f"{test}_code"],
                ),
                Measure(
                    id=f"{test}_stage_{pop}_rate",
                    numerator=test,
                    denominator=pop,
                    group_by=["ckd_primis_stage"],
                ),
                Measure(
                    id=f"{test}_biochemical_stage_{pop}_rate",
                    numerator=test,
                    denominator=pop,
                    group_by=["ckd_egfr_category", "ckd_acr_category"],
                ),
                
            ]
        )

        for d in demographics:

            m_dem = Measure(
                id=f"{test}_{d}_{pop}_rate",
                numerator=test,
                denominator=pop,
                group_by=[d],
            )

            measures.extend([m_dem])

    for d in demographics:
        m_rrt = Measure(
            id=f"RRT_{d}_{pop}_rate", numerator="RRT", denominator=pop, group_by=[d]
        )

        m_dialysis = Measure(
            id=f"dialysis_{d}_{pop}_rate",
            numerator="dialysis",
            denominator=pop,
            group_by=[d],
        )

        m_kidney_tx = Measure(
            id=f"kidney_tx_{d}_{pop}_rate",
            numerator="kidney_tx",
            denominator=pop,
            group_by=[d],
        )

        m_ckd = Measure(
            id=f"ckd_rate", numerator="ckd", denominator="population", group_by=[d]
        )
        m_ckd_1_5 = Measure(
            id=f"ckd_primis_1_5_rate",
            numerator="ckd_primis_1_5",
            denominator="population",
            group_by=[d],
        )

    measures.extend([m_rrt, m_dialysis, m_ckd, m_ckd_1_5, m_kidney_tx])

    measures.extend(
        [
            Measure(
                id=f"ckd_{pop}_rate",
                numerator="ckd",
                denominator=pop,
                group_by=["practice"],
            ),
            Measure(
                id=f"ckd_primis_1_5_{pop}_rate",
                numerator="ckd_primis_1_5",
                denominator=pop,
                group_by=["practice"],
            ),
            Measure(
                id=f"ckd_primis_1_5_stage_{pop}_practice_rate",
                numerator="ckd_primis_1_5",
                denominator=pop,
                group_by=["practice", "ckd_primis_stage"],
            ),
            Measure(
                id=f"ckd_primis_1_5_stage_{pop}_rate",
                numerator="ckd_primis_1_5",
                denominator=pop,
                group_by=["ckd_primis_stage"],
            ),
            Measure(
                id=f"ckd_primis_1_5_stage_{pop}_ethnicity_rate",
                numerator="ckd_primis_1_5",
                denominator=pop,
                group_by=["ethnicity"],
            ),
            Measure(
                id=f"ckd_primis_1_5_stage_{pop}_age_band_rate",
                numerator="ckd_primis_1_5",
                denominator=pop,
                group_by=["age_band"],
            ),
            Measure(
                id=f"ckd_primis_1_5_stage_{pop}_sex_rate",
                numerator="ckd_primis_1_5",
                denominator=pop,
                group_by=["sex"],
            ),
            Measure(
                id=f"RRT_{pop}_rate",
                numerator="RRT",
                denominator=pop,
                group_by=["practice"],
            ),
            Measure(
                id=f"dialysis_{pop}_rate",
                numerator="dialysis",
                denominator=pop,
                group_by=["practice"],
            ),
            Measure(
                id=f"kidney_tx_{pop}_rate",
                numerator="kidney_tx",
                denominator=pop,
                group_by=["practice"],
            ),
            Measure(
                id=f"renal_status_{pop}_rate",
                numerator="population",
                denominator=pop,
                group_by=["latest_renal_status"],
            ),
            Measure(
                id=f"weight_before_creatinine_stage_rate",
                numerator="weight_before_creatinine",
                denominator="population",
                group_by="ckd_primis_stage",
            ),
        ]
    )

    if pop == "population":
        measures.append(
            Measure(
                id=f"weight_before_creatinine_{pop}_rate",
                numerator="weight_before_creatinine",
                denominator=pop,
                group_by=pop,
            )
        )
    else:
        measures.append(
            Measure(
                id=f"weight_before_creatinine_{pop}_rate",
                numerator="weight_before_creatinine",
                denominator="population",
                group_by=pop,
            )
        )
