# AUTOGENERATED! DO NOT EDIT! File to edit: ../notebooks/00_grids.ipynb.

# %% auto 0
__all__ = ['SquareGridGenerator', 'FastSquareGridGenerator', 'H3GridGenerator', 'BingTileGridGenerator',
           'FastBingTileGridGenerator']

# %% ../notebooks/00_grids.ipynb 5
import logging
from functools import reduce
from typing import List, Tuple, Union, Optional, Iterable

import h3
import morecantile
import numpy as np
import pandas as pd
import polars as pl
import warnings
from fastcore.all import defaults, parallel
from fastcore.basics import patch
from geopandas import GeoDataFrame, GeoSeries
from pandas import DataFrame
from pyproj import Transformer
from shapely import box
from shapely.geometry import Polygon, shape
from shapely.prepared import prep

from geowrangler.gridding_utils import polygon_fill

logger = logging.getLogger(__name__)

# %% ../notebooks/00_grids.ipynb 7
class SquareGridBoundary:
    """Reusing Boundary. x_min, y_min, x_max, and y_max are in the the target crs"""

    BOUNDARY_TYPES = ["aoi_boundary", "custom_boundary"]

    def __init__(
        self,
        x_min: float,
        y_min: float,
        x_max: float,
        y_max: float,
        boundary_type: Optional[str] = None,
    ):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        if boundary_type is not None:
            if boundary_type not in self.BOUNDARY_TYPES:
                raise ValueError(
                    f"{boundary_type} boundary_type is not supported. Please select from these options {self.BOUNDARY_TYPES}"
                )
        self.boundary_type = boundary_type

    def get_range_subset(
        self, x_min: float, y_min: float, x_max: float, y_max: float, cell_size: float
    ) -> Tuple[float, List[float], float, List[float]]:
        """Returns a subset of grids from the orginal boundary based on the boundary and a grid size"""
        xrange = np.arange(self.x_min, self.x_max, cell_size)
        yrange = np.arange(self.y_min, self.y_max, cell_size)
        # Add cell_size buffer to catch cases where the bounds of the polygon are slightly outside
        # the bounds. This might happen to do floating point after reprojection/unary_union
        x_mask = (xrange >= (x_min - cell_size)) & (xrange <= (x_max + cell_size))
        y_mask = (yrange >= (y_min - cell_size)) & (yrange <= (y_max + cell_size))
        x_idx = np.flatnonzero(x_mask)
        x_idx_offset = None if len(x_idx) == 0 else x_idx[0]
        y_idx = np.flatnonzero(y_mask)
        y_idx_offset = None if len(y_idx) == 0 else y_idx[0]
        return (
            x_idx_offset,
            xrange[x_mask],
            y_idx_offset,
            yrange[y_mask],
        )

# %% ../notebooks/00_grids.ipynb 8
class SquareGridGenerator:
    def __init__(
        self,
        cell_size: float,  # height and width of a square cell in meters
        grid_projection: str = "EPSG:3857",  # projection of grid output
        boundary: Union[
            SquareGridBoundary, List[float], Tuple[float]
        ] = None,  # original boundary
    ):
        self.cell_size = cell_size
        self.grid_projection = grid_projection
        self.boundary = boundary

# %% ../notebooks/00_grids.ipynb 9
@patch
def create_cell(
    self: SquareGridGenerator,
    x: float,  # x coord of bottom left
    y: float,  # y coord of bottom left
) -> Polygon:
    """Create a square cell based on the bottom left coordinates and cell_size"""
    return Polygon(
        [
            (x, y),
            (x + self.cell_size, y),
            (x + self.cell_size, y + self.cell_size),
            (x, y + self.cell_size),
        ]
    )

