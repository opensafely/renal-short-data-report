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
    
    ckd=patients.with_these_clinical_events(
        codelist=ckd_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={
            "incidence": 0.5,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),

    ckd_code=patients.with_these_clinical_events(
        codelist=ckd_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"238318009": 0.5, "864311000000105": 0.5}},
        },
    ),
    ckd_primis_1_5=patients.with_these_clinical_events(
        codelist=primis_ckd_1_5_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={
            "incidence": 0.5,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),

    ckd_primis_1_5_code=patients.with_these_clinical_events(
        codelist=primis_ckd_1_5_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"238318009": 0.5, "864311000000105": 0.5}},
        },
    ),

    ckd_primis_3_5=patients.with_these_clinical_events(
        codelist=primis_ckd_3_5_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={
            "incidence": 0.5,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),

    ckd_primis_3_5_code=patients.with_these_clinical_events(
        codelist=primis_ckd_3_5_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"238318009": 0.5, "864311000000105": 0.5}},
        },
    ),
    
    
)


measures = [
    Measure(
            id=f"ckd_rate",
            numerator="ckd",
            denominator="population",
            group_by=["practice"]
            ),
    Measure(
            id=f"ckd_primis_3_5_rate",
            numerator="ckd_primis_3_5",
            denominator="population",
            group_by=["practice"]
            ),
    Measure(
            id=f"ckd_primis_1_5_rate",
            numerator="ckd_primis_1_5",
            denominator="population",
            group_by=["practice"]
            ),
]



for d in demographics:
    m_ckd = Measure(
            id=f"ckd_rate",
            numerator="ckd",
            denominator="population",
            group_by=[d]
            )
    m_ckd_1_5 = Measure(
            id=f"ckd_primis_3_5_rate",
            numerator="ckd_primis_3_5",
            denominator="population",
            group_by=[d]
            )
    m_ckd_3_5 = Measure(
            id=f"ckd_primis_1_5_rate",
            numerator="ckd_primis_1_5",
            denominator="population",
            group_by=[d]
            )
    measures.extend([m_ckd, m_ckd_1_5, m_ckd_3_5])
