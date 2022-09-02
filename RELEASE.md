# How to make a release

## Bumping the version

Run the following. Use patch, minor, major, prepatch, preminor, premajor, prerelease depending on the release. See https://python-poetry.org/docs/cli/#version for more details

```
poetry version minor
```

Change the version in `settings.ini` and `geowrangler/__init__.py`

## Publishing

Get an api token for pypi and run

```
poetry config pypi-token.pypi PYPI_TOKEN
```

Run the following

```
rm -r dist/
poetry publish --build
```

## Submitting

Create a PR and tag it as 0.1.0