# %% ../notebooks/00_grids.ipynb 10
@patch
def create_grid_for_polygon(self: SquareGridGenerator, boundary, geometry):
    x_idx_offset, xrange, y_idx_offset, yrange = boundary.get_range_subset(
        *geometry.bounds, cell_size=self.cell_size
    )
    cells = {}
    prepared_geometry = prep(geometry)
    for x_idx, x in enumerate(xrange):
        for y_idx, y in enumerate(yrange):
            x_col = x_idx + x_idx_offset
            y_col = y_idx + y_idx_offset
            cell = self.create_cell(x, y)
            if prepared_geometry.intersects(cell):
                cells.update(
                    {(x_col, y_col): {"x": x_col, "y": y_col, "geometry": cell}}
                )
    return cells

# %% ../notebooks/00_grids.ipynb 11
@patch
def generate_grid(self: SquareGridGenerator, aoi_gdf: GeoDataFrame) -> GeoDataFrame:
    reprojected_gdf = aoi_gdf.to_crs(self.grid_projection)
    boundary = setup_boundary(self.boundary, aoi_gdf, reprojected_gdf)

    polygons = {}
    unary_union = reprojected_gdf.union_all(method="unary")
    if isinstance(unary_union, Polygon):
        polygons.update(self.create_grid_for_polygon(boundary, unary_union))
    else:
        for geom in unary_union.geoms:
            polygons.update(self.create_grid_for_polygon(boundary, geom))
    if polygons:
        dest = GeoDataFrame(
            list(polygons.values()), geometry="geometry", crs=self.grid_projection
        )
        dest = dest.to_crs(aoi_gdf.crs)
        return dest
    else:
        return GeoDataFrame(
            {"x": [], "y": [], "geometry": []}, geometry="geometry", crs=aoi_gdf.crs
        )

# %% ../notebooks/00_grids.ipynb 12
def setup_boundary(
    boundary: Optional[Union[SquareGridGenerator, Iterable[float]]],
    aoi_gdf: GeoDataFrame,
    reprojected_gdf: GeoDataFrame,
) -> SquareGridBoundary:

    if boundary is None:
        boundary = SquareGridBoundary(
            *reprojected_gdf.total_bounds, boundary_type="aoi_boundary"
        )
    elif isinstance(boundary, SquareGridBoundary):
        boundary = boundary
    else:
        transformer = Transformer.from_crs(
            aoi_gdf.crs, reprojected_gdf.crs, always_xy=True
        )
        x_min, y_min = transformer.transform(boundary[0], boundary[1])
        x_max, y_max = transformer.transform(boundary[2], boundary[3])
        boundary = SquareGridBoundary(
            x_min, y_min, x_max, y_max, boundary_type="custom_boundary"
        )

    if not is_aoi_within_boundary(boundary, reprojected_gdf):
        warnings.warn(
            "The given boundary does not fully enclose the reprojected AOI. There might be missing grid cells due to this. If this is not expected, get the boundary of the reprojected AOI, and/or add a buffer to the boundary. See geowrangler.thinkingmachin.es/tutorial.grids.html#reprojecting-before-gridding for more info."
        )

    return boundary


def is_aoi_within_boundary(
    boundary: Optional[Union[SquareGridGenerator, Iterable[float]]],
    gdf: GeoDataFrame,
) -> bool:

    gdf_minx, gdf_miny, gdf_maxx, gdf_maxy = gdf.total_bounds
    is_x_within_bounds = (gdf_minx >= boundary.x_min) & (gdf_maxx <= boundary.x_max)
    is_y_within_bounds = (gdf_miny >= boundary.y_min) & (gdf_maxy <= boundary.y_max)

    is_within_bounds = is_x_within_bounds & is_y_within_bounds
    return is_within_bounds

# %% ../notebooks/00_grids.ipynb 14
class FastSquareGridGenerator:
    PIXEL_DTYPE = polygon_fill.PIXEL_DTYPE
    SUBPOLYGON_ID_COL = polygon_fill.SUBPOLYGON_ID_COL

    def __init__(
        self,
        cell_size: float,  # height and width of a square cell in meters
        grid_projection: str = "EPSG:3857",  # planar projection of grid
        boundary: Union[
            SquareGridBoundary, Iterable[float]
        ] = None,  # original boundary
    ):
        self.cell_size = cell_size
        self.grid_projection = grid_projection
        self.boundary = boundary

        if self.cell_size <= 0:
            raise ValueError(f"cell_size should be positive but instead is {cell_size}")

