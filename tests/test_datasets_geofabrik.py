import os
from pathlib import Path
from urllib.error import HTTPError

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


def test_download_geofabrik_region_err_404(
    mock_geofabrike_req, monkeypatch, mocker, tmpdir
):
    def mock_retrieve(url, filename, **kwargs):
        raise HTTPError(
            "url",
            404,
            "Invalid URL",
            mocker.MagicMock(),
            mocker.MagicMock(),
        )

    monkeypatch.setattr(geofabrik, "urlretrieve", mock_retrieve)
    filepath = geofabrik.download_geofabrik_region(
        "afghanistan", directory=str(tmpdir / "this-directory-does-not-exist")
    )
    assert filepath is None


def test_download_geofabrik_region_year_err_404(
    mock_geofabrike_req, monkeypatch, mocker, tmpdir
):
    def mock_retrieve(url, filename, **kwargs):
        raise HTTPError(
            "url",
            404,
            "Invalid URL",
            mocker.MagicMock(),
            mocker.MagicMock(),
        )

    monkeypatch.setattr(geofabrik, "urlretrieve", mock_retrieve)
    filepath = geofabrik.download_geofabrik_region(
        "afghanistan",
        directory=str(tmpdir / "this-directory-does-not-exist"),
        year="2021",
    )
    assert filepath is None


def test_download_geofabrik_region_other_err(
    mock_geofabrike_req, monkeypatch, mocker, tmpdir
):
    def mock_retrieve(url, filename, **kwargs):
        raise HTTPError(
            "url",
            403,
            "Forbidden",
            mocker.MagicMock(),
            mocker.MagicMock(),
        )

    monkeypatch.setattr(geofabrik, "urlretrieve", mock_retrieve)
    exc_info = None
    with pytest.raises(HTTPError) as exc_info:
        geofabrik.download_geofabrik_region(
            "afghanistan",
            directory=str(tmpdir / "this-directory-does-not-exist"),
            year="2001",
        )
    e = exc_info.value
    assert e.code == 403


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


