import logging

import numpy as np
from geopandas import GeoDataFrame
from shapely.geometry import Polygon

logger = logging.getLogger(__name__)


class GridGenerator:
    def __init__(
        self,
        gdf: GeoDataFrame,
        grid_size: float,
        grid_projection: str = "EPSG:3857",
    ):
        self.gdf = gdf
        self.grid_size = grid_size
        self.grid_projection = grid_projection

    def get_ranges(self):
        """Get ranges of the top and left corners of grid"""
        reprojected_gdf = self.gdf.to_crs(self.grid_projection)
        minx, miny, maxx, maxy = reprojected_gdf.total_bounds
        xrange = np.arange(minx, maxx, self.grid_size)
        yrange = np.arange(miny, maxy, self.grid_size)
        return xrange, yrange

    def create_grid(self, x: float, y: float) -> Polygon:
        """Create a grid based on the top left coordinates and grid_size"""
        return Polygon(
            [
                (x, y),
                (x + self.grid_size, y),
                (x + self.grid_size, y + self.grid_size),
                (x, y + self.grid_size),
            ]
        )

    def generate_grids(self) -> GeoDataFrame:
        xrange, yrange = self.get_ranges()
        polygons = []
        for x_idx, x in enumerate(xrange):
            for y_idx, y in enumerate(yrange):
                polygons.append(
                    {"x": x_idx, "y": y_idx, "geometry": self.create_grid(x, y)}
                )
        dest = GeoDataFrame(polygons, geometry="geometry", crs=self.grid_projection)
        dest_reproject = dest.to_crs(self.gdf.crs)
        final = dest_reproject[dest_reproject.intersects(self.gdf.unary_union)]
        return final