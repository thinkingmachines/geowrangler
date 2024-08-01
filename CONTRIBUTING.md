# Contributing

#### Table of Contents

1. [Feedback](#feedback)
2. [Report Bugs](#report-bugs)
3. [Creating Pull Requests](#creating-pull-requests)
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
2. Set up the development environment following the instructions in [DEVELOPMENT](https://github.com/thinkingmachines/geowrangler/blob/master/DEVELOPMENT.md)

3. Make the necessary contributions. See [Developing with nbdev](#developing-with-nbdev) for more info.

4. Run the tests and ensure they all pass before submitting a PR. Also add tests whenever adding a new feature. Finally, clean up tests that are longer applicable.

```
pytest --cov --cov-config=.coveragerc --cov-fail-under=80 -n auto
```

5. Commit and Submit PR for review

> Note:  If the code coverage falls below 80 percent, the PR will be rejected.
## Developing with nbdev

[nbdev](https://nbdev.fast.ai) is a library that allows you to develop a python library in [Jupyter Notebooks](https://jupyter.org/) as well, putting all your code and documentation in one place.


### Generating the python code

`nbdev` converts the notebooks within the `notebooks/` folder into python code and used as a library.

Once the necessary changes are made, run the following to generate the python code.

```
nbdev_build_lib
pre-commit run -a
pre-commit run -a
```
> Note: we are running `pre-commit` twice so that it reformats the modules to comply with the project's formatting/linting standards and the next run checks if it is already compliant. 


