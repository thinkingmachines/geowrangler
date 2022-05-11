# Notes on installing Poetry with an nbdev project
> mind dump while installing nbdev with poetry

## Installation Commands 

```shell
poetry install
poetry shell
poetry add nbdev --dev
poetry add jupyterlab --dev
poetry add jupyterlab-vim --dev # optional
poetry add nb-black --dev #optional
poetry add watchdog --dev #optional
nbdev_new
pip install pip --upgrade  # upgrade pip >= 21.3
pip install -e .
mv *.ipynb notebooks  /.  # move existing notebooks to notebooks directory
pip install pre-commit
pre-commit install
pre-commit run --all-files

```

## Additional features

* Add fastcore and break up class methods into separate cells using `@patch` decorator [TODO]
* Show Samples notebook that doesn't generate code into the package
* Show `utils.py`  that is a pure python module with no notebook equivalent
* Show documentation of parameter args using `nbdev docments` feature [TODO]
* Show add notebook2script to automate code gen at the end of cell execution (see `00_grids.ipynb`)
* Run `make docs_serve` to show doc site ([Requires install of jekyll](https://jekyllrb.com/docs/installation/ubuntu/))
* Run `make watch` to show auto update doc site on notebook changes
* Show `docker-compose up` to run jupyter notebook, jekyll and watch simultaneously
* Publish documentation site to Github pages -- _dependent on public repo status_ ( or alternately, Firebase hosting with authentication) [TODO]


## Issues

* nbdev generated code doesn't pass black formatter
   - workaround: run all nbdev commands prior to running black and doing a commit

