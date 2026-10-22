# Release Notes
## Unreleased
### Fixes
 - Fix `FastSquareGridGenerator` and `FastBingTileGridGenerator` returning cells that don't intersect the AOI and missing cells that do. Polygon edges are now traced in fractional cell coordinates instead of between vertices snapped to integer cells, so both return exactly the cells that share area with the AOI
 - Fix polygons with holes in `FastSquareGridGenerator`: cells fully inside a hole are no longer returned. `FastBingTileGridGenerator` now also excludes holes instead of filling the whole exterior with a warning
 - Fix `fast_polygon_fill` changing the shape of polygons that revisit a cell, by no longer de-duplicating vertices

### Improvements
 - `fast_polygon_fill` is vectorized with numpy, making `FastSquareGridGenerator` and `FastBingTileGridGenerator` faster

### Breaking Changes
 - `SquareGridGenerator`, `FastSquareGridGenerator` and `FastBingTileGridGenerator` only return cells that share area with the AOI, like `BingTileGridGenerator`. Cells that only touch the AOI at an edge or a corner are excluded, and so are slivers thinner than a millionth of a cell (`polygon_fill.TOLERANCE`), e.g. from floating point noise after reprojection. This only changes the results for AOIs with edges on the grid lines: e.g. regridding a 15 km cell at 1 km on the same grid returns its 225 cells instead of 289
 - In `gridding_utils.polygon_fill`, vertices are in fractional pixel coordinates and pixel `(x, y)` is the square `[x, x+1] x [y, y+1]`. Off-boundary pixels are removed since the error correction is no longer needed
   - `fast_polygon_fill` returns a polars DataFrame of pixels instead of a dict, and accepts `pixel_bounds`, `y_to_row`, `row_to_y` and `tolerance`
   - `voxel_traversal_scanline_fill` returns a set of pixels instead of a dict, and accepts a `ring_col` for polygons with holes and a `tolerance`
   - `voxel_traversal_2d` returns a set of pixels instead of a dict, and accepts a `tolerance`. Use `tolerance=0` to include the pixels that only touch the segment
   - the `debug` parameter is removed from `voxel_traversal_2d`, `scanline_fill` and `voxel_traversal_scanline_fill`
   - `fast_polygon_fill` no longer sorts its output, and raises a `ValueError` when `unique_id_col` is None and `vertices_df` has more than one id column
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
