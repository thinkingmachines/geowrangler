import geopandas as gpd
import numpy as np
import pandas as pd
import polars as pl
import pytest
import shapely
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
    with pytest.warns(UserWarning):
        grids_gdf = grid_generator.generate_grid(sample_gdf)

    assert len(grids_gdf) == 0

def test_generate_grids_aoi_partially_inside_boundary(sample_gdf):
    grid_generator = grids.SquareGridGenerator(15000, boundary=(0.5, 0.5, 20, 20))
    with pytest.warns(UserWarning):
        grids_gdf = grid_generator.generate_grid(sample_gdf)

    assert len(grids_gdf) == 108
    assert grids_gdf.to_crs("EPSG:3857").area.apply(np.isclose, b=15000**2).all()

def test_generate_fast_grids(sample_gdf):
    grid_generator = grids.FastSquareGridGenerator(15000)
    grids_gdf = grid_generator.generate_grid(sample_gdf)
    assert len(grids_gdf) == 240
    # Check if area of each grid is what we expect
    assert grids_gdf.to_crs("EPSG:3857").area.apply(np.isclose, b=15000**2).all()

def test_generate_fast_grids_w_custom_boundary(sample_gdf):
    grid_generator = grids.FastSquareGridGenerator(15000, boundary=(0, 0, 10, 10))
    grids_gdf = grid_generator.generate_grid(
        sample_gdf,
    )

    assert len(grids_gdf) == 240
    # Check if area of each grid is what we expect
    assert grids_gdf.to_crs("EPSG:3857").area.apply(np.isclose, b=15000**2).all()


def test_generate_fast_grids_w_custom_boundary_2(sample_gdf):
    boundary = grids.SquareGridBoundary(
        0, 0, 5000000, 5000000
    )  # SquareGridBoundary used the target projection
    grid_generator = grids.FastSquareGridGenerator(15000, boundary=boundary)
    grids_gdf = grid_generator.generate_grid(sample_gdf)
    assert len(grids_gdf) == 240
    # Check if area of each grid is what we expect
    assert grids_gdf.to_crs("EPSG:3857").area.apply(np.isclose, b=15000**2).all()

def test_generate_fast_grids_aoi_outside_boundary(sample_gdf):
    grid_generator = grids.FastSquareGridGenerator(15000, boundary=(10, 10, 20, 20))
    with pytest.warns(UserWarning):
        grids_gdf = grid_generator.generate_grid(sample_gdf)

    assert len(grids_gdf) == 0

def test_generate_fast_grids_aoi_partially_inside_boundary(sample_gdf):
    grid_generator = grids.FastSquareGridGenerator(15000, boundary=(0.5, 0.5, 20, 20))
    with pytest.warns(UserWarning):
        grids_gdf = grid_generator.generate_grid(sample_gdf)

    assert len(grids_gdf) == 108
    assert grids_gdf.to_crs("EPSG:3857").area.apply(np.isclose, b=15000**2).all()

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

# FastBingTileGridGenerator returns 16 more tiles than BingTileGridGenerator because the sample polygons lie
# exactly on the tile borders at longitude 0 and latitude 0. Like shapely's `intersects`, FastBingTileGridGenerator
# includes the tiles that only touch the polygon at an edge or a corner.
FAST_BING_TILE_N_TILES = BING_TILE_N_TILES + 16
FAST_BING_TILE_MULTIPOLY_N_TILES = BING_TILE_MULTIPOLY_N_TILES + 16

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


