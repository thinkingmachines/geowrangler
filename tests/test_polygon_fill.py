import numpy as np
import pandas as pd
import geopandas as gpd
import polars as pl
import pytest
import shapely
from shapely.geometry import LineString, Point, Polygon, MultiPolygon
from geowrangler.gridding_utils import polygon_fill


def brute_force_pixels(geom, pixel_bounds=None):
    """Pixels (x, y) where the closed square [x, x+1] x [y, y+1] intersects geom"""
    if pixel_bounds is None:
        minx, miny, maxx, maxy = geom.bounds
        pixel_bounds = (
            int(np.floor(minx)) - 2,
            int(np.floor(miny)) - 2,
            int(np.floor(maxx)) + 2,
            int(np.floor(maxy)) + 2,
        )
    min_x, min_y, max_x, max_y = pixel_bounds
    xs, ys = np.meshgrid(
        np.arange(min_x, max_x + 1), np.arange(min_y, max_y + 1), indexing="ij"
    )
    xs, ys = xs.ravel(), ys.ravel()
    intersects = shapely.intersects(shapely.box(xs, ys, xs + 1, ys + 1), geom)
    return set(zip(xs[intersects].tolist(), ys[intersects].tolist()))


def random_star_polygon(rng, center_range=5, max_radius=8, round_vertices=False):
    """Random star-shaped (generally concave) polygon"""
    n_vertices = rng.integers(3, 25)
    center = rng.uniform(-center_range, center_range, 2)
    angles = np.sort(rng.uniform(0, 2 * np.pi, n_vertices))
    radii = rng.uniform(0.2, max_radius, n_vertices)
    vertices = np.c_[
        center[0] + radii * np.cos(angles), center[1] + radii * np.sin(angles)
    ]
    if round_vertices:
        # vertices on pixel corners exercise the exact edge and corner touching cases
        vertices = np.round(vertices)
    return Polygon(vertices)


@pytest.fixture
def sample_polygons():
    polygon_test_cases = {
        "Square": [(0, 0), (10, 0), (10, 10), (0, 10)],
        "Triangle": [(0, 0), (10, 0), (5, 10)],
        "Right Triangle": [(0, 0), (10, 0), (0, 10)],
        "Pentagon": [(2, 0), (8, 0), (10, 6), (5, 10), (0, 6)],
        "Star": [
            (6, 2),
            (8, 8),
            (12, 8),
            (9, 12),
            (11, 18),
            (6, 14),
            (1, 18),
            (3, 12),
            (0, 8),
            (4, 8),
        ],
        "Complex Shape 1": [(0, 0), (5, 2), (3, 5), (8, 8), (5, 10), (0, 7)],
        "Complex Shape 2": [
            (0, 0),
            (2, 6),
            (4, 10),
            (6, 8),
            (8, 12),
            (10, 4),
            (12, 2),
            (8, 0),
        ],
        "Complex Shape 3": [(2, 3), (5, 3), (6, 6), (3, 7), (1, 5)],
        "Complex Shape 4": [(1, 1), (2, 5), (4, 3), (6, 7)],
        "Complex Shape 5": [(1, 2), (3, 6), (5, 5), (7, 4), (9, 5), (11, 2)],
        "Fractional Concave": [(0.3, 0.2), (7.9, 1.1), (4.5, 6.6), (2.2, 3.3)],
    }

    yield polygon_test_cases


@pytest.fixture
def sample_gdf():
    multipolygon_dict = {
        "Square": Polygon([(15, 0), (25, 0), (25, 10), (15, 10)]),
        "Triangle MultiPolygon": MultiPolygon(
            polygons=[
                Polygon([(0, 0), (10, 0), (5, 10)]),
                Polygon([(0, 12), (10, 12), (0, 22)]),
            ],
        ),
        "Pentagon": Polygon([(17, 15), (23, 15), (25, 21), (20, 25), (15, 21)]),
        "Square with Holes": Polygon(
            [(30, 0), (50, 0), (50, 20), (30, 20)],
            [
                [(34, 4), (42, 4), (42, 12), (34, 12)],
                [(44.5, 13.2), (48.1, 13.7), (46.3, 18.6)],
            ],
        ),
    }

    multipolygon_gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries(multipolygon_dict))
    multipolygon_gdf.index.name = "geom_name"
    multipolygon_gdf = multipolygon_gdf.reset_index()
    yield multipolygon_gdf


