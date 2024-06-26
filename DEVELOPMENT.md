# Geowrangler

## Development

### Development Setup

If you want to learn more about **Geowrangler** and explore its inner workings, you can setup a local development environment. 

You can run geowrangler's jupyter notebooks to see how the different modules are built and how they work. 


#### Pre-requisites

* OS: Linux, MacOS, Windows Subsystem for Linux (WSL) on Windows

* Requirements:
   - python 3.8 or higher
   - virtualenv, venv or conda for python environment virtualization
   - [quarto](https://quarto.org) to preview the documentation site locally
  
#### Github Repo Fork

If you plan to make contributions to geowrangler, we encourage you to
[create your fork](https://github.com/thinkingmachines/geowrangler/fork) of the **Geowrangler** repo. 

This will then allow you to push commits to your forked repo and 
then create a Pull Request (PR) from your repo to the main geowrangler 
repo for approval by geowrangler's maintainers.

#### Development Installation

We recommend creating a virtual python environment via [virtualenv](https://pypi.org/project/virtualenv/) or [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/index.html) for your development environment. Please see the relevant documentation for more details on installing these python environment managers. Afterward, continue with the geowrangler setup instructions below.

To generate and preview the documentation site on your local machine, you will need to install [quarto](https://quarto.org). The following assumes that you have setup quarto on your system.


**Set-up with virtualenv**

Set up your Python env with `virtualenv` and install pre-commits and the necessary python libs by running the following commands.

Remember to replace `<your-github-id>` in the github url below with your GitHub ID to clone from your fork.

```
git clone https://github.com/<your-github-id>/geowrangler.git
cd geowrangler
virtualenv -p /usr/bin/python3.9 .venv
source .venv/bin/activate
pip install -e ".[dev]"
nbdev_install_git_hooks
```

You're all set! [Run the tests](#running-tests) to make sure everything was installed properly.

Whenever you open a new terminal, you can `cd <your-local-geowrangler-folder>`
and  run `source .venv/bin/activate` to activate the geowrangler environment.

**Set-up with conda**

Run the following commands to set-up a conda env and install geos.

```
conda create -y -n geowrangler-env python=3.9 # replace geowrangler-env if you prefer a different env name
conda deactivate # important to ensure libs from other envs aren't used
conda activate geowrangler-env
```

Then run the following to install the pre-commits and python libs.
```
cd geowrangler # cd into your geowrangler local directory
pip install -e ".[dev]"
nbdev_install_git_hooks

```

You're all set! [Run the tests](#running-tests) to make sure everything was installed properly.

Whenever you open a new terminal, run `conda deactivate && conda activate geowrangler-env` to deactivate any conda env, and then activate the geowrangler environment.

### Jupyter Notebook Development

The code for the **geowrangler** python package resides in Jupyter notebooks located in the `notebooks` folder.

Using [nbdev](https://nbdev.fast.ai), we generate the python modules residing in the `geowrangler` folder from code cells in jupyter notebooks marked with an `#| export` comment. A `#| default_exp <module_name>` comment at the first code cell of each notebook directs `nbdev` to put the code in a module named `<module_name>` in the `geowrangler` folder. 

See the [nbdev cli](https://nbdev.fast.ai/cli.html) documentation for more details on the commands to generate the package as well as the documentation.
### Running notebooks

Run the following to view the jupyter notebooks in the `notebooks` folder

```
jupyter lab
```

### Sync the notebook source code with the python modules

To sync the notebook source code with the python modules, run the following.
```
nbdev_export
```
After syncing, you can run the tests to make sure everything is working as expected. See [Running tests](#running-tests) for more details.


### Generating and viewing the documentation site

To generate and view the documentation site on your local machine, the quickest way is to setup [Quarto](https://quarto.org). The following assumes that you have setup quarto on your system.
```
nbdev_preview --port 4371
```

You can now view your documentation site at `http://localhost:4371/`.

### Running tests

We are using `pytest` as our test framework. To run all tests and generate a coverage report, run the following.

```
pytest --cov --cov-config=.coveragerc -n auto
```


To run a single test or test file

```shell
# for a single test function
pytest tests/test_grids.py::test_create_grids
# for a single test file
pytest tests/test_grids.py
```
### Contributing

Please read [CONTRIBUTING.md](https://github.com/thinkingmachines/geowrangler/blob/master/CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](https://github.com/thinkingmachines/geowrangler/blob/master/CODE_OF_CONDUCT.md) before anything.

### Development Notes

For more details regarding our development standards and processes, please see [our wiki](https://github.com/thinkingmachines/geowrangler/wiki/DeveloperNotes).


