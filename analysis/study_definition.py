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
    diabetes=patients.satisfying(
        """
        (
            diabetes_any_primis AND
            (NOT diabetes_resolved)
        ) 
    
        OR

        (
            diabetes_any_primis AND
            diabetes_resolved AND
            (diabetes_resolved_date < diabetes_any_date) OR (diabetes_resolved_date < diabetes_primis_date)
        )

        """,
        diabetes_any=patients.with_these_clinical_events(
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
        diabetes_any_primis=patients.satisfying(
            """
            diabetes_any OR diabetes_primis
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

    at_risk=patients.satisfying(
        """
        diabetes
        OR
        hypertension
        """
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
        codelist=creatinine_clearance_codelist,
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
        codelist=eGFR_codelist,
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
    ),

   ckd=patients.with_these_clinical_events(
        codelist=ckd_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.5,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),

    ckd_code=patients.with_these_clinical_events(
        codelist=ckd_codelist,
        on_or_before="index_date",
        returning="code",
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"238318009": 0.5, "864311000000105": 0.5}},
        },
    ),
    ckd_primis_1_5=patients.with_these_clinical_events(
        codelist=primis_ckd_1_5_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.5,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),

    ckd_primis_1_5_code=patients.with_these_clinical_events(
        codelist=primis_ckd_1_5_codelist,
        on_or_before="index_date",
        returning="code",
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"238318009": 0.5, "864311000000105": 0.5}},
        },
    ),

    ckd_primis_3_5=patients.with_these_clinical_events(
        codelist=primis_ckd_3_5_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.2,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),

    ckd_primis_3_5_code=patients.with_these_clinical_events(
        codelist=primis_ckd_3_5_codelist,
        on_or_before="index_date",
        returning="code",
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"238318009": 0.5, "864311000000105": 0.5}},
        },
    ),

 # RRT 
    RRT=patients.with_these_clinical_events(
        codelist=RRT_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.2,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),

    RRT_code=patients.with_these_clinical_events(
        codelist=RRT_codelist,
        on_or_before="index_date",
        returning="code",
        return_expectations={
            "category": {"ratios": {"14S2.": 0.5, "7A600": 0.5}},
            "incidence": 0.2,
        },
    ),

    # dialysis 
    #defaults to the lastest match
    dialysis=patients.with_these_clinical_events(
        codelist=dialysis_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.2,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),

    dialysis_code=patients.with_these_clinical_events(
        codelist=dialysis_codelist,
        on_or_before="index_date",
        returning="code",
        return_expectations={
            "category": {"ratios": {"7A602": 0.5, "7A600": 0.5}},
            "incidence": 0.2,
        },
    ),




    # kidney_tx 
    #defaults to the lastest match
    kidney_tx=patients.with_these_clinical_events(
        codelist=kidney_tx_codelist,
        on_or_before="index_date",
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        include_date_of_match=True,
        return_expectations={
            "incidence": 0.2,
            "date": {"earliest": "1900-01-01", "latest": "today"},
        },
    ),

    kidney_tx_code=patients.with_these_clinical_events(
        codelist=kidney_tx_codelist,
        on_or_before="index_date",
        returning="code",
        return_expectations={
            "category": {"ratios": {"14S2.": 0.5, "7B00.": 0.5}},
            "incidence": 0.2,
        },
    ),

    latest_renal_date=patients.maximum_of(
    "dialysis_date", "kidney_tx_date", "RRT_date",
    "ckd_date", "ckd_primis_1_5_date","ckd_primis_3_5_date"
    ),

    #Picking most recent status
    #patients are assigned to the first condition they satisfy, so define RRT modalities first
    latest_renal_status = patients.categorised_as(
        {
            "None"      : """
                        (NOT dialysis) 
                        AND (NOT kidney_tx) 
                        AND (NOT RRT)
                        AND (NOT ckd_primis_3_5)
                        AND (NOT ckd_primis_1_5)
                        AND (NOT ckd)
                        """,
            "Dialysis"  : """
                        dialysis_date=latest_renal_date 
                        AND
                        kidney_tx_date!=latest_renal_date
                        """,
            "Transplant" : """
                        kidney_tx_date=latest_renal_date
                        AND
                        dialysis_date!=latest_renal_date 
                        """,
            "RRT_unknown"  : """
                        dialysis_date=latest_renal_date 
                        OR
                        kidney_tx_date=latest_renal_date
                        OR
                        RRT_date=latest_renal_date
                        """,
            "CKD3_5"    : """
                        ckd_primis_3_5_date=latest_renal_date
                        """,
            "CKD_unknown" : """
                        ckd_primis_1_5_date=latest_renal_date
                        OR
                        ckd_date=latest_renal_date
                        """,
            "Uncategorised" : "DEFAULT"
        },
        return_expectations={
                "rate": "universal",
                "category": {
                    "ratios": {
                        "None": 0.4,
                        "Dialysis": 0.1,
                        "Transplant": 0.1,
                        "RRT_unknown": 0.1,
                        "CKD3_5": 0.1,
                        "CKD_unknown": 0.1,
                        "Uncategorised": 0.1,
                    }
                },
            },
        ),
 
   

)

measures = []

for pop in ["population", "at_risk", "diabetes", "hypertension"]:
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
         Measure(
            id=f"ckd_{pop}_rate",
            numerator="ckd",
            denominator=pop,
            group_by=["practice"]
            ),
    Measure(
            id=f"ckd_primis_3_5_{pop}_rate",
            numerator="ckd_primis_3_5",
            denominator=pop,
            group_by=["practice"]
            ),
    Measure(
            id=f"ckd_primis_1_5_{pop}_rate",
            numerator="ckd_primis_1_5",
            denominator=pop,
            group_by=["practice"]
            ),
    Measure(
            id=f"RRT_{pop}_rate",
            numerator="RRT",
            denominator=pop,
            group_by=["practice"]
            ),
    Measure(
            id=f"dialysis_{pop}_rate",
            numerator="dialysis",
            denominator=pop,
            group_by=["practice"]
            ),
    Measure(
            id=f"kidney_tx_{pop}_rate",
            numerator="kidney_tx",
            denominator=pop,
            group_by=["practice"]
            ),
    Measure(
            id=f"renal_status_{pop}_rate",
            numerator="population",
            denominator=pop,
            group_by=["latest_renal_status"]
            ),
    Measure(
        id=f"ckd_{pop}_rate",
        numerator="ckd",
        denominator="population",
        group_by=["practice"]
    ),
    Measure(
        id=f"ckd_primis_3_5_{pop}_rate",
        numerator="ckd_primis_3_5",
        denominator="population",
        group_by=["practice"]
    ),
    Measure(
        id=f"ckd_primis_1_5_{pop}_rate",
        numerator="ckd_primis_1_5",
        denominator="population",
        group_by=["practice"]
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

        m_rrt = Measure(
            id=f"RRT_{d}_{pop}_rate", numerator="RRT", denominator=pop, group_by=[d]
        )

        m_dialysis = Measure(
            id=f"dialysis_{d}_{pop}_rate", numerator="dialysis", denominator=pop, group_by=[d]
        )

        m_kidney_tx = Measure(
            id=f"kidney_tx_{d}_{pop}_rate", numerator="kidney_tx", denominator=pop, group_by=[d]
        )

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

        measures.extend([m_crcl, m_cr, m_egfr, m_rrt, m_dialysis, m_ckd, m_ckd_1_5, m_ckd_3_5, m_kidney_tx])
