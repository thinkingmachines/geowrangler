import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Polygon

import geowrangler.vector_zonal_stats as vzs
from geowrangler.area_zonal_stats import (
    GEO_INDEX_NAME,
    build_agg_area_dicts,
    compute_imputed_stats,
    compute_intersect_stats,
    create_area_zonal_stats,
    expand_area_aggs,
    extract_func,
    fix_area_agg,
    get_source_column,
    validate_area_aoi,
    validate_area_data,
)


@pytest.fixture()
def input_aggs():
    return [
        {
            "column": GEO_INDEX_NAME,
            "func": "count",
            "output": f"{GEO_INDEX_NAME}_count",
            "extras": ["raw"],
        },
        {
            "column": "population",
            "func": "sum",
            "output": "population_sum",
            "extras": [],
        },
        {
            "column": "internet_speed",
            "func": "mean",
            "output": "internet_speed_mean",
            "extras": [],
        },
        {
            "column": "internet_speed",
            "func": "mean",
            "output": "internet_speed_imputed_mean",
            "extras": [
                "imputed",
            ],
        },
    ]


# hide
def square(x, y, size=1):
    return Polygon([(x, y), (x, size + y), (size + x, size + y), (size + x, y)])


# hide
def make_df(
    xsize,
    ysize,
    has_internet=True,
    has_population=True,
    size=1,
    offset_x=0.25,
    offset_y=0.0,
    pop_x_factor=100,
    pop_y_factor=0,
    internet_base_speed=20.0,
    internet_x_exp=2.0,
    internet_y_factor=100,
    crs="EPSG:3857",
):
    d = dict(
        geometry=[
            square(x + offset_x, y + offset_y)
            for x in range(xsize)
            for y in range(ysize)
        ]
    )
    if has_population:
        d["population"] = [
            pop_x_factor * (x + 1) + y * (pop_x_factor * ysize + pop_y_factor)
            for x in range(xsize)
            for y in range(ysize)
        ]
    if has_internet:
        d["internet_speed"] = [
            internet_base_speed / (internet_x_exp**x) + internet_y_factor * y
            for x in range(xsize)
            for y in range(ysize)
        ]
    return gpd.GeoDataFrame(d, crs=crs)


@pytest.fixture()
def simple_data():
    return make_df(3, 1)


@pytest.fixture()
def simple_aoi():
    return make_df(3, 1, has_internet=False, has_population=False, offset_x=0.0)


def test_extract_func():
    assert extract_func("count") == ("count", [])
    assert extract_func("raw_count") == ("count", ["raw"])
    assert extract_func("imputed_count") == ("count", ["imputed"])
    assert extract_func("raw_imputed_count") == ("count", ["raw", "imputed"])


def test_no_fix_area_agg():
    assert fix_area_agg(dict(func="count")) == dict(
        func=["count"],
        column=GEO_INDEX_NAME,
        output=["index_count"],
        fillna=[False],
        extras=[[]],
    )


def test_fix_area_agg():
    assert fix_area_agg(
        dict(
            func=["count", "sum"],
            column="population",
            output=["samples", "population"],
            fillna=[True, True],
        )
    ) == dict(
        func=["count", "sum"],
        column="population",
        output=["samples", "population"],
        fillna=[True, True],
        extras=[[], []],
    )


def test_fix_area_agg_raw_imputed():
    assert fix_area_agg(
        dict(
            func=["raw_imputed_count", "imputed_sum", "raw_mean"],
            column="population",
            output=["samples", "population", "pop_average"],
            fillna=[True, True, False],
        )
    ) == dict(
        func=["count", "sum", "mean"],
        column="population",
        output=["samples", "population", "pop_average"],
        fillna=[True, True, False],
        extras=[["raw", "imputed"], ["imputed"], ["raw"]],
    )


def test_fix_area_agg_aoi_data_func():
    assert fix_area_agg(
        dict(
            func=["aoi_imputed_count", "imputed_sum", "data_mean"],
            column="population",
            output=["samples", "population", "pop_average"],
            fillna=[True, True, False],
        )
    ) == dict(
        func=["count", "sum", "mean"],
        column="population",
        output=["samples", "population", "pop_average"],
        fillna=[True, True, False],
        extras=[["aoi", "imputed"], ["imputed"], ["data"]],
    )


