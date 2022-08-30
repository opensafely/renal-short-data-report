#Creates variables for all the variables available in the UKRR data, selecting only the available data for each cohort
from cohortextractor import patients

from codelists import *

ukrr_variables = dict(
    # Prevalent cohorts
    #2019
    ukrr_2019 = patients.with_record_in_ukrr(
        from_dataset="2019_prevalence",
        returning="binary_flag",
        return_expectations={
            "incidence": 0.25
        },
    ),
    ukrr_2019_mod = patients.with_record_in_ukrr(
        from_dataset="2019_prevalence",
        returning="treatment_modality_prevalence",
        return_expectations={
                "category": {"ratios": {"ICHD": 0.5, "Tx": 0.5}},
                "incidence": 0.25,
            },
    ),
    ukrr_2019_centre = patients.with_record_in_ukrr(
        from_dataset="2019_prevalence",
        returning="renal_centre",
        return_expectations={
                "category": {"ratios": {"RRK02": 0.5, "RDEE1": 0.5}},
                "incidence": 0.25,
            },
    ),
    ukrr_2019_startmod = patients.with_record_in_ukrr(
    from_dataset="2019_prevalence",
    returning="treatment_modality_start",
    return_expectations={
            "category": {"ratios": {"ICHD": 0.5, "Tx": 0.5}},
            "incidence": 0.25,
        },
    ),
    ukrr_2019_startdate = patients.with_record_in_ukrr(
        from_dataset="2019_prevalence",
        returning="rrt_start_date",
        date_format="YYYY-MM-DD",
        return_expectations={
                "date": {"earliest": "1970-01-01", "latest": "2019-12-31"},
            },
    ),
    #2020
    ukrr_2020 = patients.with_record_in_ukrr(
        from_dataset="2020_prevalence",
        returning="binary_flag",
        return_expectations={
            "incidence": 0.25
        },
    ),
    ukrr_2020_mod = patients.with_record_in_ukrr(
        from_dataset="2020_prevalence",
        returning="treatment_modality_prevalence",
        return_expectations={
                "category": {"ratios": {"ICHD": 0.5, "Tx": 0.5}},
                "incidence": 0.25,
            },
    ),
    ukrr_2020_centre = patients.with_record_in_ukrr(
        from_dataset="2020_prevalence",
        returning="renal_centre",
        return_expectations={
                "category": {"ratios": {"RRK02": 0.5, "RDEE1": 0.5}},
                "incidence": 0.25,
            },
    ),
    ukrr_2020_startmod = patients.with_record_in_ukrr(
    from_dataset="2020_prevalence",
    returning="treatment_modality_start",
    return_expectations={
            "category": {"ratios": {"ICHD": 0.5, "Tx": 0.5}},
            "incidence": 0.25,
        },
    ),
    ukrr_2020_startdate = patients.with_record_in_ukrr(
        from_dataset="2020_prevalence",
        returning="rrt_start_date",
        date_format="YYYY-MM-DD",
        return_expectations={
                "date": {"earliest": "1970-01-01", "latest": "2020-12-31"},
            },
    ),
    #2021
    ukrr_2021 = patients.with_record_in_ukrr(
        from_dataset="2021_prevalence",
        returning="binary_flag",
        return_expectations={
            "incidence": 0.25
        },
    ),
    ukrr_2021_mod = patients.with_record_in_ukrr(
        from_dataset="2021_prevalence",
        returning="treatment_modality_prevalence",
        return_expectations={
                "category": {"ratios": {"ICHD": 0.5, "Tx": 0.5}},
                "incidence": 0.25,
            },
    ),
    ukrr_2021_centre = patients.with_record_in_ukrr(
        from_dataset="2021_prevalence",
        returning="renal_centre",
        return_expectations={
                "category": {"ratios": {"RRK02": 0.5, "RDEE1": 0.5}},
                "incidence": 0.25,
            },
    ),
    ukrr_2021_startmod = patients.with_record_in_ukrr(
    from_dataset="2021_prevalence",
    returning="treatment_modality_start",
    return_expectations={
            "category": {"ratios": {"ICHD": 0.5, "Tx": 0.5}},
            "incidence": 0.25,
        },
    ),
    ukrr_2021_startdate = patients.with_record_in_ukrr(
        from_dataset="2021_prevalence",
        returning="rrt_start_date",
        date_format="YYYY-MM-DD",
        return_expectations={
                "date": {"earliest": "1970-01-01", "latest": "2021-12-31"},
            },
    ),
    #2020 CKD
    #2020
    ukrr_ckd2020 = patients.with_record_in_ukrr(
        from_dataset="2020_ckd",
        returning="binary_flag",
        return_expectations={
            "incidence": 0.35
        },
    ),
    ukrr_ckd2020_creat = patients.with_record_in_ukrr(
        from_dataset="2020_ckd",
        returning="latest_creatinine",
            return_expectations={
                "int": {"distribution": "normal", "mean": 45, "stddev": 20},
                "incidence": 0.35,
            },
    ),
    ukrr_ckd2020_egfr = patients.with_record_in_ukrr(
        from_dataset="2020_ckd",
        returning="latest_egfr",
            return_expectations={
                "float": {"distribution": "normal", "mean": 20, "stddev": 10},
                "incidence": 0.2,
            },
    ),
    ukrr_ckd2020_centre = patients.with_record_in_ukrr(
        from_dataset="2020_ckd",
        returning="renal_centre",
        return_expectations={
                "category": {"ratios": {"RRK02": 0.5, "RDEE1": 0.5}},
                "incidence": 0.35,
            },
    ),
    #Incident cohort
    #2020
    ukrr_inc2020 = patients.with_record_in_ukrr(
        from_dataset="2020_incidence",
        returning="binary_flag",
        return_expectations={
            "incidence": 0.25
        },
    ),
    ukrr_inc2020_mod = patients.with_record_in_ukrr(
        from_dataset="2020_incidence",
        returning="treatment_modality_start",
        return_expectations={
                "category": {"ratios": {"ICHD": 0.5, "Tx": 0.5}},
                "incidence": 0.25,
            },
    ),
    ukrr_inc2020_centre = patients.with_record_in_ukrr(
        from_dataset="2020_incidence",
        returning="renal_centre",
        return_expectations={
                "category": {"ratios": {"RRK02": 0.5, "RDEE1": 0.5}},
                "incidence": 0.25,
            },
    ),
    ukrr_inc2020_date = patients.with_record_in_ukrr(
        from_dataset="2020_incidence",
        returning="rrt_start_date",
        date_format="YYYY-MM-DD",
        return_expectations={
                "date": {"earliest": "2020-01-01", "latest": "2020-12-31"},
            },
    ),
)