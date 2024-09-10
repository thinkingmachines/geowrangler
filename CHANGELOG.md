# Release Notes

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
