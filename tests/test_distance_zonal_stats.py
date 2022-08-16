import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point, Polygon

from geowrangler.distance_zonal_stats import (
    INTERNAL_DISTANCE_COL,
    build_agg_distance_dicts,
    create_distance_zonal_stats,
)


def make_point_df(
    xsize,
    ysize,
    has_internet=True,
    has_population=True,
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
            Point(x + offset_x, y + offset_y)
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


def square(x, y, size=1):
    return Polygon([(x, y), (x, size + y), (size + x, size + y), (size + x, y)])


def make_df(
    xsize,
    ysize,
    has_internet=True,
    has_population=True,
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
def simple_aoi():
    return make_df(3, 1, has_internet=False, has_population=False, offset_x=0.0)


@pytest.fixture()
def simple_data():
    return make_df(3, 1)


@pytest.fixture()
def simple_point_data():
    return make_point_df(3, 5, offset_x=0.5, offset_y=3.0)


def test_build_agg_distance_dicts():
    distance_col = "distance"
    expanded_aggs = [dict(func="sum", column="population", output="population_sum")]
    agg_dicts = build_agg_distance_dicts(expanded_aggs, distance_col)
    assert agg_dicts == dict(
        distance=(INTERNAL_DISTANCE_COL, "mean"), population_sum=("population", "sum")
    )


def test_create_distance_zonal_stats(simple_aoi, simple_point_data):
    results = create_distance_zonal_stats(
        simple_aoi,
        simple_point_data,
        max_distance=7,
        aggregations=[
            dict(func="count"),
            dict(func="sum", column="population"),
            dict(func="mean", column="internet_speed"),
        ],
    )
    assert results["index_count"].equals(pd.Series([1, 1, 1]))
    assert results["population_sum"].equals(pd.Series([100, 200, 300]))
    assert results["internet_speed_mean"].equals(pd.Series([20.0, 10.0, 5.0]))
    assert results["nearest"].equals(pd.Series([2.0, 2.0, 2.0]))


def test_create_distance_zonal_stats_areas(simple_aoi, simple_data):
    results = create_distance_zonal_stats(
        simple_aoi,
        simple_data,
        max_distance=1,
        aggregations=[
            dict(func="count"),
            dict(func="sum", column="population"),
            dict(func="mean", column="internet_speed"),
        ],
    )
    assert results["index_count"].equals(pd.Series([1, 2, 2]))
    assert results["population_sum"].equals(pd.Series([100, 300, 500]))
    assert results["internet_speed_mean"].equals(pd.Series([20.0, 15.0, 7.5]))
    assert results["nearest"].equals(pd.Series([0.0, 0.0, 0.0]))
