# Contributing

#### Table of Contents

1. [Feedback](#feature-requests-or-feedback)
2. [Report Bugs](#report-bugs)
3. [Creating a Pull Request](#creating-a-pull-request)
4. [Developing with nbdev](#developing-with-nbdev)

## Feedback

Do you like geowrangler, have an idea for a feature, or any comment at all? Feel free to email us at geowrangler@thinkingmachin.es.

## Report Bugs

Report bugs for geowrangler in the [issue tracker](https://github.com/thinkingmachines/geowrangler/issues)

If you are reporting a bug, please include:

- Operating system name and version
- Python version
- Dependencies installed
- Sample data if necessary
- Details to reproduce the bug

## Creating pull requests

1. Fork the repo in Github or go to https://github.com/thinkingmachines/geowrangler/fork
2. Enable and install pre-commit and poetry

```
pip install poetry pre-commit
pre-commit install
poetry install
```

3. Make necessary changes. See [Developing with nbdev](#developing-with-nbdev) or more info

4. Run tests

```
poetry run pytest --cov . -n auto
```

5. Commit and Submit PR for review

## Developing with nbdev

[nbdev](https://github.com/fastai/nbdev) a library that allows you to develop a python library in Jupyter Notebooks.

### Running notebooks

Run the following to start a jupyter notebook

```
poetry run jupyter lab
```

### Generating the python code

`nbdev` converts the notebooks within the `notebooks/` folder into python code and used as a library.

Once the necessary changes are made, run the following to generate the python code.

```
poetry run nbdev_build_lib
```

### Generating the docs

`nbdev` converts notebooks within the `notebooks/` folder into a jekyll site.

From this jekyll site, you can then create a static site.

To generate the docs, run the following

```
poetry run nbdev_build_docs
```

To run the jekyll site, run the following

```
cd docs
bundle exec jekyll serve
```
