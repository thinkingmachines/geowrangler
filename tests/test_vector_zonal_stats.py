import warnings

warnings.filterwarnings(action="ignore", category=UserWarning, module="geopandas")

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Polygon

from geowrangler.vector_zonal_stats import _fix_agg, _prep_aoi


@pytest.fixture()
def simple_aoi():
    df = pd.DataFrame(
        data={
            "col1": [1, 2, 3],
            "lat0": [0.0, 1.0, 2.0],
            "lon0": [0.0, 0.0, 0.0],
            "lat1": [0.0, 1.0, 2.0],
            "lon1": [1.0, 1.0, 1.0],
            "lat2": [1.0, 2.0, 3.0],
            "lon2": [1.0, 1.0, 1.0],
            "lat3": [1.0, 2.0, 3.0],
            "lon3": [0.0, 0.0, 0.0],
        }
    )

    def square(row):
        return Polygon(
            (
                [
                    (row.lat0, row.lon0),
                    (row.lat1, row.lon1),
                    (row.lat2, row.lon2),
                    (row.lat3, row.lon3),
                ]
            )
        )

    return gpd.GeoDataFrame(df, geometry=df.apply(square, axis=1), crs="EPSG:4326")


def test_fix_agg():
    assert _fix_agg(
        {"func": ["sum", "max", "min", "mean"], "column": "population"}
    ) == {
        "func": ["sum", "max", "min", "mean"],
        "column": "population",
        "output": [
            "population_sum",
            "population_max",
            "population_min",
            "population_mean",
        ],
        "fillna": [True, True, True, True],
    }

    assert _fix_agg({"func": "count"}) == {
        "func": ["count"],
        "column": "aoi_index",
        "output": ["aoi_index_count"],
        "fillna": [True],
    }

    assert _fix_agg({"func": "count", "output": "pois_count"}) == {
        "func": ["count"],
        "column": "aoi_index",
        "output": ["pois_count"],
        "fillna": [True],
    }

    assert _fix_agg(
        {
            "func": ["sum", "max", "min", "mean", "std"],
            "column": "population",
            "output": ["pop_sum", "pop_max", "pop_min", "avg_pop", "pop_std_dev"],
            "fillna": [True, True, True, True, False],
        }
    ) == {
        "func": ["sum", "max", "min", "mean", "std"],
        "column": "population",
        "output": ["pop_sum", "pop_max", "pop_min", "avg_pop", "pop_std_dev"],
        "fillna": [True, True, True, True, False],
    }

    assert _fix_agg({"func": "count"}) == {
        "func": ["count"],
        "column": "aoi_index",
        "output": ["aoi_index_count"],
        "fillna": [True],
    }


def test_fix_agg_exception():
    try:
        _fix_agg({})
        threw_exception = False
    except ValueError as e:
        threw_exception = True
        assert e.args[0] == "Missing key 'func' for agg {}"
    assert threw_exception

    try:
        _fix_agg(
            {"func": ["mean", "sum"], "column": "population", "output": ["pop_mean"]}
        )
        threw_exception = False
    except ValueError as e:
        threw_exception = True
        assert (
            e.args[0]
            == "output list ['pop_mean'] doesn't match func list ['mean', 'sum']"
        )
    assert threw_exception

    try:
        _fix_agg({"func": ["mean", "sum"], "column": "population", "fillna": [True]})
        threw_exception = False
    except ValueError as e:
        threw_exception = True
        assert e.args[0] == "fillna list [True] doesn't match func list ['mean', 'sum']"
    assert threw_exception


def test_prep_aoi(simple_aoi):
    new_aoi, aoi_index_data, aoi_col_data = _prep_aoi(simple_aoi)
    assert "aoi_index" in list(new_aoi.columns.values)
    assert len(new_aoi) == len(simple_aoi)
    assert new_aoi.drop("aoi_index", axis=1).equals(simple_aoi)
    assert new_aoi["aoi_index"].equals(simple_aoi.reset_index(level=0)["index"])

    assert aoi_index_data is None
    assert aoi_col_data is None


def test_prep_aoi_with_existing_index_cols(simple_aoi):
    simple_aoi["index"] = simple_aoi[["col1"]]
    new_aoi, aoi_index_data, aoi_col_data = _prep_aoi(simple_aoi)
    assert "aoi_index" in list(new_aoi.columns.values)
    assert len(new_aoi) == len(simple_aoi)
    assert new_aoi.drop("aoi_index", axis=1).equals(simple_aoi.drop("index", axis=1))

    assert aoi_index_data.equals(simple_aoi.col1)
    assert aoi_col_data is None


def test_prep_aoi_with_existing_aoi_index_cols(simple_aoi):
    simple_aoi["aoi_index"] = simple_aoi[["col1"]]
    new_aoi, aoi_index_data, aoi_col_data = _prep_aoi(simple_aoi)
    assert "aoi_index" in list(new_aoi.columns.values)
    assert len(new_aoi) == len(simple_aoi)
    assert new_aoi.drop("aoi_index", axis=1).equals(
        simple_aoi.drop("aoi_index", axis=1)
    )

    assert aoi_index_data is None
    assert aoi_col_data.equals(simple_aoi.col1)


def test_prep_aoi_with_existing_index_and_aoi_index_cols(simple_aoi):
    simple_aoi["index"] = simple_aoi[["col1"]]
    simple_aoi["aoi_index"] = simple_aoi[["col1"]]
    new_aoi, aoi_index_data, aoi_col_data = _prep_aoi(simple_aoi)
    assert "aoi_index" in list(new_aoi.columns.values)
    assert len(new_aoi) == len(simple_aoi)
    assert new_aoi.drop("aoi_index", axis=1).equals(
        simple_aoi.drop(labels=["index", "aoi_index"], axis=1)
    )
    assert aoi_index_data.equals(simple_aoi.col1)
    assert aoi_col_data.equals(simple_aoi.col1)
