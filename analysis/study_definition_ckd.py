from cohortextractor import StudyDefinition, patients, Measure

from codelists import *

def generate_expectations_codes(codelist, incidence=0.5):
    expectations = {str(x): (1-incidence) / len(codelist) for x in codelist}
    expectations[None] = incidence
    return expectations

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
    ),
    ckd_primis=patients.with_these_clinical_events(
        codelist=primis_ckd_stage,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={
            "incidence": 0.5,
        },  
    ),
    ckd_primis_stage=patients.with_these_clinical_events(
        codelist=primis_ckd_stage,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="category",
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "1": 0.2,
                    "2": 0.2,
                    "3": 0.2,
                    "4": 0.2,
                    "5": 0.2,
                }
            },
        },
    ),
)

measures = [
    Measure(
        id="incident_ckd_primis_stage_rate",
        numerator="ckd_primis",
        denominator="population",
        group_by=["ckd_primis_stage"],
    ),
]