def test_get_source_column_count():

    assert (
        get_source_column(
            dict(
                func="count",
                column="population",
                output="samples",
                fillna=True,
                extras=[],
            )
        )
        == "population"
    )


def test_get_source_column_raw_count():

    assert (
        get_source_column(
            dict(
                func="count",
                column="population",
                output="samples",
                fillna=True,
                extras=["raw"],
            )
        )
        == "population"
    )


def test_get_source_column_sum():

    assert (
        get_source_column(
            dict(
                func="sum",
                column="population",
                output="samples",
                fillna=True,
                extras=[],
            )
        )
        == "intersect_data_population"
    )


def test_get_source_column_mean():

    assert (
        get_source_column(
            dict(
                func="mean",
                column="population",
                output="samples",
                fillna=True,
                extras=[],
            )
        )
        == "intersect_aoi_population"
    )


def test_get_source_column_median():

    assert (
        get_source_column(
            dict(
                func="median",
                column="population",
                output="samples",
                fillna=True,
                extras=[],
            )
        )
        == "population"
    )


def test_get_source_column_aoi_median():

    assert (
        get_source_column(
            dict(
                func="median",
                column="population",
                output="samples",
                fillna=True,
                extras=["aoi"],
            )
        )
        == "intersect_aoi_population"
    )


def test_get_source_column_data_median():

    assert (
        get_source_column(
            dict(
                func="median",
                column="population",
                output="samples",
                fillna=True,
                extras=["data"],
            )
        )
        == "intersect_data_population"
    )


def test_build_agg_area_dicts(input_aggs):
    assert build_agg_area_dicts(input_aggs) == {
        f"{GEO_INDEX_NAME}_count": (f"{GEO_INDEX_NAME}", "count"),
        "intersect_area_sum": ("intersect_area", "sum"),
        "population_sum": ("intersect_data_population", "sum"),
        "internet_speed_mean": ("intersect_aoi_internet_speed", "mean"),
        "internet_speed_imputed_mean": ("intersect_aoi_internet_speed", "mean"),
    }


def test_validate_geographic_aoi(simple_aoi):
    simple_aoi = simple_aoi.to_crs("EPSG:4326")
    with pytest.raises(ValueError) as exc_info:
        validate_area_aoi(simple_aoi)

    e = exc_info.value
    assert (
        e.args[0]
        == "aoi has geographic crs: EPSG:4326, areas maybe incorrectly computed"
    )


def test_validate_planar_aoi(simple_aoi):
    """Non geographic CRS (equiplanar) is valid aoi crs"""
    validate_area_aoi(simple_aoi)


def test_validate_geographic_data(simple_data):
    simple_data = simple_data.to_crs("EPSG:4326")
    with pytest.raises(ValueError) as exc_info:
        validate_area_data(simple_data)

    e = exc_info.value
    assert (
        e.args[0]
        == "data has geographic crs: EPSG:4326, areas maybe incorrectly computed"
    )


def test_validate_mixed_raw_imputed_agg(simple_data):
    """Fix area aggs fixes aggs so they pass vzs validate aggs"""
    fixed_aggs = [
        fix_area_agg(
            dict(
                func=["raw_imputed_count", "imputed_sum", "raw_mean"],
                column="population",
                output=["samples", "population", "pop_average"],
                fillna=[True, True, False],
            )
        )
    ]
    vzs._validate_aggs(fixed_aggs, simple_data)


def test_validate_mixed_data_aoi_imputed_agg(simple_data):
    """Fix area aggs fixes aggs so they pass vzs validate aggs for data and aoi func modifiers"""
    fixed_aggs = [
        fix_area_agg(
            dict(
                func=["aoi_imputed_count", "data_imputed_sum", "data_mean"],
                column="population",
                output=["samples", "population", "pop_average"],
                fillna=[True, True, False],
            )
        )
    ]
    vzs._validate_aggs(fixed_aggs, simple_data)


