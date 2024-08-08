import geopandas as gpd
import numpy as np
import pandas as pd
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
    grid_generator = grids.SquareGridGenerator(cell_size=100)
    assert grid_generator.create_cell(0, 0) == Polygon(
        [
            (0, 0),
            (100, 0),
            (100, 100),
            (0, 100),
        ]
    )


def test_generate_grids(sample_gdf):
    grid_generator = grids.SquareGridGenerator(15000)
    grids_gdf = grid_generator.generate_grid(sample_gdf)
    assert len(grids_gdf) == 240
    # Check if area of each grid is what we expect
    assert grids_gdf.to_crs("EPSG:3857").area.apply(np.isclose, b=15000**2).all()


def test_generate_grids_w_custom_boundary(sample_gdf):
    grid_generator = grids.SquareGridGenerator(15000, boundary=(0, 0, 10, 10))
    grids_gdf = grid_generator.generate_grid(
        sample_gdf,
    )

    assert len(grids_gdf) == 240
    # Check if area of each grid is what we expect
    assert grids_gdf.to_crs("EPSG:3857").area.apply(np.isclose, b=15000**2).all()


def test_generate_grids_w_custom_boundary_2(sample_gdf):
    boundary = grids.SquareGridBoundary(
        0, 0, 5000000, 5000000
    )  # SquareGridBoundary used the target projection
    grid_generator = grids.SquareGridGenerator(15000, boundary=boundary)
    grids_gdf = grid_generator.generate_grid(sample_gdf)
    assert len(grids_gdf) == 240
    # Check if area of each grid is what we expect
    assert grids_gdf.to_crs("EPSG:3857").area.apply(np.isclose, b=15000**2).all()


def test_boundary_smaller_then_a_cell():
    boundary = grids.SquareGridBoundary(0, 0, 5000000, 5000000)
    _, xrange, _, yrange = boundary.get_range_subset(2.5, 2.5, 5, 5, 10)
    # 2 because we add a boundary
    assert len(xrange) == 2
    assert len(yrange) == 2


def test_generate_grids_aoi_outside_boundary(sample_gdf):
    grid_generator = grids.SquareGridGenerator(15000, boundary=(10, 10, 20, 20))
    grids_gdf = grid_generator.generate_grid(sample_gdf)

    assert len(grids_gdf) == 0


def test_h3_grid_generator(sample_gdf):
    grid_generator = grids.H3GridGenerator(5)
    grids_gdf = grid_generator.generate_grid(sample_gdf)
    assert "geometry" in grids_gdf
    assert isinstance(grids_gdf, gpd.GeoDataFrame)
    assert len(grids_gdf) == 262


def test_h3_grid_generator_mutliple_polygons(sample_gdf):
    grid_generator = grids.H3GridGenerator(5)
    gdf2 = gpd.GeoDataFrame(
        geometry=[
            Polygon(
                [
                    (3, 3),
                    (3, 4),
                    (4, 3),
                ]
            )
        ],
        crs="EPSG:4326",
    )
    grids_gdf = grid_generator.generate_grid(pd.concat([gdf2, sample_gdf]))
    assert "geometry" in grids_gdf
    assert isinstance(grids_gdf, gpd.GeoDataFrame)
    assert len(grids_gdf) == 292


def test_h3_grid_generator_return_geometry_false(
    sample_gdf,
):
    grid_generator = grids.H3GridGenerator(5, return_geometry=False)
    grids_gdf = grid_generator.generate_grid(sample_gdf)
    assert "geometry" not in grids_gdf
    assert isinstance(grids_gdf, pd.DataFrame)
    assert len(grids_gdf) == 262


def test_h3_grid_generator_get_hexes_for_polygon():
    grid_generator = grids.H3GridGenerator(
        5,
    )
    hex_ids = grid_generator.get_hexes_for_polygon(Polygon([(0, 0.0), (0, 1), (1, 1)]))
    assert len(hex_ids) == 31


BING_TILE_N_TILES = 36
BING_TILE_MULTIPOLY_N_TILES = 46

def test_bing_tile_grid_generator(sample_gdf):
    grid_generator = grids.BingTileGridGenerator(10)
    grids_gdf = grid_generator.generate_grid(sample_gdf)
    assert "geometry" in grids_gdf
    assert isinstance(grids_gdf, gpd.GeoDataFrame)
    assert len(grids_gdf) == BING_TILE_N_TILES


def test_bing_tile_grid_generator_mutliple_polygons(sample_gdf):
    grid_generator = grids.BingTileGridGenerator(10)
    gdf2 = gpd.GeoDataFrame(
        geometry=[
            Polygon(
                [
                    (3, 3),
                    (3, 4),
                    (4, 3),
                ]
            )
        ],
        crs="EPSG:4326",
    )
    grids_gdf = grid_generator.generate_grid(pd.concat([gdf2, sample_gdf]))
    assert "geometry" in grids_gdf
    assert isinstance(grids_gdf, gpd.GeoDataFrame)
    assert len(grids_gdf) == BING_TILE_MULTIPOLY_N_TILES


