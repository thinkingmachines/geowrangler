# Geowrangler

## Usage

### Installation

```
git clone git@github.com:thinkingmachines/geowrangler.git
pip install -e geowrangler
```

### Usage

Generate square grids

```python
import geopandas as gpd
from geowrangler import grids
gdf = gpd.read_file("../admin.geojson")
grid_generator = tile_generator.GridGenerator(gdf, 100)
grids_gdf = grid_generator.generate_grids()
grids_gdf.to_file("../grids.geojson", drivers="GeoJSON")
```

## Development

See [CONTRIBUTING.md](/CONTRIBUTING.md) before anything

### Setting up

```
pip install pre-commit
pre-commit install
poetry install
```

### Running tests

We are using `pytest` as our test runner. To run all tests and generate a generate a coverage report, run the following.

```
poetry run pytest --cov . -n auto
```

To run a single test or test file

```
# for a single test function
poetry run pytest tests/test_grids.py::test_create_grids
# for a single test file
poetry run pytest tests/test_grids.py
```
