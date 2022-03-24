from cohortextractor import StudyDefinition, patients, Measure

from codelists import *

demographics = ["age_band", "sex", "region", "imd", "ethnicity"]

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
            "1": """index_of_multiple_deprivation >=1 AND index_of_multiple_deprivation < 32844*1/5""",
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
    at_risk=patients.satisfying(
        """
        (
            diabetes_any AND
            (NOT diabetes_resolved)
        ) 
    
        OR

        (
            diabetes_any AND
            diabetes_resolved AND
            (diabetes_resolved_date < diabetes_date) OR (diabetes_resolved_date < diabetes_primis_date)
        )

        OR

        (hypertension)
        """,
        diabetes=patients.with_these_clinical_events(
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
        diabetes_any=patients.satisfying(
            """
            diabetes OR diabetes_primis
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
        hypertension=patients.with_these_clinical_events(
            codelist=hypertension_codelist,
            on_or_before="index_date",
            returning="binary_flag",
            return_expectations={
                "incidence": 0.5,
                "date": {"earliest": "1900-01-01", "latest": "today"},
            },
        ),
    ),
    creatinine=patients.with_these_clinical_events(
        codelist=creatinine_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.5,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),
    creatinine_code=patients.with_these_clinical_events(
        codelist=creatinine_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"1000731000000107": 0.5, "1000981000000109": 0.5}},
        },
    ),
    creatinine_count=patients.with_these_clinical_events(
        codelist=creatinine_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="number_of_matches_in_period",
        return_expectations={
            "int": {"distribution": "poisson", "mean": 2},
            "incidence": 0.2,
        },
    ),
    creatinine_numeric_value=patients.with_these_clinical_events(
        codelist=creatinine_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="numeric_value",
        return_expectations={
            "float": {"distribution": "normal", "mean": 45.0, "stddev": 20},
            "incidence": 0.5,
        },
    ),
    creatinine_operator=patients.comparator_from(
        "creatinine_numeric_value",
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
    cr_cl=patients.with_these_clinical_events(
        codelist=creatinine_clearance_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.5},
    ),
    cr_cl_code=patients.with_these_clinical_events(
        codelist=creatinine_clearance_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"1015981000000103": 0.5, "102811001": 0.5}},
        },
    ),
    cr_cl_count=patients.with_these_clinical_events(
        codelist=creatinine_clearance_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="number_of_matches_in_period",
        return_expectations={
            "int": {"distribution": "poisson", "mean": 2},
            "incidence": 0.2,
        },
    ),
    cr_cl_numeric_value=patients.with_these_clinical_events(
        codelist=creatinine_clearance_level_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="numeric_value",
        return_expectations={
            "float": {"distribution": "normal", "mean": 45.0, "stddev": 20},
            "incidence": 0.5,
        },
    ),
    cr_cl_operator=patients.comparator_from(
        "cr_cl_numeric_value",
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
    # eGFR values
    eGFR=patients.with_these_clinical_events(
        codelist=eGFR_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.2},
    ),
    eGFR_count=patients.with_these_clinical_events(
        codelist=eGFR_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="number_of_matches_in_period",
        return_expectations={
            "int": {"distribution": "poisson", "mean": 2},
            "incidence": 0.2,
        },
    ),
    eGFR_numeric_value=patients.with_these_clinical_events(
        codelist=eGFR_level_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="numeric_value",
        return_expectations={
            "float": {"distribution": "normal", "mean": 70, "stddev": 30},
            "incidence": 0.2,
        },
    ),
    eGFR_code=patients.with_these_clinical_events(
        codelist=eGFR_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={
            "category": {"ratios": {"1011481000000105": 0.5, "1011491000000107": 0.5}},
            "incidence": 0.2,
        },
    ),
    eGFR_comparator=patients.comparator_from(
        "eGFR_numeric_value",
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
    )
)


measures = []

for pop in ["population", "at_risk"]:
    measures.extend(
        [
            Measure(
                id=f"cr_cl_{pop}_rate",
                numerator="cr_cl",
                denominator=pop,
                group_by=["practice"],
            ),
            Measure(
                id=f"cr_cl_code_{pop}_rate",
                numerator="cr_cl",
                denominator=pop,
                group_by=["cr_cl_code"],
            ),
            Measure(
                id=f"creatinine_{pop}_rate",
                numerator="creatinine",
                denominator=pop,
                group_by=["practice"],
            ),
            Measure(
                id=f"creatinine_code_{pop}_rate",
                numerator="creatinine",
                denominator=pop,
                group_by=["creatinine_code"],
            ),
            Measure(
                id=f"eGFR_{pop}_rate",
                numerator="eGFR",
                denominator=pop,
                group_by=["practice"],
            ),
            Measure(
                id=f"eGFR_code_{pop}_rate",
                numerator="eGFR",
                denominator=pop,
                group_by=["eGFR_code"],
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

    for d in demographics:
        m_crcl = Measure(
            id=f"cr_cl_{d}_{pop}_rate", numerator="cr_cl", denominator=pop, group_by=[d]
        )
        m_cr = Measure(
            id=f"creatinine_{d}_{pop}_rate",
            numerator="creatinine",
            denominator=pop,
            group_by=[d],
        )

        m_egfr = Measure(
            id=f"eGFR_{d}_{pop}_rate", numerator="eGFR", denominator=pop, group_by=[d]
        )

        measures.extend([m_crcl, m_cr, m_egfr])