def test_bing_tile_grid_generator_return_geometry_false(
    sample_gdf,
):
    grid_generator = grids.BingTileGridGenerator(10, return_geometry=False)
    grids_gdf = grid_generator.generate_grid(sample_gdf)
    assert "geometry" not in grids_gdf
    assert isinstance(grids_gdf, pd.DataFrame)
    assert len(grids_gdf) == BING_TILE_N_TILES


def test_bing_tile_grid_generator_add_xyz_true(
    sample_gdf,
):
    grid_generator = grids.BingTileGridGenerator(10, add_xyz_cols=True)
    grids_gdf = grid_generator.generate_grid(sample_gdf)
    assert "x" in grids_gdf
    assert "y" in grids_gdf
    assert "z" in grids_gdf
    assert isinstance(grids_gdf, pd.DataFrame)
    assert len(grids_gdf) == BING_TILE_N_TILES


def test_bing_tile_grid_generator_join(sample_gdf):
    grid_generator = grids.BingTileGridGenerator(10)
    grids_gdf = grid_generator.generate_grid_join(sample_gdf)
    assert "geometry" in grids_gdf
    assert isinstance(grids_gdf, gpd.GeoDataFrame)
    assert len(grids_gdf) == BING_TILE_N_TILES


def test_bing_tile_grid_generator_join_mutliple_polygons(sample_gdf):
    grid_generator = grids.BingTileGridGenerator(10)
    gdf2 = gpd.GeoDataFrame(
        geometry=[
            Polygon(
                [
                    (3, 3),
                    (3, 4),
                    (4, 3),
                ]
            )
        ],
        crs="EPSG:4326",
    )
    grids_gdf = grid_generator.generate_grid_join(pd.concat([gdf2, sample_gdf]))
    assert "geometry" in grids_gdf
    assert isinstance(grids_gdf, gpd.GeoDataFrame)
    assert len(grids_gdf) == BING_TILE_MULTIPOLY_N_TILES


def test_bing_tile_grid_generator_join_return_geometry_false(
    sample_gdf,
):
    grid_generator = grids.BingTileGridGenerator(10, return_geometry=False)
    grids_gdf = grid_generator.generate_grid_join(sample_gdf)
    assert "geometry" not in grids_gdf
    assert isinstance(grids_gdf, pd.DataFrame)
    assert len(grids_gdf) == BING_TILE_N_TILES

# FastBingTileGridGenerator returns 6 more tiles than BingTileGridGenerator because it considered tiles exactly on the border
FAST_BING_TILE_N_TILES = BING_TILE_N_TILES + 6
FAST_BING_TILE_MULTIPOLY_N_TILES = BING_TILE_MULTIPOLY_N_TILES + 6

def test_fast_bing_tile_grid_generator(sample_gdf):
    grid_generator = grids.FastBingTileGridGenerator(10)
    grids_gdf = grid_generator.generate_grid(sample_gdf)
    assert "geometry" in grids_gdf
    assert isinstance(grids_gdf, gpd.GeoDataFrame)
    assert len(grids_gdf) == FAST_BING_TILE_N_TILES 


def test_fast_bing_tile_grid_generator_mutliple_polygons(sample_gdf):
    grid_generator = grids.FastBingTileGridGenerator(10)
    gdf2 = gpd.GeoDataFrame(
        geometry=[
            Polygon(
                [
                    (3, 3),
                    (3, 4),
                    (4, 3),
                ]
            )
        ],
        crs="EPSG:4326",
    )
    grids_gdf = grid_generator.generate_grid(pd.concat([gdf2, sample_gdf]))
    assert "geometry" in grids_gdf
    assert isinstance(grids_gdf, gpd.GeoDataFrame)
    assert len(grids_gdf) == FAST_BING_TILE_MULTIPOLY_N_TILES


def test_fast_bing_tile_grid_generator_return_geometry_false(
    sample_gdf,
):
    grid_generator = grids.FastBingTileGridGenerator(10, return_geometry=False)
    grids_gdf = grid_generator.generate_grid(sample_gdf)
    assert "geometry" not in grids_gdf
    assert isinstance(grids_gdf, pd.DataFrame)
    assert len(grids_gdf) == FAST_BING_TILE_N_TILES


def test_fast_bing_tile_grid_generator_add_xyz_true(
    sample_gdf,
):
    grid_generator = grids.FastBingTileGridGenerator(10, add_xyz_cols=True)
    grids_gdf = grid_generator.generate_grid(sample_gdf)
    assert "x" in grids_gdf
    assert "y" in grids_gdf
    assert "z" in grids_gdf
    assert isinstance(grids_gdf, pd.DataFrame)
    assert len(grids_gdf) == FAST_BING_TILE_N_TILES