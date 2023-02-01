import os
from pathlib import Path

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


def test_download_geofabrik_region_no_dir(mock_geofabrike_req, monkeypatch, tmpdir):
    def mock_retrieve(url, filename, **kwargs):
        return filename, None, None

    monkeypatch.setattr(geofabrik, "urlretrieve", mock_retrieve)
    filepath = geofabrik.download_geofabrik_region(
        "afghanistan", directory=str(tmpdir / "this-directory-does-not-exist")
    )
    assert os.path.isdir(tmpdir / "this-directory-does-not-exist")
    assert (
        Path(filepath)
        == Path(str(tmpdir))
        / "this-directory-does-not-exist"
        / "afghanistan-latest-free.shp.zip"
    )


def test_download_geofabrik_region_year(mock_geofabrike_req, monkeypatch, tmpdir):
    def mock_retrieve(url, filename, **kwargs):
        return filename, None, None

    monkeypatch.setattr(geofabrik, "urlretrieve", mock_retrieve)
    filepath = geofabrik.download_geofabrik_region(
        "afghanistan", str(tmpdir / "this-directory-does-not-exist"), year="2021"
    )
    assert os.path.isdir(tmpdir / "this-directory-does-not-exist")
    assert (
        Path(filepath)
        == Path(str(tmpdir))
        / "this-directory-does-not-exist"
        / "afghanistan-210101-free.shp.zip"
    )


def test_download_geofabrik_region_no_region(mock_geofabrike_req, tmpdir):
    with pytest.raises(ValueError):
        geofabrik.download_geofabrik_region(
            "this-region-does-not-exist", directory=str(tmpdir)
        )


def test_download_osm_country_data(mock_geofabrike_req, mocker, monkeypatch, tmpdir):
    def mock_retrieve(url, filename, **kwargs):
        return filename, None, None

    monkeypatch.setattr(geofabrik, "urlretrieve", mock_retrieve)
    mocker.patch("geowrangler.datasets.geofabrik.urlcheck", return_value=True)
    filepath = geofabrik.download_osm_country_data(
        "afghanistan", cache_dir=str(tmpdir / "this-directory-does-not-exist")
    )
    assert os.path.isdir(tmpdir / "this-directory-does-not-exist" / "osm")

    assert (
        filepath
        == Path(str(tmpdir))
        / "this-directory-does-not-exist"
        / "osm"
        / "afghanistan-latest-free.shp.zip"
    )
    # assert filepath == str(
    #     Path(str(tmpdir)) / "this-directory-does-not-exist" /"afghanistan-latest-free.shp.zip"
    # )


def test_download_osm_country_data_with_year(
    mock_geofabrike_req, mocker, monkeypatch, tmpdir
):
    def mock_retrieve(url, filename, **kwargs):
        return filename, None, None

    monkeypatch.setattr(geofabrik, "urlretrieve", mock_retrieve)
    mocker.patch("geowrangler.datasets.geofabrik.urlcheck", return_value=True)
    filepath = geofabrik.download_osm_country_data(
        "afghanistan",
        year="2021",
        cache_dir=str(tmpdir / "this-directory-does-not-exist"),
    )
    assert os.path.isdir(tmpdir / "this-directory-does-not-exist" / "osm")
    assert (
        filepath
        == Path(str(tmpdir))
        / "this-directory-does-not-exist"
        / "osm"
        / "afghanistan-210101-free.shp.zip"
    )
    # assert filepath ==  Path(str(tmpdir))/ "this-directory-does-not-exist"/ "osm"/ "afghanistan-210101-latest-free.shp.zip"


def test_load_pois(mock_geofabrike_req, mocker, monkeypatch, tmpdir):
    def mock_retrieve(url, filename, **kwargs):
        return filename, None, None

    mock_gdf = mocker.MagicMock()
    mocker.patch("geowrangler.datasets.geofabrik.urlcheck", return_value=True)
    monkeypatch.setattr(geofabrik, "urlretrieve", mock_retrieve)
    mock_gdf = mocker.MagicMock()
    mocker.patch("geopandas.read_file", return_value=mock_gdf)

    osm_data_manager = geofabrik.OsmDataManager(
        cache_dir=str(tmpdir / "this-directory-does-not-exist")
    )
    gdf = osm_data_manager.load_pois("afghanistan")
    assert os.path.isdir(tmpdir / "this-directory-does-not-exist" / "osm")
    assert gdf == mock_gdf


def test_load_pois_with_year(mock_geofabrike_req, mocker, monkeypatch, tmpdir):
    def mock_retrieve(url, filename, **kwargs):
        return filename, None, None

    mock_gdf = mocker.MagicMock()
    mocker.patch("geopandas.read_file", return_value=mock_gdf)
    monkeypatch.setattr(geofabrik, "urlretrieve", mock_retrieve)
    mocker.patch("geowrangler.datasets.geofabrik.urlcheck", return_value=True)
    osm_data_manager = geofabrik.OsmDataManager(
        cache_dir=str(tmpdir / "this-directory-does-not-exist")
    )
    gdf = osm_data_manager.load_pois("afghanistan", year="2021")
    assert os.path.isdir(tmpdir / "this-directory-does-not-exist" / "osm")
    assert gdf == mock_gdf


def test_load_roads(mock_geofabrike_req, mocker, monkeypatch, tmpdir):
    def mock_retrieve(url, filename, **kwargs):
        return filename, None, None

    mock_gdf = mocker.MagicMock()
    mocker.patch("geopandas.read_file", return_value=mock_gdf)
    monkeypatch.setattr(geofabrik, "urlretrieve", mock_retrieve)
    osm_data_manager = geofabrik.OsmDataManager(
        cache_dir=str(tmpdir / "this-directory-does-not-exist")
    )
    gdf = osm_data_manager.load_roads("afghanistan")
    assert os.path.isdir(tmpdir / "this-directory-does-not-exist" / "osm")
    assert gdf == mock_gdf


def test_load_roads_with_year(mock_geofabrike_req, mocker, monkeypatch, tmpdir):
    def mock_retrieve(url, filename, **kwargs):
        return filename, None, None

    mock_gdf = mocker.MagicMock()
    mocker.patch("geopandas.read_file", return_value=mock_gdf)
    monkeypatch.setattr(geofabrik, "urlretrieve", mock_retrieve)
    osm_data_manager = geofabrik.OsmDataManager(
        cache_dir=str(tmpdir / "this-directory-does-not-exist")
    )
    gdf = osm_data_manager.load_roads("afghanistan", year="2020")
    assert os.path.isdir(tmpdir / "this-directory-does-not-exist" / "osm")
    assert gdf == mock_gdf
