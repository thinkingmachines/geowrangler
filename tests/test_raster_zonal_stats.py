import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Polygon

import geowrangler.raster_zonal_stats as rzs


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


def test_create_raster_zonal_stats(simple_aoi):
    terrain_file = "data/sample_terrain.tif"
    results = rzs.create_raster_zonal_stats(
        simple_aoi,
        terrain_file,
        aggregation=dict(func=["mean", "min", "max", "std"], column="elevation"),
        extra_args=dict(nodata=np.nan),
    )
    assert list(results.columns.values) == [
        "col1",
        "lat0",
        "lon0",
        "lat1",
        "lon1",
        "lat2",
        "lon2",
        "lat3",
        "lon3",
        "geometry",
        "elevation_min",
        "elevation_max",
        "elevation_mean",
        "elevation_std",
    ]


def test_create_raster_zonal_stats_from_file():
    terrain_file = "data/sample_terrain.tif"
    file_aoi = "data/simple_aoi.geojson"
    results = rzs.create_raster_zonal_stats(
        file_aoi,
        terrain_file,
        aggregation=dict(func=["mean", "min", "max", "std"], column="elevation"),
        extra_args=dict(
            nodata=np.nan,
            # everything below will be ignored
            stats=["sum", "count"],
            geojson_out=True,
            categorical=True,
            categorical_map=[np.nan],
            prefix="myownprefix",
            add_stats=["majority", "unique"],
        ),
    )
    assert list(results.columns.values) == [
        "col1",
        "lat0",
        "lon0",
        "lat1",
        "lon1",
        "lat2",
        "lon2",
        "lat3",
        "lon3",
        "geometry",
        "elevation_min",
        "elevation_max",
        "elevation_mean",
        "elevation_std",
    ]


def test_raster_zonal_stats_nodata():
    terrain_file = "data/phl_ppp_2020_constrained.tif"
    file_aoi = "data/region3_admin.geojson"
    results = rzs.create_raster_zonal_stats(
        file_aoi,
        terrain_file,
        aggregation=dict(
            func=["sum"],
            column="population",
            output=["population_count"],
            fillna=[True],
        ),
        extra_args=dict(nodata=-99999),
    )
    assert results["population_count"].iloc[0] > 0


def test_raster_zonal_stats_nodata_default():
    terrain_file = "data/phl_ppp_2020_constrained.tif"
    file_aoi = "data/region3_admin.geojson"
    results = rzs.create_raster_zonal_stats(
        file_aoi,
        terrain_file,
        aggregation=dict(
            func=["sum"],
            column="population",
            output=["population_count"],
            fillna=[True],
        ),
    )
    assert results["population_count"].iloc[0] > 0
