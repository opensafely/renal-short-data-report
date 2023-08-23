from cohortextractor import StudyDefinition, patients, Measure
from variable_definitions.demographic_variables import demographic_variables
from variable_definitions.test_variables import test_variables, path_tests
from variable_definitions.ckd_variables import ckd_variables
from variable_definitions.comorbidity_variables import comorbidity_variables
from variable_definitions.rrt_variables import rrt_variables
from scripts.variables import demographics


from codelists import dialysis_codelist, RRT_codelist, kidney_tx_codelist




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
    **demographic_variables,
    **test_variables,
    **comorbidity_variables,
    **ckd_variables,

    dialysis=patients.with_these_clinical_events(
        codelist=dialysis_codelist,
        on_or_before="last_day_of_month(index_date)",
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
        on_or_before="last_day_of_month(index_date)",
        returning="code",
        return_expectations={
            "category": {"ratios": {"7A602": 0.5, "7A600": 0.5}},
            "incidence": 0.2,
        },
    ),
    RRT=patients.with_these_clinical_events(
        codelist=RRT_codelist,
        on_or_before="last_day_of_month(index_date)",
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
        on_or_before="last_day_of_month(index_date)",
        returning="code",
        return_expectations={
            "category": {"ratios": {"14S2.": 0.5, "7A600": 0.5}},
            "incidence": 0.2,
        },
    ),

    kidney_tx=patients.with_these_clinical_events(
        codelist=kidney_tx_codelist,
        on_or_before="last_day_of_month(index_date)",
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.2,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    
    latest_rrt_date=patients.maximum_of("dialysis_date", "kidney_tx_date", "RRT_date"),

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
                Measure(
                    id=f"{test}_single_egfr_{pop}_rate",
                    numerator=test,
                    denominator=pop,
                    group_by=["single_egfr"],
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
                group_by=["ethnicity", "ckd_primis_stage"],
            ),
            Measure(
                id=f"ckd_primis_1_5_stage_{pop}_age_band_rate",
                numerator="ckd_primis_1_5",
                denominator=pop,
                group_by=["age_band", "ckd_primis_stage"],
            ),
            Measure(
                id=f"ckd_primis_1_5_stage_{pop}_sex_rate",
                numerator="ckd_primis_1_5",
                denominator=pop,
                group_by=["sex", "ckd_primis_stage"],
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
