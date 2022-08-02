import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point

from geowrangler import dhs


def test_get_approximate_col_name_wealth_index():
    columns = ["Wealth Index Factor (up to 5 decimal places)", "wealth index"]
    col_name = "wealth index factor"
    assert dhs.get_approximate_col_name(columns, col_name) == columns[0]


def test_get_approximate_col_name_cluster():
    columns = ["cluste", "Cluster Name", "cluster id"]
    col_name = "cluster"
    assert dhs.get_approximate_col_name(columns, col_name) == columns[1]


def test_get_approximate_col_name_no_matches():
    columns = ["cluste", "Cluster Name", "cluster id"]
    col_name = "wealth index factor"
    with pytest.raises(IndexError):
        dhs.get_approximate_col_name(columns, col_name)


@pytest.fixture()
def household(tmp_path):
    household_df = pd.DataFrame(
        [
            {"hhid": "00001", "hv000": "1", "hv0001": 100},
            {"hhid": "00002", "hv000": "1", "hv0001": 150},
            {"hhid": "00003", "hv000": "2", "hv0001": 50},
            {"hhid": "00004", "hv000": "3", "hv0001": 200},
        ]
    )
    household_path = tmp_path / "FILE.DTA"
    household_df.to_stata(
        household_path,
        variable_labels={
            "hhid": "id",
            "hv000": "Cluster",
            "hv0001": "Wealth Index Factor (up to 5 decimals)",
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


def test_generate_dhs_cluster_data(household, gps_coordinates):
    summary = dhs.generate_dhs_cluster_data(household, gps_coordinates)
    assert summary[summary.DHSCLUST == "1"].iloc[0]["Wealth Index"] == 125.0
    assert summary[summary.DHSCLUST == "2"].iloc[0]["Wealth Index"] == 50.0
    assert summary[summary.DHSCLUST == "3"].iloc[0]["Wealth Index"] == 200.0
