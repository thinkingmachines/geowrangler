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
nbdev_export
```

## View contributions on documentation site and edit as needed

1. Run nbdev_docs to create the HTML files via Quarto (can verify locally with some port: nbdev_preview --port 4327)
    - Doc site automatically updates once a PR is merged (in Settings > Pages need to make sure [geowrangler.thinkingmachin.es](http://geowrangler.thinkingmachin.es/) is the domain as it defaults to [thinkingmachines.github.io](http://thinkingmachines.github.io/) after merges)
2. Edit [notebooks/index.ipynb](https://github.com/thinkingmachines/geowrangler/blob/master/notebooks/index.ipynb) to edit the [doc homepage](https://geowrangler.thinkingmachin.es/)
3. Edit [notebooks/sidebar.yml](https://github.com/thinkingmachines/geowrangler/blob/master/notebooks/sidebar.yml) to edit the left sidebar

## Updating Google Colab links in notebooks
  - In notebooks such as tutorial notebooks you may want to add a Google Colab link at the beginning of the notebook for easy accessibility.
  - There is no automatic way yet to update this so it's a manual update of a markdown cell. Since the link points to a notebook in master, testing the Colab button is done after merging. Follow the sample below and replace the notebook name with your contributed notebook name.
  - Sample for notebooks/14_datasets_nightlights.ipynb:
[![](https://colab.research.google.com/assets/colab-badge.svg "Open in Colab button")](https://colab.research.google.com/github/thinkingmachines/geowrangler/blob/master/notebooks/14_datasets_nightlights.ipynb)