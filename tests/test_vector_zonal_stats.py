import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Point, Polygon

from geowrangler.vector_zonal_stats import (
    GEO_INDEX_NAME,
    _aggregate_stats,
    _build_agg_args,
    _check_agg,
    _expand_aggs,
    _fix_agg,
    _prep_aoi,
    _validate_aggs,
    _validate_aoi,
    create_zonal_stats,
)


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


@pytest.fixture()
def simple_data():
    df = pd.DataFrame(
        data={
            "col1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "lat": [
                0.5,
                1.5,
                2.5,
                0.45,
                1.45,
                2.45,
                0.45,
                1.45,
                2.45,
                0.45,
                1.45,
                2.45,
            ],
            "lon": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.45, 0.45, 0.45, 1.45, 1.45, 1.45],
        }
    )
    return gpd.GeoDataFrame(
        df,
        geometry=df.apply(lambda row: Point(row.lat, row.lon), axis=1),
        crs="EPSG:4326",
    )


def test_fix_agg_output():
    """default output expansion"""
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
        "fillna": [False, False, False, False],
    }


def test_fix_agg_missing_func_no_fix():
    """don't fix if func missing"""
    assert _fix_agg({}) == {}


def test_fix_agg_output_default():
    """default output expansion and fillna for GEO_INDEX_NAME"""
    assert _fix_agg({"func": "count"}) == {
        "func": ["count"],
        "column": GEO_INDEX_NAME,
        "output": ["index_count"],
        "fillna": [False],
    }


def test_fix_fillna_bool():
    """default fillna bool to array expansion"""
    assert _fix_agg({"func": "count", "fillna": False}) == {
        "func": ["count"],
        "column": GEO_INDEX_NAME,
        "output": ["index_count"],
        "fillna": [False],
    }


def test_fix_agg_default_column():
    """default column for GEO_INDEX_NAME"""
    assert _fix_agg({"func": "count", "output": "pois_count"}) == {
        "func": ["count"],
        "column": GEO_INDEX_NAME,
        "output": ["pois_count"],
        "fillna": [False],
    }


def test_fix_agg_nodefaults():
    """no defaults"""
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


def test_fix_agg_all_defaults():
    """all defaults except count"""
    assert _fix_agg({"func": "count"}) == {
        "func": ["count"],
        "column": GEO_INDEX_NAME,
        "output": ["index_count"],
        "fillna": [False],
    }


def test_check_agg_exception_no_func():
    """agg spec with no func"""
    with pytest.raises(ValueError) as exc_info:
        _check_agg({}, 0, [], pd.Series(dtype=np.float64))

    e = exc_info.value
    assert e.args[0] == "Missing key 'func' in agg[0] {}"


def test_check_agg_exception_column_not_in_data():
    """agg spec with column not in data"""
    with pytest.raises(ValueError) as exc_info:
        _check_agg(
            {"func": ["mean", "sum"], "column": "population", "output": ["pop_mean"]},
            1,
            ["land"],
            pd.Series(data={"land": np.dtype(np.int32)}),
        )
    e = exc_info.value

    assert (
        e.args[0]
        == "Column 'population' in agg[1] {'func': ['mean', 'sum'], 'column': 'population', 'output': ['pop_mean']} does not exist in the data"
    )


def test_check_agg_exception_column_not_numeric():
    """agg spec with column not in data"""
    with pytest.raises(ValueError) as exc_info:
        _check_agg(
            {"func": ["mean", "sum"], "column": "population", "output": ["pop_mean"]},
            1,
            ["population"],
            pd.Series(data={"population": np.dtype(object)}),
        )
    e = exc_info.value

    assert (
        e.args[0]
        == "Column 'population' in agg[1] {'func': ['mean', 'sum'], 'column': 'population', 'output': ['pop_mean']} is not a numeric column in the data"
    )


def test_check_agg_exception_missing_output():
    """agg spec with explicit mismatched func and output"""
    with pytest.raises(ValueError) as exc_info:
        _check_agg(
            {"func": ["mean", "sum"], "column": "population", "output": ["pop_mean"]},
            1,
            ["population"],
            pd.Series(data={"population": np.dtype(np.int32)}),
        )
    e = exc_info.value

    assert (
        e.args[0]
        == "output list ['pop_mean'] doesn't match func list ['mean', 'sum'] in agg[1] {'func': ['mean', 'sum'], 'column': 'population', 'output': ['pop_mean']}"
    )


def test_check_agg_exception_invalid_func():
    """agg spec with unknown func (misspelled)"""
    with pytest.raises(ValueError) as exc_info:
        _check_agg(
            {
                "func": ["mean", "ssum"],
                "column": "population",
                "output": ["pop_mean", "pop_total"],
                "fillna": [True],
            },
            1,
            ["population"],
            pd.Series(data={"population": np.dtype(np.int32)}),
        )
    e = exc_info.value

    assert (
        e.args[0]
        == "Unknown func 'ssum' in agg[1] {'func': ['mean', 'ssum'], 'column': 'population', 'output': ['pop_mean', 'pop_total'], 'fillna': [True]}"
    )


