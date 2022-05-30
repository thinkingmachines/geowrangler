# Contributing

#### Table of Contents

1. [Feedback](#feature-requests-or-feedback)
2. [Report Bugs](#report-bugs)
3. [Creating a Pull Request](#creating-a-pull-request)
4. [Developing with nbdev](#developing-with-nbdev)

## Feedback

Do you like geowrangler, have an idea for a feature, or any comment at all? Feel free to file an [issue in the geowrangler issue tracker](https://github.com/thinkingmachines/geowrangler/issues) and tag it as an _enhancement_. 

## Report Bugs

Report bugs for geowrangler in the [issue tracker](https://github.com/thinkingmachines/geowrangler/issues) and tag them as a _bug_.

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
poetry run pip install pip --upgrade
poetry run pip install -e .
```

3. Make necessary changes. See [Developing with nbdev](#developing-with-nbdev) for more info.

4. Run tests

```
poetry run pytest --cov . -n auto
```

5. Commit and Submit PR for review

## Developing with nbdev

[nbdev](https://nbdev.fast.ai) a library that allows you to develop a python library in Jupyter Notebooks.


### Generating the python code

`nbdev` converts the notebooks within the `notebooks/` folder into python code and used as a library.

Once the necessary changes are made, run the following to generate the python code.

```
poetry run nbdev_build_lib
poetry run pre-commit run -a
poetry run pre-commit run -a
```
> Note: we are running `pre-commit` twice so that it reformats the modules to comply with the project's formatting/linting standards and the next run checks if it is already compliant. 


