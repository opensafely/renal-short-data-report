import pandas as pd

from pandas._testing import assert_frame_equal
from analysis.scripts.combine_operators import (

    convert_values,
)
    
def test_map_numeric_values():
    mapping = {
        "albumin": {
            (16, 20): 20,
            (21, 31): 30,
            (31, float("inf")): 31,
        }
    }

    test_data = pd.DataFrame(
        {
            "albumin_numeric_value": pd.Series([-5, 0, 0.1, 16, 20, 21, 31, 40]),
        }
    )

    expected = pd.DataFrame(
        {
            "albumin_numeric_value": pd.Series([-1, 0, 1, 20, 20, 30, 31, 31]),
        }
    )

    result = convert_values(test_data, "albumin", mapping)

    assert_frame_equal(result, expected)