# %% ../notebooks/00_grids.ipynb 15
@patch
def generate_grid(
    self: FastSquareGridGenerator,
    aoi_gdf: GeoDataFrame,
    unique_id_col: Optional[
        str
    ] = None,  # the ids under this column will be preserved in the output tiles
) -> Union[GeoDataFrame, pd.DataFrame]:

    reprojected_gdf = aoi_gdf.to_crs(self.grid_projection)
    boundary = setup_boundary(self.boundary, aoi_gdf, reprojected_gdf)

    vertices = polygon_fill.polygons_to_vertices(reprojected_gdf, unique_id_col)
    if boundary.boundary_type != "aoi_boundary":
        vertices = self._remove_out_of_bounds_polygons(vertices, boundary)
    vertices = self._northingeasting_to_xy(
        vertices, boundary, northing_col="y", easting_col="x"
    )

    polygon_fill_result = polygon_fill.fast_polygon_fill(vertices, unique_id_col)
    tiles_in_geom = polygon_fill_result["tiles_in_geom"]
    bboxes = self._xy_to_bbox(tiles_in_geom, boundary, "x", "y")

    # this is error correction on the polygon boundary (not the square boundary)
    tiles_off_boundary = polygon_fill_result["tiles_off_boundary"]
    if not tiles_off_boundary.is_empty():
        off_boundary_bboxes = self._xy_to_bbox(tiles_off_boundary, boundary, "x", "y")
        all_polygon_boundary = reprojected_gdf.boundary.union_all(method="unary")
        intersects_boundary_bool = off_boundary_bboxes.intersects(all_polygon_boundary)

        addtl_tiles_in_geom = tiles_off_boundary.filter(
            pl.Series(intersects_boundary_bool)
        )
        addtl_boundary_bboxes = off_boundary_bboxes[intersects_boundary_bool].copy()

        tiles_in_geom = pl.concat([tiles_in_geom, addtl_tiles_in_geom])
        bboxes = pd.concat([bboxes, addtl_boundary_bboxes], ignore_index=True)

    column_order = ["x", "y"]
    if unique_id_col is not None:
        column_order += [unique_id_col]
    assert set(tiles_in_geom.columns) == set(column_order)
    tiles_in_geom = tiles_in_geom.select(column_order)

    tiles_in_geom = GeoDataFrame(tiles_in_geom.to_pandas(), geometry=bboxes)
    if tiles_in_geom.crs != aoi_gdf.crs:
        tiles_in_geom = tiles_in_geom.to_crs(aoi_gdf.crs)

    return tiles_in_geom

# %% ../notebooks/00_grids.ipynb 16
@patch
def _remove_out_of_bounds_polygons(
    self: FastSquareGridGenerator,
    vertices: pl.DataFrame,
    boundary: SquareGridBoundary,
) -> pl.DataFrame:
    id_cols = [col for col in vertices.columns if col != "x" and col != "y"]

    x_out_of_bounds_expr = (pl.col("maxx") < pl.lit(boundary.x_min)) | (
        pl.lit(boundary.x_max) < pl.col("minx")
    )
    y_out_of_bounds_expr = (pl.col("maxy") < pl.lit(boundary.y_min)) | (
        pl.lit(boundary.y_max) < pl.col("miny")
    )

    out_of_bounds_expr = x_out_of_bounds_expr | y_out_of_bounds_expr

    out_of_bounds_polygons = (
        vertices.group_by(id_cols)
        .agg(
            minx=pl.col("x").min(),
            miny=pl.col("y").min(),
            maxx=pl.col("x").max(),
            maxy=pl.col("y").max(),
        )
        .filter(out_of_bounds_expr)
        .select(id_cols)
    )

    # keep only vertices from polygons that are not out of bounds
    vertices = vertices.join(out_of_bounds_polygons, on=id_cols, how="anti")
    return vertices