def test_fill_individual_polygons(sample_polygons):
    for polygon_name, vertices in sample_polygons.items():
        vertices_df = pd.DataFrame(vertices, columns=["x", "y"])
        filled_pixels = polygon_fill.voxel_traversal_scanline_fill(vertices_df)
        expected_pixels = brute_force_pixels(Polygon(vertices))
        assert (
            filled_pixels == expected_pixels
        ), f"{polygon_name} has {len(filled_pixels - expected_pixels)} extra and {len(expected_pixels - filled_pixels)} missing pixels"


@pytest.mark.parametrize("round_vertices", [False, True])
def test_fill_random_concave_polygons(round_vertices):
    rng = np.random.default_rng(0)
    n_tested = 0
    while n_tested < 200:
        polygon = random_star_polygon(rng, round_vertices=round_vertices)
        if not polygon.is_valid or polygon.area == 0:
            continue
        n_tested += 1
        x, y = np.array(polygon.exterior.coords).T
        filled_pixels = polygon_fill.voxel_traversal_scanline_fill(
            pl.DataFrame({"x": x, "y": y})
        )
        assert filled_pixels == brute_force_pixels(polygon), polygon.wkt


def test_fill_polygon_with_hole():
    polygon = Polygon(
        [(0, 0), (20, 0), (20, 20), (0, 20)],
        [[(6.5, 6.5), (14.5, 6.5), (14.5, 14.5), (6.5, 14.5)]],
    )
    vertices_df = pd.DataFrame(
        [(x, y, 0) for x, y in polygon.exterior.coords]
        + [(x, y, 1) for x, y in polygon.interiors[0].coords],
        columns=["x", "y", "ring"],
    )
    filled_pixels = polygon_fill.voxel_traversal_scanline_fill(
        vertices_df, ring_col="ring"
    )
    assert filled_pixels == brute_force_pixels(polygon)
    # pixels fully inside the hole are excluded
    assert not {(x, y) for x in range(7, 14) for y in range(7, 14)} & filled_pixels


def test_voxel_traversal_2d():
    rng = np.random.default_rng(0)
    segments = [((0, 0), (5, 5)), ((0, 0), (5, 0)), ((2, 1), (2, 7)), ((1, 1), (1, 1))]
    segments += [tuple(map(tuple, rng.uniform(-10, 10, (2, 2)))) for _ in range(100)]
    segments += [tuple(map(tuple, rng.integers(-10, 10, (2, 2)))) for _ in range(100)]
    for start_vertex, end_vertex in segments:
        line = LineString([start_vertex, end_vertex])
        if line.length == 0:
            line = Point(start_vertex)
        pixels = polygon_fill.voxel_traversal_2d(start_vertex, end_vertex)
        assert pixels == brute_force_pixels(line), (start_vertex, end_vertex)


def test_scanline_fill():
    rng = np.random.default_rng(0)
    for _ in range(100):
        polygon = random_star_polygon(rng)
        if not polygon.is_valid:
            continue
        pixels = polygon_fill.scanline_fill(list(polygon.exterior.coords)[:-1])
        candidates = brute_force_pixels(polygon)
        expected = {
            (x, y) for x, y in candidates if polygon.contains(Point(x + 0.5, y + 0.5))
        }
        assert pixels == expected


def test_polygons_to_vertices_separates_rings(sample_gdf):
    vertices_df = polygon_fill.polygons_to_vertices(sample_gdf, "geom_name")
    n_rings = (
        vertices_df.filter(pl.col("geom_name") == "Square with Holes")[
            polygon_fill.RING_ID_COL
        ]
        .unique()
        .len()
    )
    assert n_rings == 3
    n_subpolygons = (
        vertices_df.filter(pl.col("geom_name") == "Triangle MultiPolygon")[
            polygon_fill.SUBPOLYGON_ID_COL
        ]
        .unique()
        .len()
    )
    assert n_subpolygons == 2


def test_fill_gdf(sample_gdf):
    vertices_df = polygon_fill.polygons_to_vertices(sample_gdf, "geom_name")
    filled_polygons = polygon_fill.fast_polygon_fill(vertices_df, "geom_name")
    assert filled_polygons.columns == ["x", "y", "geom_name"]

    for geom_name, geom in zip(sample_gdf["geom_name"], sample_gdf.geometry):
        pixels = set(
            filled_polygons.filter(pl.col("geom_name") == geom_name)
            .select("x", "y")
            .iter_rows()
        )
        assert pixels == brute_force_pixels(geom), geom_name


def test_fill_gdf_without_unique_id_col(sample_gdf):
    vertices_df = polygon_fill.polygons_to_vertices(sample_gdf)
    filled_polygons = polygon_fill.fast_polygon_fill(vertices_df)
    assert filled_polygons.columns == ["x", "y"]

    pixels = set(filled_polygons.iter_rows())
    expected_pixels = set().union(*[brute_force_pixels(geom) for geom in sample_gdf.geometry])
    assert pixels == expected_pixels


