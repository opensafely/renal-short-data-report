from cohortextractor import patients

from codelists import *

rrt_variables = dict(
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
)
renal = {'latest_renal_status', 'latest_renal_date'}
rrt_variables_no_renal = {i:rrt_variables[i] for i in rrt_variables if i not in renal}