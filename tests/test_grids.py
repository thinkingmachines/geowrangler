import geopandas as gpd
import pytest
from geopandas import GeoDataFrame
from shapely.geometry import Polygon

from geowrangler import grids


@pytest.fixture
def sample_gdf():
    yield GeoDataFrame(
        geometry=Polygon(
            [
                (0, 0),
                (1, 0),
                (1, 1),
                (0, 1),
            ]
        ),
        crs="EPSG:3857",
    )


def test_create_grids():
    grid_generator = grids.GridGenerator(sample_gdf, grid_size=100)
    assert grid_generator.create_grid(0, 0) == Polygon(
        [
            (0, 0),
            (100, 0),
            (100, 100),
            (0, 100),
        ]
    )


def test_get_ranges():
    gdf = gpd.read_file("data/region3_admin.geojson")
    grid_generator = grids.GridGenerator(gdf, 5000)
    grid_range = grid_generator.get_ranges()
    assert grid_range[0].shape[0] == 55
    assert grid_range[1].shape[0] == 49


def test_generate_grids():
    gdf = gpd.read_file("data/region3_admin.geojson")
    grid_generator = grids.GridGenerator(gdf, 15000)
    grids_gdf = grid_generator.generate_grids()
    assert len(grids_gdf) == 154