@patch
def _northing_to_ytile(
    self: FastSquareGridGenerator,
    northing: pl.Expr,
    y_min: float,
    y_max: float,
) -> pl.Expr:

    # clamping to bounds
    northing = (
        pl.when(northing < y_min)
        .then(pl.lit(y_min))
        .when(northing > y_max)
        .then(pl.lit(y_max))
        .otherwise(northing)
    )
    ytile = ((northing - y_min) / self.cell_size).floor()
    ytile = ytile.cast(self.PIXEL_DTYPE)

    return ytile


@patch
def _easting_to_xtile(
    self: FastSquareGridGenerator,
    easting: pl.Expr,
    x_min: float,
    x_max: float,
) -> pl.Expr:

    # clamping to bounds
    easting = (
        pl.when(easting < x_min)
        .then(pl.lit(x_min))
        .when(easting > x_max)
        .then(pl.lit(x_max))
        .otherwise(easting)
    )

    xtile = ((easting - x_min) / self.cell_size).floor()
    xtile = xtile.cast(self.PIXEL_DTYPE)

    return xtile


@patch
def _northingeasting_to_xy(
    self: FastSquareGridGenerator,
    df: pl.DataFrame,
    boundary: SquareGridBoundary,
    northing_col: str,
    easting_col: str,
) -> pl.DataFrame:

    x_min = boundary.x_min
    y_min = boundary.y_min
    x_max = boundary.x_max
    y_max = boundary.y_max

    xy_df = df.with_columns(
        x=self._easting_to_xtile(pl.col(easting_col), x_min, x_max),
        y=self._northing_to_ytile(pl.col(northing_col), y_min, y_max),
    )

    return xy_df


@patch
def _xtile_to_easting(
    self: FastSquareGridGenerator,
    xtile: pl.Expr,
    x_min: float,
) -> pl.Expr:
    """This gets the easting of the lower left corner of the tile"""

    easting = (xtile * self.cell_size) + x_min

    return easting


@patch
def _ytile_to_northing(
    self: FastSquareGridGenerator,
    ytile: pl.Expr,
    y_min: float,
) -> pl.Expr:
    """This gets the northing of the lower left corner of the tile"""

    northing = (ytile * self.cell_size) + y_min

    return northing


@patch
def _xy_to_bbox(
    self: FastSquareGridGenerator,
    df: pl.DataFrame,
    boundary: SquareGridBoundary,
    xtile_col: str,
    ytile_col: str,
) -> GeoSeries:

    x_min = boundary.x_min
    y_min = boundary.y_min

    lower_left_easting = self._xtile_to_easting(pl.col(xtile_col), x_min)
    lower_left_northing = self._ytile_to_northing(pl.col(ytile_col), y_min)
    upper_right_easting = self._xtile_to_easting(pl.col(xtile_col) + 1, x_min)
    upper_right_northing = self._ytile_to_northing(pl.col(ytile_col) + 1, y_min)

    bbox_df = df.select(
        minx=lower_left_easting,
        miny=lower_left_northing,
        maxx=upper_right_easting,
        maxy=upper_right_northing,
    )

    # use vectorized version in shapely 2.0
    bboxes = box(
        bbox_df["minx"].to_list(),
        bbox_df["miny"].to_list(),
        bbox_df["maxx"].to_list(),
        bbox_df["maxy"].to_list(),
    )
    bboxes = GeoSeries(bboxes, crs=self.grid_projection)

    return bboxes

# %% ../notebooks/00_grids.ipynb 18
class H3GridGenerator:
    def __init__(
        self,
        resolution: int,  # Resolution of hexagon. See: https://h3geo.org/docs/core-library/restable/ for more info
        return_geometry: bool = True,  # If geometry should be returned. Setting this to false will only return hex_ids
    ):
        self.resolution = resolution
        self.return_geometry = return_geometry