def test_check_agg_exception_missing_fillna():
    """agg spec with explicit mismatched func and output"""
    with pytest.raises(ValueError) as exc_info:
        _check_agg(
            {
                "func": ["mean", "sum"],
                "column": "population",
                "output": ["pop_mean", "pop_total"],
                "fillna": [True],
            },
            1,
            ["population"],
            pd.Series(data={"population": np.dtype(np.int32)}),
        )
    e = exc_info.value

    assert (
        e.args[0]
        == "fillna list [True] doesn't match func list ['mean', 'sum'] in agg[1] {'func': ['mean', 'sum'], 'column': 'population', 'output': ['pop_mean', 'pop_total'], 'fillna': [True]}"
    )


def test_check_agg_exception_valid_agg():
    """agg spec with valid input should not raise exception"""

    _check_agg(
        {
            "func": ["mean", "sum"],
            "column": "population",
            "output": ["pop_mean", "pop_total"],
            "fillna": [True, True],
        },
        1,
        ["population"],
        pd.Series(data={"population": np.dtype(np.int32)}),
    )


def test_validate_aggs():
    """valid aggs list should not throw exception"""
    _validate_aggs(
        [
            {
                "func": ["count"],
                "column": "population",
                "output": ["pop_count"],
                "fillna": [True],
            }
        ],
        pd.DataFrame(data={"population": [1, 2, 3]}),
    )


def test_validate_aggs_with_mismatched_funcs():
    with pytest.raises(ValueError) as exc_info:
        _validate_aggs(
            [{"func": ["mean", "sum"], "column": "population", "output": ["pop_mean"]}],
            pd.DataFrame(data={"population": [1, 2, 3]}),
        )
    e = exc_info.value

    assert (
        e.args[0]
        == "output list ['pop_mean'] doesn't match func list ['mean', 'sum'] in agg[0] {'func': ['mean', 'sum'], 'column': 'population', 'output': ['pop_mean']}"
    )


def test_validate_aggs_with_missing_column():
    with pytest.raises(ValueError) as exc_info:
        _validate_aggs(
            [{"func": ["mean", "sum"], "column": "population", "output": ["pop_mean"]}],
            pd.DataFrame(data={"land": [1, 2, 3]}),
        )
    e = exc_info.value

    assert (
        e.args[0]
        == "Column 'population' in agg[0] {'func': ['mean', 'sum'], 'column': 'population', 'output': ['pop_mean']} does not exist in the data"
    )


def test_validate_aggs_with_duplicate_output_column():
    with pytest.raises(ValueError) as exc_info:
        _validate_aggs(
            [
                {
                    "func": ["mean"],
                    "column": "population",
                    "output": ["pop_mean"],
                    "fillna": [True],
                },
                {
                    "func": ["mean"],
                    "column": "dad",
                    "output": ["pop_mean"],
                    "fillna": [True],
                },
            ],
            pd.DataFrame(data={"population": [1, 2, 3], "dad": [6, 7, 8]}),
        )
    e = exc_info.value

    assert e.args[0] == "Duplicate output column name found for agg[1] ['pop_mean']"


def test_validate_aoi():
    """Raises value error when AOI contains multindex"""
    index = pd.MultiIndex.from_product(
        [
            [
                "type1",
            ],
            ["type2", "type3"],
        ],
    )
    with pytest.raises(ValueError):
        _validate_aoi(pd.DataFrame("-", index, ["col1", "col2"]))


def test_validate_aoi_valid():
    """Raises nothing when APOI contains index"""
    index = pd.RangeIndex(0, 10)
    _validate_aoi(pd.DataFrame("-", index, ["col1", "col2"]))


def test_expand_args():
    assert _expand_aggs(
        [
            {
                "func": ["mean", "sum"],
                "column": "population",
                "output": ["pop_mean", "pop_total"],
                "fillna": [True, True],
            },
            {
                "func": ["mean", "sum"],
                "column": "dads",
                "output": ["dad_mean", "dad_total"],
                "fillna": [True, True],
            },
        ],
    ) == [
        {"func": "mean", "column": "population", "output": "pop_mean", "fillna": True},
        {"func": "sum", "column": "population", "output": "pop_total", "fillna": True},
        {"func": "mean", "column": "dads", "output": "dad_mean", "fillna": True},
        {"func": "sum", "column": "dads", "output": "dad_total", "fillna": True},
    ]


def test_build_add_args():
    assert _build_agg_args(
        [
            {
                "func": "mean",
                "column": "population",
                "output": "pop_mean",
                "fillna": True,
            },
            {
                "func": "sum",
                "column": "population",
                "output": "pop_total",
                "fillna": True,
            },
            {"func": "mean", "column": "dads", "output": "dad_mean", "fillna": True},
            {"func": "sum", "column": "dads", "output": "dad_total", "fillna": True},
        ]
    ) == {
        "pop_mean": ("population", "mean"),
        "pop_total": ("population", "sum"),
        "dad_mean": ("dads", "mean"),
        "dad_total": ("dads", "sum"),
    }


