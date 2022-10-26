import geopandas as gpd
import numpy as np
import pytest

import geowrangler.grids as grids
import geowrangler.tile_clustering as tc


@pytest.fixture()
def grid_gdf5k():
    rs = np.random.default_rng(seed=42)
    region3_gdf = gpd.read_file("data/region3_admin.geojson")
    grid_generator5k = grids.SquareGridGenerator(5_000)
    grid = grid_generator5k.generate_grid(region3_gdf)
    grid["score"] = rs.random(len(grid))
    grid["class"] = grid["score"] > 0.7
    yield grid


def test_tile_clustering(grid_gdf5k):
    tileclustering = tc.TileClustering()
    gdf5k = tileclustering.cluster_tiles(grid_gdf5k, category_col="class")
    assert len(gdf5k) == 1074
    assert gdf5k["tile_cluster"].nunique() == 159


def test_tile_clustering_eightway(grid_gdf5k):
    tileclustering = tc.TileClustering(cluster_type="eight_way")
    gdf5k = tileclustering.cluster_tiles(grid_gdf5k, category_col="class")
    assert len(gdf5k) == 1074
    assert gdf5k["tile_cluster"].nunique() == 70


def test_tile_clustering_no_category(grid_gdf5k):
    tileclustering = tc.TileClustering()
    gdf5k = tileclustering.cluster_tiles(grid_gdf5k)
    assert len(gdf5k) == 1074
    assert gdf5k["tile_cluster"].nunique() == 1
