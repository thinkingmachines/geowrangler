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