def test_fast_bing_tile_grid_generator_non_4326_crs():
    """Test that FastBingTileGridGenerator correctly handles non-EPSG:4326 CRS.
    
    This tests the fix for issue #263 bug 2: Input in a projected CRS (like EPSG:32651)
    should be converted to EPSG:4326 internally and results converted back.
    """
    # Create polygon in EPSG:4326 first
    gdf_4326 = gpd.GeoDataFrame(
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
    
    # Convert to a projected CRS (Web Mercator)
    gdf_3857 = gdf_4326.to_crs("EPSG:3857")
    
    grid_generator = grids.FastBingTileGridGenerator(10)
    
    # Generate grids from the projected CRS input
    grids_gdf = grid_generator.generate_grid(gdf_3857)
    
    # Result should be in the original input CRS
    assert grids_gdf.crs.to_epsg() == 3857
    assert "geometry" in grids_gdf
    assert isinstance(grids_gdf, gpd.GeoDataFrame)
    # Should get approximately same number of tiles
    assert len(grids_gdf) == FAST_BING_TILE_N_TILES


def test_fast_bing_tile_grid_generator_polygon_with_holes():
    """Test that FastBingTileGridGenerator excludes tiles that are fully inside a hole"""
    exterior = [(0, 0), (4, 0), (4, 4), (0, 4), (0, 0)]
    hole = [(1, 1), (3, 1), (3, 3), (1, 3), (1, 1)]
    polygon_with_hole = Polygon(exterior, [hole])

    gdf = gpd.GeoDataFrame(
        geometry=[polygon_with_hole],
        crs="EPSG:4326",
    )

    grid_generator = grids.FastBingTileGridGenerator(10, add_xyz_cols=True)
    grids_gdf = grid_generator.generate_grid(gdf)

    assert "geometry" in grids_gdf
    assert isinstance(grids_gdf, gpd.GeoDataFrame)
    assert set(zip(grids_gdf.x, grids_gdf.y)) == brute_force_bing_tiles(
        grid_generator, polygon_with_hole
    )
    assert not shapely.contains_properly(Polygon(hole), grids_gdf.geometry.values).any()


def test_fast_bing_tile_grid_generator_no_crs_warning():
    """Test that FastBingTileGridGenerator warns when input has no CRS."""
    gdf_no_crs = gpd.GeoDataFrame(
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
        crs=None,
    )
    
    grid_generator = grids.FastBingTileGridGenerator(10)
    
    # Should emit a warning about missing CRS
    with pytest.warns(UserWarning, match="no CRS"):
        grids_gdf = grid_generator.generate_grid(gdf_no_crs)
    
    assert len(grids_gdf) > 0

def brute_force_square_cells(polygon, cell_size, boundary):
    """Cells (x, y) of the boundary's lattice where the closed cell intersects the polygon"""
    x_min, y_min, x_max, y_max = boundary
    n_x = int(np.ceil((x_max - x_min) / cell_size))
    n_y = int(np.ceil((y_max - y_min) / cell_size))
    xs, ys = np.meshgrid(np.arange(n_x), np.arange(n_y), indexing="ij")
    xs, ys = xs.ravel(), ys.ravel()
    cells = shapely.box(
        x_min + xs * cell_size,
        y_min + ys * cell_size,
        x_min + (xs + 1) * cell_size,
        y_min + (ys + 1) * cell_size,
    )
    intersects = shapely.intersects(cells, polygon)
    return set(zip(xs[intersects].tolist(), ys[intersects].tolist()))


def brute_force_bing_tiles(grid_generator, polygon):
    """Tiles (x, y) where the closed tile intersects the polygon in EPSG:4326"""
    minx, miny, maxx, maxy = polygon.bounds
    xs = np.arange(
        int(grid_generator._lng_to_xtile(minx)) - 2,
        int(grid_generator._lng_to_xtile(maxx)) + 3,
    )
    ys = np.arange(
        int(grid_generator._lat_to_ytile(maxy)) - 2,
        int(grid_generator._lat_to_ytile(miny)) + 3,
    )
    xs, ys = np.meshgrid(xs, ys, indexing="ij")
    xs, ys = xs.ravel(), ys.ravel()
    tiles = grid_generator._xy_to_bbox(pl.DataFrame({"x": xs, "y": ys}), "x", "y")
    intersects = tiles.intersects(polygon).values
    return set(zip(xs[intersects].tolist(), ys[intersects].tolist()))


def random_star_polygons(rng, n_polygons, center_min, center_max, max_radius):
    """Random star-shaped (generally concave) polygons"""
    polygons = []
    while len(polygons) < n_polygons:
        n_vertices = rng.integers(5, 20)
        center = rng.uniform(center_min, center_max, 2)
        angles = np.sort(rng.uniform(0, 2 * np.pi, n_vertices))
        radii = rng.uniform(max_radius / 8, max_radius, n_vertices)
        polygon = Polygon(
            np.c_[center[0] + radii * np.cos(angles), center[1] + radii * np.sin(angles)]
        )
        if polygon.is_valid:
            polygons.append(polygon)
    return polygons


def test_fast_square_grid_generator_random_concave_polygons():
    rng = np.random.default_rng(0)
    polygons = random_star_polygons(rng, 100, 150, 850, 150)
    gdf = gpd.GeoDataFrame(
        {"polygon_id": range(len(polygons))}, geometry=polygons, crs="EPSG:3857"
    )
    boundary = (0, 0, 1000, 1000)
    cell_size = 37

    grid_generator = grids.FastSquareGridGenerator(
        cell_size, boundary=grids.SquareGridBoundary(*boundary)
    )
    grids_gdf = grid_generator.generate_grid(gdf, unique_id_col="polygon_id")

    for polygon_id, polygon in enumerate(polygons):
        polygon_grids = grids_gdf[grids_gdf["polygon_id"] == polygon_id]
        assert set(zip(polygon_grids.x, polygon_grids.y)) == brute_force_square_cells(
            polygon, cell_size, boundary
        ), polygon_id

    # the geometries match the grid cells
    assert grids_gdf.area.apply(np.isclose, b=cell_size**2).all()
    matching_polygons = gdf.set_index("polygon_id").geometry.loc[grids_gdf["polygon_id"]]
    assert shapely.intersects(grids_gdf.geometry.values, matching_polygons.values).all()


def test_fast_square_grid_generator_matches_square_grid_generator():
    rng = np.random.default_rng(1)
    polygons = random_star_polygons(rng, 20, 0, 5, 2)
    gdf = gpd.GeoDataFrame(geometry=polygons, crs="EPSG:4326")

    fast_grids_gdf = grids.FastSquareGridGenerator(20000).generate_grid(gdf)
    grids_gdf = grids.SquareGridGenerator(20000).generate_grid(gdf)

    assert set(zip(fast_grids_gdf.x, fast_grids_gdf.y)) == set(
        zip(grids_gdf.x, grids_gdf.y)
    )


def test_fast_square_grid_generator_polygon_with_holes():
    exterior = [(0, 0), (1000, 0), (1000, 1000), (0, 1000)]
    holes = [
        [(300, 300), (700, 300), (700, 700), (300, 700)],
        [(810, 820), (930, 845), (880, 960)],
    ]
    polygon_with_holes = Polygon(exterior, holes)
    gdf = gpd.GeoDataFrame(geometry=[polygon_with_holes], crs="EPSG:3857")
    boundary = (0, 0, 1000, 1000)
    cell_size = 50

    grid_generator = grids.FastSquareGridGenerator(
        cell_size, boundary=grids.SquareGridBoundary(*boundary)
    )
    grids_gdf = grid_generator.generate_grid(gdf)

    assert set(zip(grids_gdf.x, grids_gdf.y)) == brute_force_square_cells(
        polygon_with_holes, cell_size, boundary
    )
    # cells fully inside the hole are excluded
    assert not shapely.contains_properly(Polygon(holes[0]), grids_gdf.geometry.values).any()


def test_fast_square_grid_generator_polygon_partially_outside_boundary():
    polygon = Polygon([(-120, 130), (420, -80), (510, 260), (180, 140), (90, 470)])
    gdf = gpd.GeoDataFrame(geometry=[polygon], crs="EPSG:3857")
    boundary = (0, 0, 300, 300)
    cell_size = 23

    grid_generator = grids.FastSquareGridGenerator(
        cell_size, boundary=grids.SquareGridBoundary(*boundary)
    )
    with pytest.warns(UserWarning):
        grids_gdf = grid_generator.generate_grid(gdf)

    assert set(zip(grids_gdf.x, grids_gdf.y)) == brute_force_square_cells(
        polygon, cell_size, boundary
    )


def test_fast_bing_tile_grid_generator_random_concave_polygons():
    rng = np.random.default_rng(0)
    polygons = random_star_polygons(rng, 50, -60, 60, 2)
    gdf = gpd.GeoDataFrame(
        {"polygon_id": range(len(polygons))}, geometry=polygons, crs="EPSG:4326"
    )

    grid_generator = grids.FastBingTileGridGenerator(9, add_xyz_cols=True)
    grids_gdf = grid_generator.generate_grid(gdf, unique_id_col="polygon_id")

    for polygon_id, polygon in enumerate(polygons):
        polygon_grids = grids_gdf[grids_gdf["polygon_id"] == polygon_id]
        assert set(zip(polygon_grids.x, polygon_grids.y)) == brute_force_bing_tiles(
            grid_generator, polygon
        ), polygon_id


@pytest.mark.parametrize(
    "geometry", [[], [Polygon()]], ids=["no_rows", "empty_polygon"]
)
def test_fast_square_grid_generator_empty_aoi(geometry):
    gdf = gpd.GeoDataFrame({"polygon_id": range(len(geometry))}, geometry=geometry, crs="EPSG:4326")
    grid_generator = grids.FastSquareGridGenerator(15000)
    with pytest.warns(UserWarning):
        grids_gdf = grid_generator.generate_grid(gdf, unique_id_col="polygon_id")
    assert len(grids_gdf) == 0
    assert list(grids_gdf.columns) == ["x", "y", "polygon_id", "geometry"]