def test_validate_invalid_mixed_data_agg(simple_data):

    fixed_aggs = [
        fix_area_agg(
            dict(
                func=["raw_data_imputed_count", "imputed_sum", "raw_mean"],
                column="population",
                output=["samples", "population", "pop_average"],
                fillna=[True, True, False],
            )
        )
    ]

    with pytest.raises(ValueError) as exc_info:
        vzs._validate_aggs(fixed_aggs, simple_data)

    e = exc_info.value
    assert (
        e.args[0]
        == "Unknown func 'data_count' in agg[0] {'func': ['data_count', 'sum', 'mean'], 'column': 'population', 'output': ['samples', 'population', 'pop_average'], 'fillna': [True, True, False], 'extras': [['raw', 'imputed'], ['imputed'], ['raw']]}"
    )


def test_validate_invalid_mixed_aoi_agg(simple_data):

    fixed_aggs = [
        fix_area_agg(
            dict(
                func=["raw_aoi_imputed_count", "imputed_sum", "raw_mean"],
                column="population",
                output=["samples", "population", "pop_average"],
                fillna=[True, True, False],
            )
        )
    ]

    with pytest.raises(ValueError) as exc_info:
        vzs._validate_aggs(fixed_aggs, simple_data)

    e = exc_info.value
    assert (
        e.args[0]
        == "Unknown func 'aoi_count' in agg[0] {'func': ['aoi_count', 'sum', 'mean'], 'column': 'population', 'output': ['samples', 'population', 'pop_average'], 'fillna': [True, True, False], 'extras': [['raw', 'imputed'], ['imputed'], ['raw']]}"
    )


def test_validate_invalid_mixed_data_aoi_agg(simple_data):

    fixed_aggs = [
        fix_area_agg(
            dict(
                func=["data_aoi_imputed_count", "imputed_sum", "raw_mean"],
                column="population",
                output=["samples", "population", "pop_average"],
                fillna=[True, True, False],
            )
        )
    ]

    with pytest.raises(ValueError) as exc_info:
        vzs._validate_aggs(fixed_aggs, simple_data)

    e = exc_info.value
    assert (
        e.args[0]
        == "Unknown func 'aoi_count' in agg[0] {'func': ['aoi_count', 'sum', 'mean'], 'column': 'population', 'output': ['samples', 'population', 'pop_average'], 'fillna': [True, True, False], 'extras': [['data', 'imputed'], ['imputed'], ['raw']]}"
    )


def test_validate_planar_data(simple_data):
    """Non geographic CRS (equiplanar) is valid data crs"""

    validate_area_data(simple_data)


def test_expand_area_aggs():
    assert expand_area_aggs(
        [
            dict(
                func=["count", "sum"],
                column="population",
                output=["samples", "population"],
                fillna=[True, True],
                extras=[[], []],
            )
        ]
    ) == [
        dict(
            func="count", column="population", output="samples", fillna=True, extras=[]
        ),
        dict(
            func="sum", column="population", output="population", fillna=True, extras=[]
        ),
    ]


def test_compute_simple_intersect_stats():
    intersect = pd.DataFrame(
        dict(
            pct_data=[1.0, 1.0, 1.0],
            pct_aoi=[1.0, 1.0, 1.0],
            population=[100, 200, 400],
        )
    )
    expanded_aggs = [dict(extras=[], column="population")]
    result = compute_intersect_stats(intersect, expanded_aggs)
    assert "intersect_data_population" in list(result.columns.values)
    assert "intersect_aoi_population" in list(result.columns.values)
    result.equals(
        pd.DataFrame(
            dict(
                pct_data=[1.0, 1.0, 1.0],
                pct_aoi=[1.0, 1.0, 1.0],
                population=[100, 200, 400],
                intersect_aoi_population=[100, 200, 400],
                intersect_data_population=[100, 200, 400],
            )
        )
    )


def test_compute_raw_intersect_stats():
    intersect = pd.DataFrame()
    expanded_aggs = [dict(extras=["raw"])]
    result = compute_intersect_stats(intersect, expanded_aggs)
    assert result.equals(intersect)


