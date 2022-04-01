import numpy as np
from geopandas import GeoDataFrame
from shapely.geometry import Polygon


class TileGenerator:
    def __init__(
        self,
        gdf: GeoDataFrame,
        grid_size: float,
        grid_projection: str = "EPSG:3857",
    ):
        self.gdf = gdf
        self.grid_size = grid_size
        self.grid_projection = grid_projection

    def generate_grids(self) -> GeoDataFrame:
        reprojected_gdf = self.gdf.to_crs(self.grid_projection)
        minx, miny, maxx, maxy = reprojected_gdf.total_bounds
        grid_size = self.grid_size
        xrange = np.arange(minx, maxx, grid_size)
        yrange = np.arange(miny, maxy, grid_size)
        polygons = []
        for x_idx, x in enumerate(xrange):
            for y_idx, y in enumerate(yrange):
                polygons.append(
                    {
                        "x": x_idx,
                        "y": y_idx,
                        "geometry": Polygon(
                            [
                                (x, y),
                                (x + grid_size, y),
                                (x + grid_size, y + grid_size),
                                (x, y + grid_size),
                            ]
                        ),
                    }
                )
        dest = GeoDataFrame(polygons, geometry="geometry", crs=self.grid_projection)
        dest_reproject = dest.to_crs(self.gdf.crs)
        final = dest_reproject[dest_reproject.intersects(self.gdf.unary_union)]
        return final
