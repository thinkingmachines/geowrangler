# Geowrangler
[![License: MIT](https://img.shields.io/github/license/thinkingmachines/geowrangler?style=flat-square)](./LICENSE)
[![Code style: black](https://img.shields.io/badge/code-black-black?style=flat-square)](https://github.com/psf/black)
[![Code style: isort](https://img.shields.io/badge/style-isort-yellow?style=flat-square)](https://pycqa.github.io/isort/)
[![Code style: flake8](https://img.shields.io/badge/lint-flake8-orange?style=flat-square)](https://flake8.pycqa.org/en/latest/)
[![Versions](https://img.shields.io/pypi/pyversions/geowrangler.svg?style=flat-square)](https://pypi.org/project/geowrangler/)
[![Docs](https://img.shields.io/badge/docs-passing-green?style=flat-square)](https://geowrangler.thinkingmachin.es)

> Tools for wrangling with geospatial data


## Overview

**Geowrangler** is a python package for geodata wrangling. It helps you build data transformation workflows with no out-of-the-box solutions from other geospatial libraries.

We have surveyed our past geospatial projects to extract these solutions for our work and hope it will be useful for others as well.

Our audience are researchers, analysts and engineers delivering geospatial projects.

We [welcome your comments, suggestions, bug reports and code contributions](https://github.com/thinkingmachines/geowrangler/discussions) to make **Geowrangler** better. 

### Modules

* Grid Tile Generation
* Geometry Validation 
* Vector Zonal Stats 
* Raster Zonal Stats
* Area Zonal Stats 
* Distance Zonal Stats 
* Demographic and Health Survey (DHS) Processing Utils 
* Geofabrik (OSM) Data Download
* Ookla Data Download

_Check [this page for more details about our Roadmap](https://github.com/orgs/thinkingmachines/projects/17)_

## Installation

```
pip install git+https://github.com/thinkingmachines/geowrangler.git
```

## Documentation

The documentation for [the package is available here](https://geowrangler.thinkingmachin.es)

## Development

### Development Setup

If you want to learn more about **Geowrangler** and explore its inner workings,
you can setup a local development environment. You can run geowrangler's jupyter notebooks
to see how the different modules are built and how they work. 


#### Pre-requisites

* OS: Linux, MacOS, Windows Subsystem for Linux (WSL) on Windows

* Requirements:
   - python 3.7 or higher
   - virtualenv, venv or conda for python environment virtualization
   - poetry for dependency management

#### Github Repo Fork

If you plan to make contributions to geowrangler, we encourage you to
[create your fork](https://github.com/thinkingmachines/geowrangler/fork) of the Geowrangler repo. 

This will then allow you to push commits to your forked repo and 
then create a Pull Request (PR) from your repo to the main geowrangler 
repo for approval by geowrangler's maintainers.

#### Development Installation

We recommend creating a virtual python environment via [virtualenv](https://pypi.org/project/virtualenv/) or 
[conda](https://docs.conda.io/projects/conda/en/latest/user-guide/index.html) for your geowrangler development environment. Please see the relevant
documentation for more details.

The example below uses `virtualenv` to create a separate environment on Linux or WSL
using `python3.9`.

This next command will install `libgeos` ( version >=3.8 required for building pygeos/shapely). See [libgeos documentation](https://libgeos.org/usage/install/) for installation details on other systems.

```
sudo apt install libgeos-dev  # skip this if you already have GEOS
```

Replace the github url below with `git@github.com:<your-github-id>/geowrangler.git` if you created a fork.

```
git clone https://github.com/thinkingmachines/geowrangler.git
cd geowrangler
virtualenv -p /usr/bin/python3.9 .venv
source .venv/bin/activate
pip install pre-commit poetry==1.2.0b3
pre-commit install
poetry config --local installer.no-binary pygeos,shapely
poetry install
```

This completes the installation and setup of a local geowrangler environment.
#### Activating the geowrangler environment

To activate the geowrangler environment, you can `cd <your-local-geowrangler-folder>`
and  run `poetry shell` to activate the environment.


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

### Development Notes

For more details regarding our development standards and processes, please see [our wiki](https://github.com/thinkingmachines/geowrangler/wiki/DeveloperNotes).