# %% ../notebooks/00_grids.ipynb 19
@patch
def get_hexes_for_polygon(self: H3GridGenerator, poly: Polygon):
    if h3.__version__[0] == "3":
        return h3.polyfill(
            poly.__geo_interface__,
            self.resolution,
            geo_json_conformant=True,
        )
    else:
        return h3.polygon_to_cells(
            h3.geo_to_h3shape(poly.__geo_interface__),
            self.resolution,
        )

# %% ../notebooks/00_grids.ipynb 20
@patch
def generate_grid(self: H3GridGenerator, aoi_gdf: GeoDataFrame) -> DataFrame:
    reprojected_gdf = aoi_gdf.to_crs("epsg:4326")  # h3 hexes are in epsg:4326 CRS
    hex_ids = set()
    unary_union = reprojected_gdf.union_all(method="unary")
    if isinstance(unary_union, Polygon):
        hex_ids.update(self.get_hexes_for_polygon(unary_union))
    else:
        for geom in unary_union.geoms:
            _hexes = self.get_hexes_for_polygon(geom)
            hex_ids.update(_hexes)
    df = DataFrame({"hex_id": list(hex_ids)})
    if self.return_geometry is False:
        return df
    if h3.__version__[0] == "3":
        hexes = df.hex_id.apply(
            lambda id: Polygon(h3.h3_to_geo_boundary(id, geojson=True))
        )
    else:
        hexes = df.hex_id.apply(lambda id: Polygon(h3.cell_to_boundary(id)))
    h3_gdf = GeoDataFrame(
        df,
        geometry=hexes,
        crs="epsg:4326",
    )
    return h3_gdf.to_crs(aoi_gdf.crs)

# %% ../notebooks/00_grids.ipynb 22
class BingTileGridGenerator:
    def __init__(
        self,
        zoom_level: int,  # Zoom level of tile. See: https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system for more info
        return_geometry: bool = True,  # If geometry should be returned. Setting this to false will only return quadkeys
        add_xyz_cols: bool = False,  # If quadkey should be converted to their xyz values.
    ):
        self.zoom_level = zoom_level
        self.return_geometry = return_geometry
        self.add_xyz_cols = add_xyz_cols
        self.tms = morecantile.tms.get("WebMercatorQuad")

    def tile_to_polygon(self, tile: morecantile.Tile):
        """Converts a tile to geometry"""
        return shape(self.tms.feature(tile)["geometry"])

    def get_tiles_for_polygon(
        self,
        polygon: Polygon,
        filter: bool = True,
    ):
        """Get the intersecting tiles with polygon for a zoom level. Polygon should be in EPSG:4326"""
        x_min, y_min, x_max, y_max = polygon.bounds
        tiles = (
            (self.tms.quadkey(tile), self.tile_to_polygon(tile), tile)
            for tile in self.tms.tiles(x_min, y_min, x_max, y_max, self.zoom_level)
        )
        # Return dict to make it easier to deduplicate
        if filter:
            tiles = {
                qk: (geom, tile) for qk, geom, tile in tiles if polygon.intersects(geom)
            }
        else:
            tiles = {qk: (geom, tile) for qk, geom, tile in tiles}
        return tiles

# %% ../notebooks/00_grids.ipynb 23
@patch
def get_all_tiles_for_polygon(self: BingTileGridGenerator, polygon: Polygon):
    """Get the interseting tiles with polygon for a zoom level. Polygon should be in EPSG:4326"""
    x_min, y_min, x_max, y_max = polygon.bounds
    tiles = (
        (self.tms.quadkey(tile), self.tile_to_polygon(tile), tile)
        for tile in self.tms.tiles(x_min, y_min, x_max, y_max, self.zoom_level)
    )
    return tiles

