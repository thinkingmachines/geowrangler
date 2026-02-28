#!/bin/bash
sed -i 's/readme_nb = readme.ipynb/readme_nb = index.ipynb/' settings.ini
nbdev-readme 
nbdev-pypi --repository $1
sed -i 's/readme_nb = index.ipynb/readme_nb = readme.ipynb/' settings.ini
nbdev-readme