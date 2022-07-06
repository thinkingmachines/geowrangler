"""Utility function for working with bing map tiles quadkey


A lot of code was copied and edited from pyquadkey2 to just get inheritance to work properly.

Once https://github.com/muety/pyquadkey2/pull/11/files is merged.
We can just need to keep get_quadkeys_for_polygon and to_polygon_4326

"""

import morecantile
from shapely.geometry import Polygon, shape


class QuadKey:
    tms = morecantile.tms.get("WebMercatorQuad")

    @classmethod
    def tile_to_polygon(cls, tile):
        return shape(cls.tms.feature(tile)["geometry"])

    @classmethod
    def get_quadkeys_for_polygon(
        cls,
        polygon: Polygon,
        resolution: int,
        id_only: bool = False,
        filter: bool = True,
    ):
        """Converts quadkey to a polygon in the epsg:4325 projection"""
        x_min, y_min, x_max, y_max = polygon.bounds
        tiles = (
            (cls.tms.quadkey(tile), cls.tile_to_polygon(tile))
            for tile in cls.tms.tiles(x_min, y_min, x_max, y_max, resolution)
        )
        # Return dict or set to make it easier to deduplicate
        if filter:
            tiles = {qk: geom for qk, geom in tiles if polygon.intersects(geom)}
        if id_only:
            return {qk for qk, _ in tiles.items()}
        else:
            return tiles
