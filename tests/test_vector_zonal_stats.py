import warnings

warnings.filterwarnings(action="ignore", category=UserWarning, module="geopandas")

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point, Polygon

from geowrangler.vector_zonal_stats import (
    _aggregate_stats,
    _fix_agg,
    _prep_aoi,
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


def test_aggregate_stats(simple_aoi, simple_data):
    simple_data.to_crs(simple_aoi.crs)
    aoi, _, _ = _prep_aoi(simple_aoi)
    features = gpd.sjoin(
        aoi[["aoi_index", "geometry"]], simple_data, how="inner", predicate="intersects"
    )
    groups = features.groupby("aoi_index")
    agg = _fix_agg({"func": "count"})
    results = _aggregate_stats(aoi, groups, agg)
    assert list(results.columns.values) == [
        *list(aoi.columns.values),
        "aoi_index_count",
    ]


def test_aggregate_stats_with_existing_aoi_column(simple_aoi, simple_data):

    aoi, _, _ = _prep_aoi(simple_aoi)
    aoi["pois_count"] = aoi.col1
    features = gpd.sjoin(
        aoi[["aoi_index", "geometry"]], simple_data, how="inner", predicate="intersects"
    )
    groups = features.groupby("aoi_index")
    agg = _fix_agg({"func": "count", "output": "pois_count"})
    results = _aggregate_stats(aoi, groups, agg)
    assert list(results.columns.values) == [*list(aoi.columns.values), "pois_count_y"]


def test_create_zonal_stats(simple_aoi, simple_data):
    results = create_zonal_stats(
        simple_aoi, simple_data, aggregations=[{"func": "count"}]
    )
    assert list(results.columns.values) == [
        *list(simple_aoi.columns.values),
        "aoi_index_count",
    ]


def test_create_zonal_stats_with_mismatched_crs(simple_aoi, simple_data):
    simple_data = simple_data.to_crs("EPSG:3136")
    results = create_zonal_stats(
        simple_aoi, simple_data, aggregations=[{"func": "count"}]
    )
    assert list(results.columns.values) == [
        *list(simple_aoi.columns.values),
        "aoi_index_count",
    ]


def test_create_zonal_stats_with_aoi_index_columns(simple_aoi, simple_data):
    # simple_aoi['index'] = simple_aoi.col1
    # simple_aoi['aoi_index'] = simple_aoi.col1
    results = create_zonal_stats(
        simple_aoi, simple_data, aggregations=[{"func": "count"}]
    )
    assert list(results.columns.values) == [
        *list(simple_aoi.columns.values),
        "aoi_index_count",
    ]
    # assert results['index'].equals(simple_aoi.col1)
    # assert results['aoi_index'].equals(simple_aoi.col1)