# %% ../notebooks/00_grids.ipynb 24
@patch
def generate_grid(self: BingTileGridGenerator, aoi_gdf: GeoDataFrame) -> DataFrame:
    reprojected_gdf = aoi_gdf.to_crs("epsg:4326")  # quadkeys hexes are in epsg:4326 CRS
    tiles = {}
    unary_union = reprojected_gdf.union_all(method="unary")
    if isinstance(unary_union, Polygon):
        tiles.update(self.get_tiles_for_polygon(unary_union))
    else:
        for geom in unary_union.geoms:
            _tiles = self.get_tiles_for_polygon(geom)
            tiles.update(_tiles)
    quadkey, geom_tile = zip(*((k, v) for k, v in tiles.items()))
    geom, tile = zip(*geom_tile)

    result = {"quadkey": list(quadkey)}

    if self.add_xyz_cols:
        result["x"] = [t.x for t in tile]
        result["y"] = [t.y for t in tile]
        result["z"] = [t.z for t in tile]

    if self.return_geometry:
        tiles_gdf = GeoDataFrame(
            result,
            geometry=list(geom),
            crs="epsg:4326",
        )
        tiles_gdf = tiles_gdf.to_crs(aoi_gdf.crs)
        return tiles_gdf
    else:
        tiles_gdf = DataFrame(result)

    return tiles_gdf

# %% ../notebooks/00_grids.ipynb 25
def get_intersect_partition(item):
    tiles_gdf, reprojected_gdf = item
    tiles_gdf.sindex
    reprojected_gdf.sindex
    intersect_tiles_gdf = tiles_gdf.sjoin(
        reprojected_gdf, how="inner", predicate="intersects"
    )
    return intersect_tiles_gdf

# %% ../notebooks/00_grids.ipynb 26
def get_parallel_intersects(
    tiles_gdf, reprojected_gdf, n_workers=defaults.cpus, progress=True
):

    # split tiles into n chunks (1 chunk per cpu)
    n_splits = int(np.ceil(len(tiles_gdf) / n_workers))
    tile_items = [
        tiles_gdf.iloc[i : i + n_splits] for i in range(0, len(tiles_gdf), n_splits)
    ]

    items = [(tile_item, reprojected_gdf) for tile_item in tile_items]
    intersect_dfs = parallel(
        get_intersect_partition,
        items,
        n_workers=n_workers,
        threadpool=True,
        progress=progress,
    )
    results = pd.concat(intersect_dfs)
    results = results.drop_duplicates(subset=["quadkey"])
    return results

# %% ../notebooks/00_grids.ipynb 27
@patch
def generate_grid_join(
    self: BingTileGridGenerator,
    aoi_gdf: GeoDataFrame,
    filter: bool = True,
    n_workers=defaults.cpus,
    progress=True,
) -> DataFrame:
    reprojected_gdf = aoi_gdf.to_crs("epsg:4326")[
        ["geometry"]
    ]  # quadkeys hexes are in epsg:4326 CRS
    tiles = []
    unary_union = reprojected_gdf.union_all(method="unary")
    if isinstance(unary_union, Polygon):
        tiles += self.get_all_tiles_for_polygon(unary_union)
    else:
        for geom in unary_union.geoms:
            tiles += self.get_all_tiles_for_polygon(
                geom,
            )

    quadkey, geom, tile = zip(*tiles)

    result = {"quadkey": list(quadkey)}

    if self.add_xyz_cols:
        result["x"] = [t.x for t in tile]
        result["y"] = [t.y for t in tile]
        result["z"] = [t.z for t in tile]

    tiles_gdf = GeoDataFrame(
        result,
        geometry=list(geom),
        crs="epsg:4326",
    )

    if filter:
        # tiles_gdf.sindex
        # reprojected_gdf.sindex
        # intersect_tiles_gdf = tiles_gdf.sjoin(
        #     reprojected_gdf,
        #     how='inner',
        #     predicate='intersects')
        intersect_tiles_gdf = get_parallel_intersects(
            tiles_gdf, reprojected_gdf, n_workers=n_workers, progress=progress
        )
        keep_cols = list(tiles_gdf.columns.values)
        tiles_gdf = intersect_tiles_gdf[
            intersect_tiles_gdf.columns.intersection(keep_cols)
        ]
        tiles = tiles_gdf.reset_index(drop=True)

    if not self.return_geometry:
        df = DataFrame(tiles_gdf.drop(columns=["geometry"]))
        return df

    return tiles_gdf.to_crs(aoi_gdf.crs)

