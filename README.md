# Geowrangler
> Tools for wrangling with geospatial data

## Overview

**Geowrangler** is a python package for geodata wrangling. It helps you build data transformation workflows with no out-of-the-box solutions from other geospatial libraries.

We have surveyed our past geospatial projects to extract these solutions for our work and hope it will be useful for others as well.

Our audience are researchers, analysts and engineers delivering geospatial projects.

We [welcome your comments, suggestions, bug reports and code contributions](https://github.com/thinkingmachines/geowrangler/issues) to make **Geowrangler** better. 

### Modules

* Grid Tile Generation
* Geometry Validation 
* Vector Zonal Stats 
* Raster Zonal Stats (_planned_)
* Geometry Simplification (_planned_)
* Grid Tile Spatial Imputation (_planned_)

## Installation

```
pip install git+https://github.com/thinkingmachines/geowrangler.git
```

## Documentation

The documentation for [the package is available here](https://geowrangler.web.app)

## Development

### Development Setup

If you want to learn more about **Geowrangler** and explore its inner workings,
you can setup a local development environment. You can run geowrangler's jupyter notebooks
to see how the different modules are built and how they work. 

Please ensure you are using python `3.7` or higher

```
pip install pre-commit poetry
pre-commit install
poetry install
poetry run pip install pip --upgrade
poetry run pip install -e .
```
### Jupyter Notebook Development

The code for the **geowrangler** python package resides in Jupyter notebooks located in the `notebooks` folder.

Using [nbdev](https://nbdev.fast.ai), we generate the python modules residing in the `geowrangler` folder from code cells in jupyter notebooks marked with an `#export` comment. A `#default_exp <module_name>` comment at the first code cell of each notebook directs `nbdev` to put the code in a module named `<module_name>` in the `geowrangler` folder. 

See the [nbdev cli](https://nbdev.fast.ai/cli.html) documentation for more details on the commands to generate the package as well as the documentation.
### Running notebooks

Run the following to view the jupyter notebooks in the `notebooks` folder

```
poetry run jupyter lab
```
### Generating and viewing the documentation site

To generate and view the documentation site on your local machine, the quickest way is to setup [Docker](https://docs.docker.com/get-started/). The following assumes that you have setup docker on your system.
```
poetry run nbdev_build_docs --mk_readme False --force_all True
docker-compose up jekyll
```

As an alternative if you don't want to use _Docker_ you can [install jekyll](https://jekyllrb.com/docs/installation/) to view the documentation site locally.

`nbdev` converts notebooks within the `notebooks/` folder into a jekyll site.

From this jekyll site, you can then create a static site.

To generate the docs, run the following

```

poetry run nbdev_build_docs -mk_readme False --force_all True
cd docs && bundle i && cd ..

```

To run the jekyll site, run the following

```
cd docs
bundle exec jekyll serve
```

### Running tests

We are using `pytest` as our test framework. To run all tests and generate a generate a coverage report, run the following.

```
poetry run pytest --cov --cov-config=.coveragerc -n auto
```


To run a single test or test file

```shell
# for a single test function
poetry run pytest tests/test_grids.py::test_create_grids
# for a single test file
poetry run pytest tests/test_grids.py
```
### Contributing

Please read [CONTRIBUTING.md](https://github.com/thinkingmachines/geowrangler/blob/master/CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](https://github.com/thinkingmachines/geowrangler/blob/master/CODE_OF_CONDUCT.md) before anything.