def test_download_osm_region_data(mock_geofabrike_req, mocker, monkeypatch, tmpdir):
    def mock_retrieve(url, filename, **kwargs):
        return filename, None, None

    monkeypatch.setattr(geofabrik, "urlretrieve", mock_retrieve)
    mocker.patch("geowrangler.datasets.geofabrik.urlcheck", return_value=True)
    filepath = geofabrik.download_osm_region_data(
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


def test_download_osm_region_data_urlretrieve_no_file(
    mock_geofabrike_req, mocker, monkeypatch, tmpdir
):
    def mock_retrieve(url, filename, **kwargs):
        return None, None, None  # filename retrieved is None

    monkeypatch.setattr(geofabrik, "urlretrieve", mock_retrieve)
    mocker.patch("geowrangler.datasets.geofabrik.urlcheck", return_value=True)
    filepath = geofabrik.download_osm_region_data(
        "afghanistan", cache_dir=str(tmpdir / "this-directory-does-not-exist")
    )
    assert filepath is None


def test_download_osm_region_data_fail_urlcheck(
    mock_geofabrike_req, mocker, monkeypatch, tmpdir
):
    mocker.patch("geowrangler.datasets.geofabrik.urlcheck", return_value=False)
    filepath = geofabrik.download_osm_region_data(
        "afghanistan", cache_dir=str(tmpdir / "this-directory-does-not-exist")
    )
    assert filepath is None


def test_download_osm_region_data_with_year_fail_urlcheck(
    mock_geofabrike_req, mocker, monkeypatch, tmpdir
):
    mocker.patch("geowrangler.datasets.geofabrik.urlcheck", return_value=False)
    filepath = geofabrik.download_osm_region_data(
        "afghanistan",
        year="2001",
        cache_dir=str(tmpdir / "this-directory-does-not-exist"),
    )
    assert filepath is None


def test_download_osm_region_data(mock_geofabrike_req, mocker, monkeypatch, tmpdir):
    def mock_retrieve(url, filename, **kwargs):
        return filename, None, None

    monkeypatch.setattr(geofabrik, "urlretrieve", mock_retrieve)
    mocker.patch("geowrangler.datasets.geofabrik.urlcheck", return_value=True)
    filepath = geofabrik.download_osm_region_data(
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


def test_download_existing_osm_region_data_no_cache(
    mock_geofabrike_req, mocker, monkeypatch, tmpdir
):
    def mock_retrieve(url, filename, **kwargs):
        return filename, None, None

    mock_region_zip_file = mocker.MagicMock()
    mock_region_zip_file.exists = mocker.MagicMock(return_value=True)
    monkeypatch.setattr(geofabrik, "urlretrieve", mock_retrieve)
    monkeypatch.setattr(
        geofabrik,
        "get_download_filepath",
        mocker.MagicMock(return_value=mock_region_zip_file),
    )
    mocker.patch("geowrangler.datasets.geofabrik.urlcheck", return_value=True)
    filepath = geofabrik.download_osm_region_data(
        "afghanistan",
        cache_dir=str(tmpdir / "this-directory-does-not-exist"),
        use_cache=False,
    )
    assert os.path.isdir(tmpdir / "this-directory-does-not-exist" / "osm")
    assert filepath == mock_region_zip_file


def test_download_existing_osm_region_data(mocker, tmpdir):
    mock_region_zip_file = mocker.MagicMock()
    mock_region_zip_file.exists = mocker.MagicMock(return_value=True)
    mocker.patch(
        "geowrangler.datasets.geofabrik.get_download_filepath",
        return_value=mock_region_zip_file,
    )
    filepath = geofabrik.download_osm_region_data(
        "afghanistan", cache_dir=str(tmpdir / "this-directory-does-not-exist")
    )
    assert filepath == mock_region_zip_file


def test_download_osm_region_data_with_year(
    mock_geofabrike_req, mocker, monkeypatch, tmpdir
):
    def mock_retrieve(url, filename, **kwargs):
        return filename, None, None

    monkeypatch.setattr(geofabrik, "urlretrieve", mock_retrieve)
    mocker.patch("geowrangler.datasets.geofabrik.urlcheck", return_value=True)
    filepath = geofabrik.download_osm_region_data(
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
    assert "afghanistan" in osm_data_manager.pois_cache
    assert os.path.isdir(tmpdir / "this-directory-does-not-exist" / "osm")
    assert gdf == mock_gdf


def test_reload_pois(mocker, tmpdir):
    """ "reload same country should retrieve gdf from cache"""
    mock_gdf = mocker.MagicMock()

    osm_data_manager = geofabrik.OsmDataManager(
        cache_dir=str(tmpdir / "this-directory-does-not-exist")
    )
    osm_data_manager.pois_cache.update({"afghanistan": mock_gdf})
    gdf = osm_data_manager.load_pois("afghanistan")
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
    assert "afghanistan_21" in osm_data_manager.pois_cache
    assert os.path.isdir(tmpdir / "this-directory-does-not-exist" / "osm")
    assert gdf == mock_gdf


def test_reload_pois_with_year(mocker, tmpdir):
    """ "reload same country should retrieve gdf from cache"""
    mock_gdf = mocker.MagicMock()

    osm_data_manager = geofabrik.OsmDataManager(
        cache_dir=str(tmpdir / "this-directory-does-not-exist")
    )
    osm_data_manager.pois_cache.update({"afghanistan_19": mock_gdf})
    gdf = osm_data_manager.load_pois("afghanistan", year="2019")
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
    assert "afghanistan" in osm_data_manager.roads_cache
    assert os.path.isdir(tmpdir / "this-directory-does-not-exist" / "osm")
    assert gdf == mock_gdf


def test_reload_roads(mocker, tmpdir):
    """ "reload same country should retrieve gdf from cache"""
    mock_gdf = mocker.MagicMock()

    osm_data_manager = geofabrik.OsmDataManager(
        cache_dir=str(tmpdir / "this-directory-does-not-exist")
    )
    osm_data_manager.roads_cache.update({"afghanistan": mock_gdf})
    gdf = osm_data_manager.load_roads("afghanistan")
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
    assert "afghanistan_20" in osm_data_manager.roads_cache
    assert os.path.isdir(tmpdir / "this-directory-does-not-exist" / "osm")
    assert gdf == mock_gdf


def test_reload_roads_with_year(mocker, tmpdir):
    """ "reload same country should retrieve gdf from cache"""
    mock_gdf = mocker.MagicMock()

    osm_data_manager = geofabrik.OsmDataManager(
        cache_dir=str(tmpdir / "this-directory-does-not-exist")
    )
    osm_data_manager.roads_cache.update({"afghanistan_19": mock_gdf})
    gdf = osm_data_manager.load_roads("afghanistan", year="2019")
    assert gdf == mock_gdf