# %% ../notebooks/00_grids.ipynb 29
class FastBingTileGridGenerator:
    EPSILON = 1e-14
    PIXEL_DTYPE = polygon_fill.PIXEL_DTYPE
    SUBPOLYGON_ID_COL = polygon_fill.SUBPOLYGON_ID_COL
    MAX_ZOOM = 30

    def __init__(
        self,
        zoom_level: int,  # Zoom level of tile. See: https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system for more info
        return_geometry: bool = True,  # If geometry should be returned. Setting this to false will only return quadkeys
        add_xyz_cols: bool = False,  # If xyz columns should be returned. Unlike BingTileGridGenerator, choosing to return xyz columns doesn't substantionally add compute time.
    ):
        self.zoom_level = zoom_level
        self.return_geometry = return_geometry
        self.add_xyz_cols = add_xyz_cols

        if self.zoom_level > self.MAX_ZOOM:
            raise NotImplementedError(
                f"Maximum allowed zoom level is {self.MAX_ZOOM}. Input was {self.zoom_level}"
            )

# %% ../notebooks/00_grids.ipynb 30
@patch
def generate_grid(
    self: FastBingTileGridGenerator,
    aoi_gdf: GeoDataFrame,
    unique_id_col: Optional[
        str
    ] = None,  # the ids under this column will be preserved in the output tiles
) -> Union[GeoDataFrame, pd.DataFrame]:

    vertices = polygon_fill.polygons_to_vertices(aoi_gdf, unique_id_col)
    vertices = self._latlng_to_xy(vertices, lat_col="y", lng_col="x")

    polygon_fill_result = polygon_fill.fast_polygon_fill(vertices, unique_id_col)
    tiles_in_geom = polygon_fill_result["tiles_in_geom"]

    # this is error correction on the polygon boundary (not the square boundary)
    tiles_off_boundary = polygon_fill_result["tiles_off_boundary"]
    if not tiles_off_boundary.is_empty():
        off_boundary_bboxes = self._xy_to_bbox(tiles_off_boundary, "x", "y")
        all_polygon_boundary = aoi_gdf.boundary.union_all(method="unary")
        intersects_boundary_bool = off_boundary_bboxes.intersects(all_polygon_boundary)
        addtl_tiles_in_geom = tiles_off_boundary.filter(
            pl.Series(intersects_boundary_bool)
        )

        tiles_in_geom = pl.concat([tiles_in_geom, addtl_tiles_in_geom])

    quadkey_expr = self._xyz_to_quadkey(
        pl.col("x"),
        pl.col("y"),
    )
    tiles_in_geom = tiles_in_geom.with_columns(quadkey=quadkey_expr)

    if self.return_geometry:
        bboxes = self._xy_to_bbox(tiles_in_geom, "x", "y")

        if not tiles_off_boundary.is_empty():
            addtl_boundary_bboxes = off_boundary_bboxes[intersects_boundary_bool].copy()
            bboxes = pd.concat([bboxes, addtl_boundary_bboxes], ignore_index=True)

    if not self.add_xyz_cols:
        tiles_in_geom = tiles_in_geom.drop(["x", "y"])
    else:
        tiles_in_geom = tiles_in_geom.with_columns(z=pl.lit(self.zoom_level))
        column_order = ["quadkey", "x", "y", "z"]
        if unique_id_col is not None:
            column_order += [unique_id_col]
        assert set(tiles_in_geom.columns) == set(column_order)
        tiles_in_geom = tiles_in_geom.select(column_order)

    if self.return_geometry:
        tiles_in_geom = GeoDataFrame(tiles_in_geom.to_pandas(), geometry=bboxes)
    else:
        tiles_in_geom = tiles_in_geom.to_pandas()

    return tiles_in_geom