def test_prep_aoi(simple_aoi):
    """simple aoi adds geo index name to aoi"""
    new_aoi = _prep_aoi(simple_aoi)
    assert GEO_INDEX_NAME in list(new_aoi.columns.values)
    assert len(new_aoi) == len(simple_aoi)
    assert new_aoi.drop(GEO_INDEX_NAME, axis=1).equals(simple_aoi)
    assert new_aoi[GEO_INDEX_NAME].equals(simple_aoi.reset_index(level=0)["index"])


def test_prep_aoi_with_existing_index_cols(simple_aoi):
    """aoi with index as pre-existing column name"""
    simple_aoi["index"] = simple_aoi[["col1"]]
    new_aoi = _prep_aoi(simple_aoi)
    assert GEO_INDEX_NAME in list(new_aoi.columns.values)
    assert len(new_aoi) == len(simple_aoi)
    assert new_aoi.drop(GEO_INDEX_NAME, axis=1).equals(simple_aoi)


def test_prep_aoi_with_existing_aoi_index_cols(simple_aoi):
    """aoi with preexisting col name same as GEO_INDEX_NAME"""
    simple_aoi[GEO_INDEX_NAME] = simple_aoi[["col1"]]
    with pytest.raises(ValueError) as exc_info:
        _, _ = _prep_aoi(simple_aoi)

    e = exc_info.value
    assert (
        e.args[0]
        == f"Invalid column name error: AOI column should not match Geowrangler index column {GEO_INDEX_NAME}"
    )


def test_prep_aoi_with_existing_index_and_aoi_index_cols(simple_aoi):
    """aoi with both index and GEO_INDEX_NAME as preexisting col names"""
    simple_aoi["index"] = simple_aoi[["col1"]]
    simple_aoi[GEO_INDEX_NAME] = simple_aoi[["col1"]]
    with pytest.raises(ValueError) as exc_info:
        _, _ = _prep_aoi(simple_aoi)

    e = exc_info.value
    assert (
        e.args[0]
        == f"Invalid column name error: AOI column should not match Geowrangler index column {GEO_INDEX_NAME}"
    )


def test_aggregate_stats(simple_aoi, simple_data):
    """agg stats for simplest agg spec"""
    simple_data.to_crs(simple_aoi.crs)
    aoi = _prep_aoi(simple_aoi)
    features = gpd.sjoin(
        aoi[[GEO_INDEX_NAME, "geometry"]],
        simple_data,
        how="inner",
        predicate="intersects",
    )
    groups = features.groupby(GEO_INDEX_NAME)
    aggs = _expand_aggs([_fix_agg({"func": "count"})])
    results = _aggregate_stats(aoi, groups, aggs)
    assert list(results.columns.values) == [*list(aoi.columns.values), "index_count"]


def test_aggregate_stats_with_existing_aoi_column(simple_aoi, simple_data):
    """agg spec with output col same as preexisting aoi col name"""
    aoi = _prep_aoi(simple_aoi)
    aoi["pois_count"] = aoi.col1
    features = gpd.sjoin(
        aoi[[GEO_INDEX_NAME, "geometry"]],
        simple_data,
        how="inner",
        predicate="intersects",
    )
    groups = features.groupby(GEO_INDEX_NAME)
    aggs = _expand_aggs([_fix_agg({"func": "count", "output": "pois_count"})])
    results = _aggregate_stats(aoi, groups, aggs)
    assert list(results.columns.values) == [*list(aoi.columns.values), "pois_count_y"]


def test_create_zonal_stats(simple_aoi, simple_data):
    """zonal stats for default index col"""
    results = create_zonal_stats(
        simple_aoi, simple_data, aggregations=[{"func": "count"}]
    )
    assert any(
        item in list(results.columns.values)
        for item in [*list(simple_aoi.columns.values), "index_count"]
    )
    assert results.index_count.sum() == 9
    assert results.iloc[0].index_count == 3


def test_create_zonal_stats_with_mismatched_crs(simple_aoi, simple_data):
    simple_data = simple_data.to_crs("EPSG:3136")
    results = create_zonal_stats(
        simple_aoi, simple_data, aggregations=[{"func": "count"}]
    )
    assert any(
        item in list(results.columns.values)
        for item in [*list(simple_aoi.columns.values), "index_count"]
    )
    assert results.crs == simple_aoi.crs
    assert simple_data.crs != results.crs


def test_create_zonal_stats_with_aoi_index_columns(simple_aoi, simple_data):
    simple_aoi["index"] = simple_aoi.col1
    results = create_zonal_stats(
        simple_aoi, simple_data, aggregations=[{"func": "count"}]
    )
    assert any(
        item in list(results.columns.values)
        for item in [*list(simple_aoi.columns.values), "index_count"]
    )
    assert results["index"].equals(simple_aoi.col1)
