# Release Notes
## 0.6.0
0.5.2 was not published to PyPI, so this release also includes the 0.5.2 changes below.

### Fixes
 - `FastSquareGridGenerator` and `FastBingTileGridGenerator` return exactly the cells that share area with the AOI. Before, they could return cells that don't touch it and miss cells that do (PR [#271](https://github.com/thinkingmachines/geowrangler/pull/271))
 - The fast grid generators exclude cells inside polygon holes
 - `raster_zonal_stats` no longer needs `fiona`, and `datasets.geofabrik` works with `fastcore` 2
 - `raster_to_dataframe.generate_mask` raises a clear error when `labels_column` is missing (PR [#272](https://github.com/thinkingmachines/geowrangler/pull/272)) from [@AmmarYasser455](https://github.com/AmmarYasser455)

### Improvements
 - The fast grid generators are several times faster

### Breaking Changes
 - `SquareGridGenerator`, `FastSquareGridGenerator` and `FastBingTileGridGenerator` exclude cells that only touch the AOI at an edge or corner. This only changes results for AOIs with edges on the grid lines
 - `gridding_utils.polygon_fill`:
   - vertices are in fractional pixel coordinates, and off-boundary pixels are removed
   - `fast_polygon_fill` returns a DataFrame instead of a dict and no longer sorts it
   - `voxel_traversal_2d` and `voxel_traversal_scanline_fill` return sets instead of dicts
   - the fill functions take a `tolerance`, and the `debug` parameters are removed
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
