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
    
    gdf = gpd.GeoDataFrame(df, geometry=df.apply(square, axis=1), crs="EPSG:3857")
    gdf = gdf.to_crs("epsg:4326")

    return gdf


def test_create_raster_zonal_stats(simple_aoi):
    raster_file = "data/sample_terrain.tif"
    simple_aoi = simple_aoi.to_crs("epsg:3857")
    results = rzs.create_raster_zonal_stats(
        simple_aoi,
        raster_file,
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
    raster_file = "data/phl_ppp_2020_constrained.tif"
    file_aoi = "data/simple_aoi.geojson"

    results = rzs.create_raster_zonal_stats(
        file_aoi,
        raster_file,
        aggregation=dict(func=["mean", "min", "max", "std"], column="population"),
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
        "population_min",
        "population_max",
        "population_mean",
        "population_std",
    ]


def test_raster_zonal_stats_nodata():
    raster_file = "data/phl_ppp_2020_constrained.tif"
    file_aoi = "data/region3_admin.geojson"
    results = rzs.create_raster_zonal_stats(
        file_aoi,
        raster_file,
        aggregation=dict(
            func=["sum"],
            column="population",
            output=["population_count"],
            fillna=[True],
        ),
        extra_args=dict(nodata=-99999),
    )
    assert results["population_count"].iloc[0] > 0

def test_create_raster_zonal_stats_crs_mismatch(simple_aoi):
    raster_file = "data/sample_terrain.tif"
   
    with pytest.raises(ValueError):
        results = rzs.create_raster_zonal_stats(
            simple_aoi,
            raster_file,
            aggregation=dict(func=["mean", "min", "max", "std"], column="elevation"),
            extra_args=dict(nodata=np.nan),
        )
    
def test_raster_zonal_stats_nodata_default():
    raster_file = "data/phl_ppp_2020_constrained.tif"
    file_aoi = "data/region3_admin.geojson"
    results = rzs.create_raster_zonal_stats(
        file_aoi,
        raster_file,
        aggregation=dict(
            func=["sum"],
            column="population",
            output=["population_count"],
            fillna=[True],
        ),
    )
    assert results["population_count"].values[0] > 0

# exactextract tests
def test_create_exactextract_zonal_stats(simple_aoi):
    raster_file = "data/sample_terrain.tif"
    simple_aoi = simple_aoi.to_crs("epsg:3857")
    results = rzs.create_exactextract_zonal_stats(
        simple_aoi,
        raster_file,
        aggregation=dict(band=1, func=["mean", "max", "min", "stdev"], output="elevation"),
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
        "elevation_mean",
        "elevation_max",
        "elevation_min",
        "elevation_stdev",
    ]

def test_create_exactextract_zonal_stats_invalid_band(simple_aoi):
    raster_file = "data/sample_terrain.tif"
    simple_aoi = simple_aoi.to_crs("epsg:3857")
    with pytest.warns(UserWarning):
        results = rzs.create_exactextract_zonal_stats(
            simple_aoi,
            raster_file,
            aggregation=[
                dict(band=1, func=["mean", "max", "min", "stdev"], output="elevation"),
                dict(band=2, func=["mean", "max", "min", "stdev"], output="elevation")
            ],    
        )
    
def test_create_exactextract_zonal_stats_from_file():
    raster_file = "data/phl_ppp_2020_constrained.tif"
    file_aoi = "data/simple_aoi.geojson"
    results = rzs.create_exactextract_zonal_stats(
        file_aoi,
        raster_file,
        aggregation=[dict(band=1, func=["mean", "min", "max", "stdev"], output="population")],
    )
    print(results)
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
        "population_mean",
        "population_min",
        "population_max",
        "population_stdev",
    ]

def test_exactextract_zonal_stats_multiband():
    aq_file = "data/ph_s5p_AER_AI_340_380.tiff"
    file_aoi = "data/region3_admin.geojson"
    file_aoi = gpd.read_file(file_aoi)
    results = rzs.create_exactextract_zonal_stats(
        file_aoi,
        aq_file,
        aggregation=[
            dict(band=1, func=["mean", "sum"], nodata_val=-9999), # default - band1_mean, band1_sum
            dict(band=2, func=["mean", "sum"]), # default - band2_mean, band2_sum
            dict(band=2, func=["mean", "sum"], output="prefix"), # prefix_mean, prefix_sum
            dict(band=1, func=["mean", "sum", "count"], output=["aer_ai_mean", "aer_ai_sum", "aer_ai_count"]),
        ],
    )
    assert list(results.columns.values) == [
        "Reg_Code",
        "Reg_Name",
        "Reg_Alt_Name",
        "geometry",
        "band_1_mean",
        "band_1_sum",
        "band_2_mean",
        "band_2_sum",
        "prefix_mean",
        "prefix_sum",
        "aer_ai_mean",
        "aer_ai_sum",
        "aer_ai_count"
    ]

def test_exactextract_zonal_stats_multiband_crs_mismatch():
    aq_file = "data/ph_s5p_AER_AI_340_380.tiff"
    file_aoi = "data/region3_admin.geojson"
    file_aoi = gpd.read_file(file_aoi).to_crs("EPSG:3857")
    
    with pytest.raises(ValueError):
        results = rzs.create_exactextract_zonal_stats(
            file_aoi,
            aq_file,
            aggregation=[
                dict(band=1, func=["mean", "sum"], nodata_val=-9999), # default - band1_mean, band1_sum
                dict(band=2, func=["mean", "sum"]), # default - band2_mean, band2_sum
                dict(band=2, func=["mean", "sum"], output="prefix"), # prefix_mean, prefix_sum
                dict(band=1, func=["mean", "sum", "count"], output=["aer_ai_mean", "aer_ai_sum", "aer_ai_count"]),
            ],
        )
         
def test_exactextract_geojson(simple_aoi):
    "Check if output returns pandas output despite output option"
    raster_file = "data/sample_terrain.tif"
    simple_aoi = simple_aoi.to_crs("epsg:3857")
    with pytest.warns(UserWarning):
        results = rzs.create_exactextract_zonal_stats(
            simple_aoi,
            raster_file,
            aggregation=[
                dict(band=1, func=["sum"], output="elevation"),
            ],
            extra_args = dict(output="geojson")
        )
    assert isinstance(results, (pd.DataFrame, gpd.GeoDataFrame))

def test_exactextract_include_cols(simple_aoi):
    "Check if output returns specified columns"
    raster_file = "data/sample_terrain.tif"
    simple_aoi = simple_aoi.to_crs("epsg:3857")
    results = rzs.create_exactextract_zonal_stats(
        simple_aoi,
        raster_file,
        aggregation=[
            dict(band=1, func=["sum"], output="elevation"),
        ],
        include_cols=["col1", "lat0"]
    )
    assert list(results.columns.values) == [
        "col1",
        "lat0",
        "elevation_sum",
    ]

def test_exactextract_include_geom(simple_aoi):
    "Check if output returns geom"
    raster_file = "data/sample_terrain.tif"
    simple_aoi = simple_aoi.to_crs("epsg:3857")
    results = rzs.create_exactextract_zonal_stats(
        simple_aoi,
        raster_file,
        aggregation=dict(band=1, func=["sum"], output="elevation"),
        include_geom=True,
    )
    assert isinstance(results, (pd.DataFrame, gpd.GeoDataFrame))