.ONESHELL:
SHELL := /bin/bash
SRC = $(wildcard notebooks/*.ipynb)

all: geowrangler docs

geowrangler: $(SRC)
	nbdev_build_lib
	touch geowrangler
	pre-commit run -a
	pre-commit run -a

sync:
	nbdev_update_lib

docs_serve: docs
	cd docs && bundle exec jekyll serve

docs: $(SRC)
	nbdev_build_docs --mk_readme False --force_all True
	touch docs

test:
	pytest --cov --cov-config=.coveragerc -n auto 

release: pypi conda_release
	nbdev_bump_version

conda_release:
	fastrelease_conda_package

pypi: dist
	twine upload --repository pypi dist/*

dist: clean
	python setup.py sdist bdist_wheel

clean:
	rm -rf dist

watch:
	watchmedo shell-command --patterns="notebooks/*.ipynb" --command='nbdev_build_docs --mk_readme False --force_all True' --recursive --drop