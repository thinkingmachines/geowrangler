import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import Polygon

from geowrangler import grids


@pytest.fixture
def sample_gdf():
    """Create an L shape Polygon"""
    yield gpd.GeoDataFrame(
        geometry=[
            Polygon(
                [
                    (0, 0),
                    (2, 0),
                    (2, 1),
                    (1, 1),
                    (1, 3),
                    (0, 3),
                ]
            )
        ],
        crs="EPSG:4326",
    )


def test_create_grids(sample_gdf):
    grid_generator = grids.SquareGridGenerator(sample_gdf, cell_size=100)
    assert grid_generator.create_cell(0, 0) == Polygon(
        [
            (0, 0),
            (100, 0),
            (100, 100),
            (0, 100),
        ]
    )


def test_generate_grids(sample_gdf):
    grid_generator = grids.SquareGridGenerator(sample_gdf, 15000)
    grids_gdf = grid_generator.generate_grid()
    assert len(grids_gdf) == 240
    # Check if area of each grid is what we expect
    assert grids_gdf.to_crs("EPSG:3857").area.apply(np.isclose, b=15000**2).all()


def test_generate_grids_w_custom_boundary(sample_gdf):
    grid_generator = grids.SquareGridGenerator(
        sample_gdf, 15000, boundary=(0, 0, 5000000, 5000000)
    )
    grids_gdf = grid_generator.generate_grid()

    assert len(grids_gdf) == 240
    # Check if area of each grid is what we expect
    assert grids_gdf.to_crs("EPSG:3857").area.apply(np.isclose, b=15000**2).all()


def test_generate_grids_w_custom_boundary_2(sample_gdf):
    boundary = grids.SquareGridBoundary(0, 0, 5000000, 5000000)
    grid_generator = grids.SquareGridGenerator(sample_gdf, 15000, boundary=boundary)
    grids_gdf = grid_generator.generate_grid()
    assert len(grids_gdf) == 240
    # Check if area of each grid is what we expect
    assert grids_gdf.to_crs("EPSG:3857").area.apply(np.isclose, b=15000**2).all()
