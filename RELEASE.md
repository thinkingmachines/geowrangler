# How to make a release

## Bumping the version

Run the following. Use `<part>` = 0, 1, 2 for major, minor or patch depending on the release. See https://nbdev.fast.ai/api/release.html#bump-version for more details

```
nbdev_bump_version --part <part>
```

## Publishing

You will need to have an API token for [PyPi](https://pypi.org/) (or [TestPyPi](https://test.pypi.org/)). Ask the current project owners for access. 

Set your `~/.pypirc` file as follows.
```
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = <PyPI token>

[testpypi]
username = __token__
password = <TestPyPI token>
```
Run the following to publish to PyPi (or TestPypi). 
The `<REPOSITORY>` value is either `pypi` or `testpypi`.
```
./scripts/publish2pypi.sh <REPOSITORY>
```

## Updating release notes and tagging a release

1. Document the release notes in `CHANGELOG.md`
2. Run `nbdev_release_git` to create entries for the [release page](https://github.com/thinkingmachines/geowrangler/tags). 
    - You'll need to create a GitHub personal access token for this if you haven't already. See the [nbdev.release docs](https://nbdev.fast.ai/api/release.html#overview), under the `Setup` section, for more details.

## Submitting

Create a PR and tag it as the release version. The tag should be in the format `vX.Y.Z` where `X.Y.Z` is the major, minor and patch version numbers. 
