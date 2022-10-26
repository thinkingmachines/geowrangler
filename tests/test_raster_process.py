import shutil
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
import rasterio as rio
import rasterio.coords as cds
from shapely.geometry import Polygon

import geowrangler.raster_process as rp


def make_circle_geometry(lat, lon, buffer, crs="epsg:4326"):
    df = pd.DataFrame({"lat": [lat], "lon": [lon]})
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs=crs)
    gdf["geometry"] = gdf["geometry"].buffer(buffer)
    return gdf


@pytest.fixture()
def circle_geometry():
    yield make_circle_geometry(14.599512, 120.984222, 1)


def test_query_window_by_gdf(circle_geometry, capsys):
    input_image = "data/phl_ppp_2020_constrained.tif"
    output_folder = Path("data/circle_files")
    if output_folder.exists():
        shutil.rmtree(output_folder, ignore_errors=False)
    output_folder.mkdir(exist_ok=False, parents=True)

    rp.query_window_by_gdf(input_image, output_folder, circle_geometry)
    captured = capsys.readouterr()
    assert captured.out == "data/circle_files/output_0.tif\n"
    with rio.open(output_folder / "output_0.tif") as dst:
        bounds = dst.bounds
    assert np.isclose([*bounds], [*circle_geometry.iloc[0].geometry.bounds]).all(axis=0)
    if output_folder.exists():
        shutil.rmtree(output_folder, ignore_errors=False)