def test_compute_empty_intersect_stats():
    intersect = pd.DataFrame()
    expanded_aggs = []
    result = compute_intersect_stats(intersect, expanded_aggs)
    assert result.equals(intersect)


def test_compute_one_intersect_stats():
    intersect = pd.DataFrame(
        dict(
            pct_data=[0.4, 0.1, 0.2, 0.3],
            pct_aoi=[0.2, 0.3, 0.1, 0.4],
            population=[100, 200, 300, 400],
            internet_speed=[10, 20, 30, 100],
        )
    )
    expanded_aggs = [
        dict(column="population", extras=[]),
        dict(column="internet_speed", extras=[]),
    ]
    result = compute_intersect_stats(intersect, expanded_aggs)
    result_columns = list(result.columns.values)
    assert "intersect_data_population" in result_columns
    assert "intersect_aoi_population" in result_columns
    assert "intersect_data_internet_speed" in result_columns
    assert "intersect_aoi_internet_speed" in result_columns
    assert result["intersect_data_population"].equals(
        pd.Series([40.0, 20.0, 60.0, 120.0])
    )
    assert result["intersect_aoi_population"].equals(
        pd.Series([20.0, 60.0, 30.0, 160.0])
    )
    assert result["intersect_data_internet_speed"].equals(
        pd.Series([4.0, 2.0, 6.0, 30.0])
    )
    assert result["intersect_aoi_internet_speed"].equals(
        pd.Series([2.0, 6.0, 3.0, 40.0])
    )


def test_compute_imputed_stats():
    intersect = pd.DataFrame(
        dict(
            internet_speed_mean=[10, 20, 30, 40],
            population_sum=[100, 50, 10, 20],
            aoi_area=[20.0, 40.0, 30.0, 20.0],
            intersect_area_sum=[20.0, 20.0, 30.0, 10.0],
        )
    )
    expanded_aggs = [
        dict(output="internet_speed_mean", extras=["imputed"]),
        dict(output="population_sum", extras=[]),
    ]
    results = compute_imputed_stats(intersect, expanded_aggs)
    assert results["internet_speed_mean"].equals(pd.Series([10.0, 40.0, 30.0, 80.0]))
    assert results["population_sum"].equals(pd.Series([100, 50, 10, 20]))


def test_create_area_zonal_stats(simple_aoi, simple_data):
    aggregations = [
        dict(func="sum", column="population"),
        dict(func=["min", "max", "imputed_mean"], column="internet_speed"),
        dict(func="count"),
    ]
    results = create_area_zonal_stats(
        simple_aoi, simple_data, aggregations=aggregations
    )
    results_columns = list(results.columns.values)
    assert "intersect_area_sum" in results_columns
    assert "index_count" in results_columns
    assert "population_sum" in results_columns
    assert "internet_speed_mean" in results_columns
    assert "internet_speed_min" in results_columns
    assert "internet_speed_max" in results_columns
    assert results["index_count"].equals(pd.Series([1, 2, 2]))
    assert results["intersect_area_sum"].equals(pd.Series([0.75, 1.0, 1.0]))
    assert results["internet_speed_mean"].equals(pd.Series([20.0, 6.25, 3.125]))
    assert results["internet_speed_min"].equals(pd.Series([0.0, 10.0, 5.0]))
    assert results["internet_speed_max"].equals(pd.Series([20.0, 20.0, 10.0]))
    assert results["population_sum"].equals(pd.Series([75.0, 175.0, 275.0]))


def test_create_area_zonal_stats_drop_intersect(simple_aoi, simple_data):
    aggregations = [
        dict(func="sum", column="population"),
        dict(func=["min"], column="internet_speed"),
        dict(func="count"),
    ]
    results = create_area_zonal_stats(
        simple_aoi,
        simple_data,
        aggregations=aggregations,
        include_intersect=False,
        fix_min=False,
    )
    results_columns = list(results.columns.values)
    assert "intersect_area_sum" not in results_columns
    assert "internet_speed_min" in results_columns
    assert results["internet_speed_min"].equals(pd.Series([20.0, 10.0, 5.0]))
