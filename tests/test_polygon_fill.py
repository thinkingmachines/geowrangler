import pandas as pd
import geopandas as gpd
import pytest
from shapely.geometry import Polygon, MultiPolygon
from geowrangler.gridding_utils import polygon_fill

@pytest.fixture
def sample_polygons():
    polygon_test_cases = {
        "Square": {"vertices":[(0, 0), (10, 0), (10, 10), (0, 10)], "n_pixels":121},
        "Triangle": {"vertices":[(0, 0), (10, 0), (5, 10)], "n_pixels":71},
        "Right Triangle": {"vertices":[(0, 0), (10, 0), (0, 10)], "n_pixels":66},
        "Pentagon": {"vertices":[(2, 0), (8, 0), (10, 6), (5, 10), (0, 6)], "n_pixels":87},
        "Star": {"vertices":[
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
        ], "n_pixels":109},
        "Complex Shape 1": {"vertices":[(0, 0), (5, 2), (3, 5), (8, 8), (5, 10), (0, 7)], "n_pixels":59},
        "Complex Shape 2": {"vertices":[
            (0, 0),
            (2, 6),
            (4, 10),
            (6, 8),
            (8, 12),
            (10, 4),
            (12, 2),
            (8, 0),
        ], "n_pixels":102},
        "Complex Shape 3": {"vertices":[(2, 3), (5, 3), (6, 6), (3, 7), (1, 5)], "n_pixels":22},
        "Complex Shape 4": {"vertices":[(1, 1), (2, 5), (4, 3), (6, 7)], "n_pixels":17},
        "Complex Shape 5": {"vertices":[(1, 2), (3, 6), (5, 5), (7, 4), (9, 5), (11, 2)], "n_pixels":40}
    }

    yield polygon_test_cases

@pytest.fixture
def sample_gdf():
    multipolygon_dict = {
        "Square": {"vertices":Polygon([(15, 0), (25, 0), (25, 10), (15, 10)]), "n_pixels":121},
        "Triangle MultiPolygon": {"vertices":MultiPolygon(polygons = [
            Polygon([(0, 0), (10, 0), (5, 10)]), 
            Polygon([(0, 12), (10, 12), (0, 22)])],
        ), "n_pixels":137},
        "Pentagon": {"vertices":Polygon([(17, 15), (23, 15), (25, 21), (20, 25), (15, 21)]), "n_pixels":87}
    }

    multipolygon_gdf = pd.DataFrame.from_dict(multipolygon_dict, orient = "index")
    multipolygon_gdf.index.name = "geom_name"
    multipolygon_gdf = multipolygon_gdf.reset_index()
    geometry = gpd.GeoSeries(multipolygon_gdf["vertices"])
    multipolygon_gdf = gpd.GeoDataFrame(multipolygon_gdf.drop(columns="vertices"),geometry=geometry)
    yield multipolygon_gdf

def test_fill_individual_polygons(sample_polygons):
    for polygon_name, polygon_data in sample_polygons.items():
        vertices = polygon_data["vertices"]
        n_pixels = polygon_data["n_pixels"]
        vertices_df = pd.DataFrame(vertices, columns=["x", "y"])

        filled_pixels = polygon_fill.voxel_traversal_scanline_fill(vertices_df)
        assert n_pixels == len(filled_pixels), f"{polygon_name} has {len(filled_pixels)} pixels, but expected {n_pixels}"

def test_fill_gdf(sample_gdf):
    vertices_df = polygon_fill.polygons_to_vertices(sample_gdf, "geom_name")
    vertices_df = vertices_df.cast({"x":polygon_fill.PIXEL_DTYPE, "y":polygon_fill.PIXEL_DTYPE})
    filled_polygons = polygon_fill.fast_polygon_fill(vertices_df, "geom_name")

    n_pixels_per_geom = (
        filled_polygons
        .group_by("geom_name")
        .len("computed_n_pixels")
        .to_pandas()
    )
    
    n_pixels_per_geom = pd.merge(
        n_pixels_per_geom, 
        sample_gdf, 
        how = "outer", 
        on = "geom_name", 
        validate = "1:1"
    )
    
    assert (n_pixels_per_geom["computed_n_pixels"] == n_pixels_per_geom["n_pixels"]).all()

