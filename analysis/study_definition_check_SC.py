#code to check the secondary care codes, for one month only

from cohortextractor import StudyDefinition, patients
from variable_definitions.ukrr_variables import ukrr_variables
from codelists import *

demographics = ["age_band", "sex", "region", "imd", "ethnicity"]

def loop_over_proc_codes(code_list):

    def make_variable(code):
        #removing . from variable name
        code2=code.replace('.','')
        return {
            f"op_proc_{code2}": patients.outpatient_appointment_date(
                    returning="binary_flag",
                    with_these_procedures=codelist([code], system="opcs4"),
                    between=["index_date - 3 months", "index_date"],
                    return_expectations={
                        "incidence": 0.3,
                    },
                ),
            f"ip_proc_{code2}": patients.admitted_to_hospital(
                    returning="binary_flag",
                    find_last_match_in_period=True,
                    with_these_procedures=codelist([code], system="opcs4"),
                    between=["index_date - 3 months", "index_date"],
                    return_expectations={
                        "incidence": 0.3,
                    },
                ),
    #get critical care days (not using _proc_ in name as want to pick this up separately)
            f"ipp_cc_{code2}": patients.admitted_to_hospital(
                    returning="days_in_critical_care",
                    find_last_match_in_period=True,
                    with_these_procedures=codelist([code], system="opcs4"),
                    between=["index_date - 3 months", "index_date"],
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
 #           f"ipp_cc_flag_{code2}": [1 if v > 0 else 0 for v in f"ipp_cc_{code2}"]
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
                    between=["index_date - 3 months", "index_date"],
                    return_expectations={
                        "incidence": 0.3,
                    },
                ),
    #get critical care days (not using _diag_ in name as want to pick this up separately)
            f"ipd_cc_{code2}": patients.admitted_to_hospital(
                    returning="days_in_critical_care",
                    find_last_match_in_period=True,
                    with_these_diagnoses=codelist([code], system="icd10"),
                    between=["index_date - 3 months", "index_date"],
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
 #           f"ipd_cc_flag_{code2}": [1 if v > 0 else 0 for v in f"ipd_cc_{code2}"]
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

   
    ckd_code=patients.with_these_clinical_events(
        codelist=ckd_codelist,
        between=["index_date - 3 months", "index_date"],
        returning="code",
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"238318009": 0.5, "864311000000105": 0.5}},
        },
    ),

    ckd_primis_1_5_code=patients.with_these_clinical_events(
        codelist=primis_ckd_1_5_codelist,
        between=["index_date - 3 months", "index_date"],
        returning="code",
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"238318009": 0.5, "864311000000105": 0.5}},
        },
    ),

    # RRT
    RRT_code=patients.with_these_clinical_events(
        codelist=RRT_codelist,
        between=["index_date - 3 months", "index_date"],
        returning="code",
        return_expectations={
            "category": {"ratios": {"14S2.": 0.5, "7A600": 0.5}},
            "incidence": 0.2,
        },
    ),
    # dialysis
    dialysis_code=patients.with_these_clinical_events(
        codelist=dialysis_codelist,
        between=["index_date - 3 months", "index_date"],
        returning="code",
        return_expectations={
            "category": {"ratios": {"7A602": 0.5, "7A600": 0.5}},
            "incidence": 0.2,
        },
    ),
    # kidney_tx
    kidney_tx_code=patients.with_these_clinical_events(
        codelist=kidney_tx_codelist,
        between=["index_date - 3 months", "index_date"],
        returning="code",
        return_expectations={
            "category": {"ratios": {"14S2.": 0.5, "7B00.": 0.5}},
            "incidence": 0.2,
        },
    ),
  
   ### Secondary care codes ####
   #looking at whole codelist to check we aren't somehow picking up codes not on our list of individual codes because of prefix matching
    # outpatients
 
    op_RRT=patients.outpatient_appointment_date(
        returning="binary_flag",
        with_these_procedures=RRT_opcs4_codelist,
        between=["index_date - 3 months", "index_date"],
        return_expectations={
            "incidence": 0.3,
        },
    ),
  
    # inpatients
   
    ip_RRT_diagnosis=patients.admitted_to_hospital(
        returning="binary_flag",
        find_last_match_in_period=True,
        with_these_diagnoses=RRT_icd10_codelist,
        between=["index_date - 3 months", "index_date"],
        return_expectations={
            "incidence": 0.3,
        },
    ),
  
    ip_RRT_procedure=patients.admitted_to_hospital(
        returning="binary_flag",
        find_last_match_in_period=True,
        with_these_procedures=RRT_opcs4_codelist,
        between=["index_date - 3 months", "index_date"],
        return_expectations={
            "incidence": 0.3,
        },
    ),
  
  # creating variables from individual codes
    **loop_over_proc_codes(RRT_opcs4_codelist),
    **loop_over_diag_codes(RRT_icd10_codelist),

     **ukrr_variables
)

