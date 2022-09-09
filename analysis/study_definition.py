from cohortextractor import StudyDefinition, patients, Measure
from variable_definitions.demographic_variables import demographic_variables
from variable_definitions.test_variables import test_variables, path_tests
from variable_definitions.ckd_variables import ckd_variables
from variable_definitions.secondary_care_variables import secondary_care_variables
from variable_definitions.rrt_variables import rrt_variables
from variable_definitions.comorbidity_variables import comorbidity_variables
from scripts.variables import demographics


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
    **rrt_variables,
    **secondary_care_variables,
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
                Measure(
                    id=f"{test}_single_egfr_{pop}_ethnicity_rate",
                    numerator=test,
                    denominator=pop,
                    group_by=["single_egfr", "ethnicity"],
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

    measures.extend([m_rrt, m_dialysis, m_kidney_tx])

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