# %% ../notebooks/00_grids.ipynb 31
@patch
def _lat_to_ytile(self: FastBingTileGridGenerator, lat: pl.Expr) -> pl.Expr:
    logtan = pl.Expr.log(pl.Expr.tan((np.pi / 4) + (pl.Expr.radians(lat) / 2)))

    y = 0.5 - (logtan / (2 * np.pi))

    power_of_2 = int(np.power(2, self.zoom_level))

    # To address loss of precision in round-tripping between tile
    # and lng/lat, points within EPSILON of the right side of a tile
    # are counted in the next tile over.
    y_pixel_coord = pl.Expr.floor((y + self.EPSILON) * power_of_2)

    ytile = (
        pl.when(y <= 0)
        .then(pl.lit(0))
        .when(y >= 1)
        .then(pl.lit(power_of_2 - 1))
        .otherwise(y_pixel_coord)
        .cast(self.PIXEL_DTYPE)
    )

    return ytile


@patch
def _lng_to_xtile(self: FastBingTileGridGenerator, lng: pl.Expr) -> pl.Expr:
    x = 0.5 + (lng / 360.0)
    power_of_2 = int(np.power(2, self.zoom_level))

    x_pixel_coord = pl.Expr.floor((x + self.EPSILON) * power_of_2)

    xtile = (
        pl.when(x <= 0)
        .then(pl.lit(0))
        .when(x >= 1)
        .then(pl.lit(power_of_2 - 1))
        .otherwise(x_pixel_coord)
        .cast(self.PIXEL_DTYPE)
    )

    return xtile


@patch
def _latlng_to_xy(
    self: FastBingTileGridGenerator,
    df: pl.DataFrame,
    lat_col: str,
    lng_col: str,
) -> pl.DataFrame:
    xy_df = df.with_columns(
        x=self._lng_to_xtile(pl.col(lng_col)),
        y=self._lat_to_ytile(pl.col(lat_col)),
    )

    return xy_df


@patch
def _xtile_to_lng(self: FastBingTileGridGenerator, xtile: pl.Expr) -> pl.Expr:
    """This gets the longitude of the upper left corner of the tile"""
    power_of_2 = int(np.power(2, self.zoom_level))
    lng_deg = (xtile / power_of_2) * 360.0 - 180.0
    return lng_deg


@patch
def _ytile_to_lat(self: FastBingTileGridGenerator, ytile: pl.Expr) -> pl.Expr:
    """This gets the latitude of the upper left corner of the tile"""
    power_of_2 = int(np.power(2, self.zoom_level))
    y = ytile / power_of_2
    lat_rad = pl.Expr.arctan(pl.Expr.sinh(np.pi * (1 - 2 * y)))
    lat_deg = pl.Expr.degrees(lat_rad)
    return lat_deg


@patch
def _xy_to_bbox(
    self: FastBingTileGridGenerator,
    df: pl.DataFrame,
    xtile_col: str,
    ytile_col: str,
) -> GeoSeries:

    upper_left_lng = self._xtile_to_lng(pl.col(xtile_col))
    upper_left_lat = self._ytile_to_lat(pl.col(ytile_col))
    lower_right_lng = self._xtile_to_lng(pl.col(xtile_col) + 1)
    lower_right_lat = self._ytile_to_lat(pl.col(ytile_col) + 1)

    bbox_df = df.select(
        minx=upper_left_lng,
        miny=lower_right_lat,
        maxx=lower_right_lng,
        maxy=upper_left_lat,
    )

    # use vectorized version in shapely 2.0
    bboxes = box(
        bbox_df["minx"].to_list(),
        bbox_df["miny"].to_list(),
        bbox_df["maxx"].to_list(),
        bbox_df["maxy"].to_list(),
    )
    bboxes = GeoSeries(bboxes, crs="epsg:4326")

    return bboxes


@patch
def _xyz_to_quadkey(self: FastBingTileGridGenerator, x: pl.Expr, y: pl.Expr) -> pl.Expr:

    # Create expressions for the quadkey digit at each bit position
    quadkey_digit_exprs = [
        ((x // (2**i) % 2) | ((y // (2**i) % 2) * 2))
        for i in reversed(range(self.zoom_level))
    ]

    quadkey = pl.concat_str(quadkey_digit_exprs)

    return quadkey
