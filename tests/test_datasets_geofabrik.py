import os
import shutil

import pytest
import requests

from geowrangler.datasets import geofabrik


@pytest.fixture
def mock_geofabrike_req(monkeypatch):
    class MockResponse:
        def raw(*args, **kwargs):
            return b""

        @staticmethod
        def json():
            return {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "id": "afghanistan",
                            "parent": "asia",
                            "iso3166-1:alpha2": ["AF"],
                            "name": "Afghanistan",
                            "urls": {
                                "pbf": "https://download.geofabrik.de/asia/afghanistan-latest.osm.pbf",
                                "bz2": "https://download.geofabrik.de/asia/afghanistan-latest.osm.bz2",
                                "shp": "https://download.geofabrik.de/asia/afghanistan-latest-free.shp.zip",
                                "pbf-internal": "https://osm-internal.download.geofabrik.de/asia/afghanistan-latest-internal.osm.pbf",
                                "history": "https://osm-internal.download.geofabrik.de/asia/afghanistan-internal.osh.pbf",
                                "taginfo": "https://taginfo.geofabrik.de/asia/afghanistan/",
                                "updates": "https://download.geofabrik.de/asia/afghanistan-updates",
                            },
                        },
                    },
                ],
            }

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    yield


def test_list_geofabrik_regions(mock_geofabrike_req):
    regions = geofabrik.list_geofabrik_regions()
    assert len(regions.keys()) == 1
    assert "afghanistan" in regions


def test_download_geofabrik_region_no_dir(
    mock_geofabrike_req, monkeypatch, mocker, tmpdir
):
    monkeypatch.setattr(shutil, "copyfileobj", mocker.MagicMock())
    geofabrik.download_geofabrik_region(
        "afghanistan", tmpdir / "this-directory-does-not-exits"
    )
    assert os.path.isdir(tmpdir / "this-directory-does-not-exits")


def test_download_geofabrik_region_no_region(mock_geofabrike_req, tmpdir):
    with pytest.raises(ValueError):
        geofabrik.download_geofabrik_region("this-region-does-not-exist", tmpdir)
