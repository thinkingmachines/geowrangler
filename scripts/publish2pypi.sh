#!/bin/bash
sed -i "s/readme_nb = 'readme.ipynb'/readme_nb = 'index.ipynb'/" pyproject.toml
nbdev-readme 
nbdev-pypi --repository $1
sed -i "s/readme_nb = 'index.ipynb'/readme_nb = 'readme.ipynb'/" pyproject.toml
nbdev-readme