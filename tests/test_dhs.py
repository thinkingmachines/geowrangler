import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point

from geowrangler import dhs


def test_load_column_config():
    assert dhs.load_column_config("ph") == dhs.PH_COLUMN_CONFIG


def test_load_column_config_no_matches():
    with pytest.raises(ValueError):
        dhs.load_column_config("gb")


@pytest.fixture()
def household(tmp_path):
    household_df = pd.DataFrame(
        [
            {"hhid": "00001", "hv000": "1", "hv0003": 12, "hv0002": 10, "hv0001": 100},
            {"hhid": "00002", "hv000": "1", "hv0003": 21, "hv0002": 15, "hv0001": 150},
            {"hhid": "00003", "hv000": "2", "hv0003": 31, "hv0002": 5, "hv0001": 50},
            {"hhid": "00004", "hv000": "3", "hv0003": 91, "hv0002": 20, "hv0001": 200},
        ]
    )
    household_path = tmp_path / "FILE.DTA"
    household_df.to_stata(
        household_path,
        variable_labels={
            "hhid": "id",
            "hv000": "Cluster",
            "hv0001": "Wealth Index Factor (up to 5 decimals)",
            "hv0002": "Rooms",
            "hv0003": "TVs",
        },
    )
    yield household_path


@pytest.fixture()
def gps_coordinates(tmp_path):
    gps_gdf = gpd.GeoDataFrame(
        [
            {
                "DHSCLUST": "1",
            },
            {
                "DHSCLUST": "2",
            },
            {
                "DHSCLUST": "3",
            },
        ],
        geometry=[Point(0, 0), Point(1, 1), Point(1, 2)],
        crs=4326,
    )
    gps_path = tmp_path / "GPS.shp"
    gps_gdf.to_file(gps_path, driver="ESRI Shapefile")
    yield gps_path


def test_load_dhs_file(household):
    df = dhs.load_dhs_file(household)
    assert "id" in df.columns
    assert "Cluster" in df.columns
    assert "Wealth Index Factor (up to 5 decimals)" in df.columns


def test_apply_threshold(household):
    household_df = dhs.load_dhs_file(household)
    dhs.apply_threshold(
        household_df, ["TVs", "Rooms"], {"Rooms": [5, 10], "_default": [10, 20]}
    )


def test_wealth_index_pca(household):
    household_df = dhs.load_dhs_file(household)
    dhs.assign_wealth_index(household_df[["Rooms", "TVs"]])


def test_wealth_index_no_pca(household):
    household_df = dhs.load_dhs_file(household)
    dhs.assign_wealth_index(household_df[["Rooms", "TVs"]], use_pca=False)
