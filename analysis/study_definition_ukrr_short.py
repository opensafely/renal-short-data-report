from cohortextractor import StudyDefinition, patients, Measure
from variable_definitions.demographic_variables import demographic_variables
#from variable_definitions.test_variables import test_variables, path_tests
#from variable_definitions.ckd_variables import ckd_variables
from variable_definitions.secondary_care_variables import secondary_care_variables
from variable_definitions.rrt_variables import rrt_variables_no_renal
from variable_definitions.comorbidity_variables import comorbidity_variables
from variable_definitions.ukrr_variables import ukrr_variables
from variable_definitions.incident_variables import incident_variables
from scripts.variables import demographics
from codelists import *



study = StudyDefinition(
    default_expectations={
        "date": {"earliest": "2019-01-01", "latest": "today"},
        "rate": "uniform",
        "incidence": 0.5,
    },
    # define study index date
    index_date="2020-01-01",
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

    # Ethnicity
    ethnicity=patients.categorised_as(
        {
            "Missing": "DEFAULT",
            "White": "eth='1' OR (NOT eth AND ethnicity_sus='1')",
            "Mixed": "eth='2' OR (NOT eth AND ethnicity_sus='2')",
            "South Asian": "eth='3' OR (NOT eth AND ethnicity_sus='3')",
            "Black": "eth='4' OR (NOT eth AND ethnicity_sus='4')",
            "Other": "eth='5' OR (NOT eth AND ethnicity_sus='5')",
        },
        return_expectations={
            "category": {
                "ratios": {
                    "White": 0.2,
                    "Mixed": 0.2,
                    "South Asian": 0.2,
                    "Black": 0.2,
                    "Other": 0.2,
                }
            },
            "incidence": 0.4,
        },
        ethnicity_sus=patients.with_ethnicity_from_sus(
            returning="group_6",
            use_most_frequent_code=True,
            return_expectations={
                "category": {
                    "ratios": {"1": 0.2, "2": 0.2, "3": 0.2, "4": 0.2, "5": 0.2}
                },
                "incidence": 0.4,
            },
        ),
        eth=patients.with_these_clinical_events(
            ethnicity_codelist,
            returning="category",
            find_last_match_in_period=True,
            on_or_before="2022-07-31",
            return_expectations={
                "category": {
                    "ratios": {"1": 0.4, "2": 0.4, "3": 0.2, "4": 0.2, "5": 0.2}
                },
                "incidence": 0.75,
            },
        ),
    ),

    **demographic_variables,
    **comorbidity_variables,
    #**test_variables,
    #**ckd_variables,
    **rrt_variables_no_renal,
    **secondary_care_variables,
    **ukrr_variables,
    **incident_variables,

   
)


