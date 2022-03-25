from cohortextractor import StudyDefinition, patients, Measure

from codelists import *



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
    
    sex=patients.sex(
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"M": 0.49, "F": 0.5, "U": 0.01}},
        }
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
   
    # RRT 
    RRT=patients.with_these_clinical_events(
        codelist=RRT_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.2},
    ),

    RRT_count=patients.with_these_clinical_events(
        codelist=RRT_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="number_of_matches_in_period",
        return_expectations={
            "int": {"distribution": "poisson", "mean": 2},
            "incidence": 0.2,
        },
    ),

    RRT_code=patients.with_these_clinical_events(
        codelist=RRT_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={
            "category": {"ratios": {"14S2.": 0.5, "7A600": 0.5}},
            "incidence": 0.2,
        },
    ),

    # dialysis 
    dialysis=patients.with_these_clinical_events(
        codelist=dialysis_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.2},
    ),

    dialysis_count=patients.with_these_clinical_events(
        codelist=dialysis_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="number_of_matches_in_period",
        return_expectations={
            "int": {"distribution": "poisson", "mean": 2},
            "incidence": 0.2,
        },
    ),

    dialysis_code=patients.with_these_clinical_events(
        codelist=dialysis_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={
            "category": {"ratios": {"7A602": 0.5, "7A600": 0.5}},
            "incidence": 0.2,
        },
    ),
)


measures = []

for pop in ["population", "at_risk"]:
    measures.extend(
        [
            Measure(
                id=f"RRT_{pop}_rate",
                numerator="RRT",
                denominator=pop,
                group_by=["practice"],
            ),
            Measure(
                id=f"RRT_code_{pop}_rate",
                numerator="RRT",
                denominator=pop,
                group_by=["RRT_code"],
            ),
            Measure(
                id=f"dialysis_{pop}_rate",
                numerator="dialysis",
                denominator=pop,
                group_by=["practice"],
            ),
            Measure(
                id=f"dialysis_code_{pop}_rate",
                numerator="dialysis",
                denominator=pop,
                group_by=["dialysis_code"],
            ),
        ]
    )

   