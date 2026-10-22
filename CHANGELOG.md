# Release Notes
## Unreleased
### Fixes
 - Fix `FastSquareGridGenerator` and `FastBingTileGridGenerator` returning cells that don't intersect the AOI and missing cells that do. Polygon edges are now traced in fractional cell coordinates instead of between vertices snapped to integer cells, so both return exactly the cells whose closed square intersects the AOI (the same as shapely's `intersects`)
 - Fix polygons with holes in `FastSquareGridGenerator`: cells fully inside a hole are no longer returned. `FastBingTileGridGenerator` now also excludes holes instead of filling the whole exterior with a warning
 - Fix `fast_polygon_fill` changing the shape of polygons that revisit a cell, by no longer de-duplicating vertices

### Improvements
 - `fast_polygon_fill` is vectorized with numpy, making `FastSquareGridGenerator` and `FastBingTileGridGenerator` faster

### Breaking Changes
 - `FastBingTileGridGenerator` now includes tiles that only touch the AOI at an edge or a corner, e.g. along the tile borders at longitude 0 and latitude 0
 - In `gridding_utils.polygon_fill`, vertices are in fractional pixel coordinates and pixel `(x, y)` is the closed square `[x, x+1] x [y, y+1]`. Off-boundary pixels are removed since the error correction is no longer needed
   - `fast_polygon_fill` returns a polars DataFrame of pixels instead of a dict, and accepts `pixel_bounds`, `y_to_row` and `row_to_y`
   - `voxel_traversal_scanline_fill` returns a set of pixels instead of a dict, and accepts a `ring_col` for polygons with holes
   - `voxel_traversal_2d` returns a set of pixels instead of a dict
   - `polygons_to_vertices` adds a `__ring_id__` column

## 0.5.2
### Improvements
 - Upgrade Python development version to `3.14` 
 - Upgrade `nbdev` to `nbdev3` `(3.x)` 
 - Improve markdown describing off-boundary pixels 

### Fixes
 - Fix h3 version4 module incompatibility
 - Fix FastBingTileGridGenerator 

### Others
 - Add maintenance note
  
## 0.5.1

### Improvements
- Missing corner tiles issue is fixed for both `FastSquareGridGenerator` and `FastBingTileGenerator` (PR [#255](https://github.com/thinkingmachines/geowrangler/pull/255)) from [@joshuacortez](https://github.com/joshuacortez)

## 0.5.0

### New Features

- `FastSquareGridGenerator` as a faster equivalent to `SquareGridGenerator` (PR [#253](https://github.com/thinkingmachines/geowrangler/pull/253)) from [@joshuacortez](https://github.com/joshuacortez)
  - Just like `FastBingTileGenerator`, this is also added in `00_grids.ipynb`.

### Improvements
- The `generate_grid` method in `SquareGridGenerator` and `FastSquareGridGenerator` shows a warning when the boundary of doesn't fully enclose the AOI. (issue [#147](https://github.com/thinkingmachines/geowrangler/issues/147))

## 0.4.0

### New Features

- `FastBingTileGenerator` for significantly speeding up grid generation ([#245](https://github.com/thinkingmachines/geowrangler/pull/245)), thanks to [@joshuacortez](https://github.com/joshuacortez)
  - This PR adds a new gridding class `FastBingTileGenerator` that significantly speeds up grid generation. This is added in `00_grids.ipynb`.

- `Exactextract zonal stats` method for a faster raster zonal stats implementation based on `exactextract` python package ([#236](https://github.com/thinkingmachines/geowrangler/pull/236)), thanks to [@tm-jc-nacpil](https://github.com/tm-jc-nacpil)

  - This PR adds a new method `create_raster_zonal_stats_exactextract` that uses the `exactextract` python package for a faster raster zonal stats implementation. This is added in `02_raster_zonal_stats.ipynb`.

- Documentation updates: updated the Development, Contributing and Release sections of the documentation to reflect the new development and release processes.

## 0.1.0 - Initial Release

### Features

- Implemented `GridGenerator`
- Implemented `GeometryValidation`
- Implemented `VectorZonalStats`
- Implemented `RasterZonalStats`
- Implemented `AreaZonalStats`
- Implemented `DistanceZonalStats`
- Implemented dataset download for ookla and geofabrik
- Implemented DHS utility functions