def test_fill_overlapping_polygons_without_unique_id_col():
    # overlapping polygons from different rows shouldn't cancel out in the even-odd fill
    gdf = gpd.GeoDataFrame(
        geometry=[
            Polygon([(0, 0), (10, 0), (10, 10), (0, 10)]),
            Polygon([(2.5, 2.5), (7.5, 2.5), (7.5, 7.5), (2.5, 7.5)]),
        ]
    )
    vertices_df = polygon_fill.polygons_to_vertices(gdf)
    pixels = set(polygon_fill.fast_polygon_fill(vertices_df).iter_rows())
    assert pixels == brute_force_pixels(gdf.geometry[0])


def test_fill_gdf_pixel_bounds(sample_gdf):
    pixel_bounds = (3, 2, 33, 14)
    vertices_df = polygon_fill.polygons_to_vertices(sample_gdf, "geom_name")
    filled_polygons = polygon_fill.fast_polygon_fill(
        vertices_df, "geom_name", pixel_bounds=pixel_bounds
    )
    for geom_name, geom in zip(sample_gdf["geom_name"], sample_gdf.geometry):
        pixels = set(
            filled_polygons.filter(pl.col("geom_name") == geom_name)
            .select("x", "y")
            .iter_rows()
        )
        assert pixels == brute_force_pixels(geom, pixel_bounds), geom_name


def test_fill_gdf_extra_vertex_column(sample_gdf):
    vertices_df = polygon_fill.polygons_to_vertices(sample_gdf, "geom_name").with_row_index("vertex_order")
    filled_polygons = polygon_fill.fast_polygon_fill(vertices_df, "geom_name")
    square_pixels = set(
        filled_polygons.filter(pl.col("geom_name") == "Square").select("x", "y").iter_rows()
    )
    assert square_pixels == brute_force_pixels(sample_gdf.geometry[0])

    # without unique_id_col, the id column is ambiguous
    with pytest.raises(ValueError, match="at most 1 id column"):
        polygon_fill.fast_polygon_fill(vertices_df)


def test_fill_nan_vertices():
    vertices_df = pd.DataFrame({"x": [0, np.nan, 10, 10, 0], "y": [0, 5, 0, 10, 10]})
    expected_pixels = brute_force_pixels(Polygon([(0, 0), (10, 0), (10, 10), (0, 10)]))
    assert polygon_fill.voxel_traversal_scanline_fill(vertices_df) == expected_pixels

    all_nan_df = pd.DataFrame({"x": [np.nan] * 3, "y": [np.nan] * 3})
    assert polygon_fill.voxel_traversal_scanline_fill(all_nan_df) == set()


def test_fill_empty_vertices():
    gdf = gpd.GeoDataFrame({"geom_name": []}, geometry=[])
    vertices_df = polygon_fill.polygons_to_vertices(gdf, "geom_name")
    assert len(polygon_fill.fast_polygon_fill(vertices_df, "geom_name")) == 0


def test_fill_shared_and_null_ids():
    gdf = gpd.GeoDataFrame(
        {"geom_name": [None, "b"]},
        geometry=[
            Polygon([(0, 0), (2, 0), (2, 2), (0, 2)]),
            MultiPolygon(
                [
                    Polygon([(5, 5), (7, 5), (7, 7), (5, 7)]),
                    Polygon([(6, 6), (9, 6), (9, 9), (6, 9)]),
                ]
            ),
        ],
    )
    vertices_df = polygon_fill.polygons_to_vertices(gdf, "geom_name")
    filled_polygons = polygon_fill.fast_polygon_fill(vertices_df, "geom_name")
    # pixels shared by the subpolygons of the same geometry aren't duplicated
    assert not filled_polygons.is_duplicated().any()
    for geom_name, geom in zip(gdf["geom_name"], gdf.geometry):
        pixels = set(
            filled_polygons.filter(
                pl.col("geom_name").is_null() if pd.isna(geom_name) else pl.col("geom_name") == geom_name
            )
            .select("x", "y")
            .iter_rows()
        )
        assert pixels == brute_force_pixels(geom), geom_name


def test_scanline_unclosed_ring_raises():
    # a single edge that isn't part of a closed ring crosses the pixel rows an odd number of times
    with pytest.raises(ValueError, match="odd number of edge crossings"):
        polygon_fill._scanline_pixels(
            np.array([0.0]), np.array([0.0]), np.array([5.0]), np.array([5.0]),
            group=np.zeros(1, dtype=np.int64), pixel_bounds=(0, 0, 10, 10),
        )
