# Import functions from the cohort extractor package
from cohortextractor import (
    StudyDefinition, 
    patients, 
    codelist, 
    codelist_from_csv,  
    filter_codes_by_category,
    combine_codelists,
    Measure
)

# Import all relevant code lists using codelists.py 

from codelists import *
from demographic_variables import demographic_variables

# Specify study definition


study = StudyDefinition(
    # define default dummy data behaviour
    default_expectations={
        "date": {"earliest": "2019-01-01", "latest": "today"},  
        "rate": "uniform",
        "incidence": 0.5,
    },

    # define study index date
    index_date="2019-01-01"
    ,
    #define study population

    population=patients.satisfying(
        """
        registered AND
        (sex = "M" OR sex = "F") AND
        (age >= 18 AND age <= 120)
        """,
        registered=patients.registered_as_of("index_date")
    ),

    #population=patients.registered_as_of("index_date")
   # ,
       
#Clinical variables

    eGFR_test=patients.with_these_clinical_events(
        codelist=eGFR_tests_codes,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.2}
    ),

    eGFR_values=patients.with_these_clinical_events(
        codelist=eGFR_values_codes,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.2}
    ),
    
#    eGFR_values=patients.with_these_clinical_events(    
#        codelist=eGFR_values_codes,
#        between=["index_date", "last_day_of_month(index_date)"],
#        returning="numeric_value",
#        find_last_match_in_period=True
#        return_expectations={
#            "float" : {"distribution": "normal", "mean": 70, "stddev": 30},
#            "incidence" : 0.2
#            }
#    ),

  **demographic_variables
    
)
# Define measures by region, practice, sex, age ethnicity. 


measures = [
    Measure(
        id="eGFR_test_region",
        numerator="eGFR_test",
        denominator="population",
        group_by=["region"],
        small_number_suppression=False
    ),

    Measure(
        id="eGFR_test_practice",
        numerator="eGFR_test",
        denominator="population",
        group_by=["practice"],
        small_number_suppression=False
    ),

    Measure(
        id="eGFR_test_sex",
        numerator="eGFR_values",
        denominator="population",
        group_by=["sex"],
        small_number_suppression=False
    ),

    Measure(
        id="eGFR_test_ethnicity",
        numerator="eGFR_values",
        denominator="population",
        group_by=["ethnicity"],
        small_number_suppression=False
    ),

    Measure(
        id="eGFR_values_rate_sex",
        numerator="eGFR_values",
        denominator="population",
        group_by=["sex"],
        small_number_suppression=False
    ),

    Measure(
        id="eGFR_values_rate_ethnicity",
        numerator="eGFR_values",
        denominator="population",
        group_by=["ethnicity"],
        small_number_suppression=False
    ),

        Measure(
        id="eGFR_values_region",
        numerator="eGFR_values",
        denominator="population",
        group_by=["region"],
        small_number_suppression=False
    ),

    Measure(
        id="eGFR_values_practice",
        numerator="eGFR_values",
        denominator="population",
        group_by=["practice"],
        small_number_suppression=False
    ),

    Measure(
        id="eGFR_values_sex",
        numerator="eGFR_values",
        denominator="population",
        group_by=["sex"],
        small_number_suppression=False
    ),

    Measure(
        id="eGFR_values_ethnicity",
        numerator="eGFR_values",
        denominator="population",
        group_by=["ethnicity"],
        small_number_suppression=False
    ),
]
