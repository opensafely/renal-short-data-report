from cohortextractor import StudyDefinition, patients, Measure
from variable_definitions.demographic_variables import demographic_variables
from variable_definitions.test_variables import test_variables, path_tests
from variable_definitions.ckd_variables import ckd_variables
from variable_definitions.secondary_care_variables import secondary_care_variables
from variable_definitions.rrt_variables import rrt_variables
from variable_definitions.comorbidity_variables import comorbidity_variables
from variable_definitions.ukrr_variables import ukrr_variables
from variable_definitions.incident_variables import incident_variables
from scripts.variables import demographics
from codelists import *

+def loop_over_proc_codes(code_list):

    def make_variable(code):
        #removing . from variable name
        code2=code.replace('.','')
        return {
            f"op_proc_{code2}": patients.outpatient_appointment_date(
                    returning="binary_flag",
                    with_these_procedures=codelist([code], system="opcs4"),
                    between=["latest_rrt_date_secondary","latest_rrt_date_secondary"],  #to only pick up codes on the date of interest
                    return_expectations={
                        "incidence": 0.3,
                    },
                ),
            f"ip_proc_{code2}": patients.admitted_to_hospital(
                    returning="binary_flag",
                    date_format="YYYY-MM-DD",
                    find_last_match_in_period=True,
                    with_these_procedures=codelist([code], system="opcs4"),
                    between=["latest_rrt_date_secondary","latest_rrt_date_secondary"],
                    return_expectations={
                        "incidence": 0.3,
                    },
                ),
    #get critical care days (not using _proc_ in name as want to pick this up separately)
            f"ipp_cc_{code2}": patients.admitted_to_hospital(
                    returning="days_in_critical_care",
                    find_last_match_in_period=True,
                    with_these_procedures=codelist([code], system="opcs4"),
                    between=["latest_rrt_date_secondary","latest_rrt_date_secondary"],
                    return_expectations={
                        "category": {
                            "ratios": {
                                "0": 0.6,
                                "1": 0.1,
                                "2": 0.2,
                                "3": 0.1,
                                }
                            },
                        "incidence": 0.1,
                        },
                ),
        }

    variables = {}
    for code in code_list:
        variables.update(make_variable(code))
    return variables

def loop_over_diag_codes(code_list):

    def make_variable(code):
        #removing . from variable name
        code2=code.replace('.','')
        return {
            f"ip_diag_{code2}": patients.admitted_to_hospital(
                    returning="binary_flag",
                    find_last_match_in_period=True,
                    with_these_diagnoses=codelist([code], system="icd10"),
                    between=["latest_rrt_date_secondary","latest_rrt_date_secondary"],
                    return_expectations={
                        "incidence": 0.3,
                    },
                ),
    #get critical care days (not using _diag_ in name as want to pick this up separately)
            f"ipd_cc_{code2}": patients.admitted_to_hospital(
                    returning="days_in_critical_care",
                    find_last_match_in_period=True,
                    with_these_diagnoses=codelist([code], system="icd10"),
                    between=["latest_rrt_date_secondary","latest_rrt_date_secondary"],
                    return_expectations={
                        "category": {
                            "ratios": {
                                "0": 0.6,
                                "1": 0.1,
                                "2": 0.2,
                                "3": 0.1,
                                }
                            },
                        "incidence": 0.1,
                        },
                ),
        }

    variables = {}
    for code in code_list:
        variables.update(make_variable(code))
    return variables


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
    **test_variables,
    **ckd_variables,
    **rrt_variables,
    **secondary_care_variables,
    **ukrr_variables,
    **incident_variables,

     # creating variables from individual codes
    **loop_over_proc_codes(RRT_opcs4_codelist),
    **loop_over_diag_codes(RRT_icd10_codelist),
)


