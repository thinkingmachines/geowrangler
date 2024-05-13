import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import requests

from geowrangler.datasets import ookla
from geowrangler.datasets.ookla import (
    OoklaDataManager,
    OoklaFile,
    compute_datakey,
    download_ookla_file,
    download_ookla_year_data,
    list_ookla_files,
    lookup_ookla_file,
)


@pytest.fixture
def mock_ookla_req(monkeypatch):
    class MockResponse:
        def raw(*args, **kwargs):
            return b""

        def raise_for_status(self):
            pass  # noqa

        @property
        def text(self):
            return """<?xml version="1.0" encoding="UTF-8"?>
<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
<Name>ookla-open-data</Name>
<Prefix>parquet</Prefix>
<KeyCount>28</KeyCount>
<MaxKeys>1000</MaxKeys>
<IsTruncated>false</IsTruncated>
<Contents>
<Key>parquet/performance/type=fixed/year=2019/quarter=1/2019-01-01_performance_fixed_tiles.parquet</Key>
<LastModified>2021-06-01T19:16:04.000Z</LastModified>
<ETag>&quot;35a51f641831316ceffb0402f0e54550-50&quot;</ETag>
<Size>414572196</Size>
<StorageClass>INTELLIGENT_TIERING</StorageClass>
</Contents>
</ListBucketResult>
            """

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    yield


def test_list_ookla_file(mock_ookla_req):
    files = list_ookla_files()
    assert len(files.keys()) == 1
    assert OoklaFile("fixed", "2019", "1") in files


def test_lookup_ookla_file(mock_ookla_req):
    ookla_file = lookup_ookla_file("2019-01-01_performance_fixed_tiles.parquet")
    assert ookla_file == OoklaFile("fixed", "2019", "1")


def test_download_ookla_file_no_dir(mock_ookla_req, monkeypatch, mocker, tmpdir):
    # monkeypatch.setattr(shutil, "copyfileobj", mocker.MagicMock())
    def mock_retrieve(url, filename, **kwargs):
        return filename, None, None

    monkeypatch.setattr(ookla, "urlretrieve", mock_retrieve)

    filepath = download_ookla_file(
        "fixed", "2019", "1", str(tmpdir / "this-directory-does-not-exist")
    )
    assert os.path.isdir(tmpdir / "this-directory-does-not-exist")
    assert (
        filepath
        == Path(str(tmpdir))
        / "this-directory-does-not-exist"
        / "2019-01-01_performance_fixed_tiles.parquet"
    )


def test_download_ookla_file_no_file(mock_ookla_req, tmpdir):
    with pytest.raises(ValueError):
        download_ookla_file("fixed", "2020", "1", tmpdir)


def test_download_ookla_year_data(mock_ookla_req, mocker, tmpdir):
    fixed_2019_files = {
        OoklaFile("fixed", "2019", "1"): "2019-01-01_performance_fixed_tiles.parquet",
        OoklaFile("fixed", "2019", "2"): "2019-04-01_performance_fixed_tiles.parquet",
        OoklaFile("fixed", "2019", "3"): "2019-07-01_performance_fixed_tiles.parquet",
        OoklaFile("fixed", "2019", "4"): "2019-10-01_performance_fixed_tiles.parquet",
    }
    mocker.patch(
        "geowrangler.datasets.ookla.list_ookla_files", return_value=fixed_2019_files
    )
    mocker.patch(
        "geowrangler.datasets.ookla.download_ookla_parallel", mocker.MagicMock()
    )

    filepath = download_ookla_year_data(
        "fixed", "2019", str(tmpdir / "this-directory-does-not-exist"), use_cache=True
    )
    assert filepath == str(tmpdir / "this-directory-does-not-exist/ookla/fixed/2019")


def test_compute_data_key():
    data_key = compute_datakey(np.array([1.0, 2.0, 3.0, 4.0]), "fixed", "2019", False)
    assert data_key == "401c36c37ff0b73736d6c673afad2325"


def test_ookla_datamanager_load_type_year_data(mock_ookla_req, tmpdir, mocker):
    fixed_2019_files = {
        OoklaFile("fixed", "2019", "1"): "2019-01-01_performance_fixed_tiles.parquet",
        OoklaFile("fixed", "2019", "2"): "2019-04-01_performance_fixed_tiles.parquet",
        OoklaFile("fixed", "2019", "3"): "2019-07-01_performance_fixed_tiles.parquet",
        OoklaFile("fixed", "2019", "4"): "2019-10-01_performance_fixed_tiles.parquet",
    }
    mocker.patch(
        "geowrangler.datasets.ookla.list_ookla_files", return_value=fixed_2019_files
    )
    aoi = mocker.MagicMock()
    aoi.total_bounds = np.array([1.0, 2.0, 3.0, 4.0])
    mocker.patch(
        "geowrangler.datasets.ookla.download_ookla_year_data",
        return_value=str(tmpdir / "this-directory-does-not-exist/ookla/fixed/2019"),
    )
    aoi_quadkeys_df = pd.DataFrame(dict(quadkey=["11111", "22222", "44444"]))
    mock_generator = mocker.MagicMock()
    mock_generator.generate_grid = mocker.MagicMock(return_value=aoi_quadkeys_df)
    mocker.patch("geowrangler.grids.BingTileGridGenerator", return_value=mock_generator)
    fixed_2019_files = [
        "2019-01-01_performance_fixed_tiles.parquet",
        "2019-04-01_performance_fixed_tiles.parquet",
        "2019-07-01_performance_fixed_tiles.parquet",
        "2019-10-01_performance_fixed_tiles.parquet",
    ]

    mocker.patch("os.listdir", return_value=fixed_2019_files)
    ookla_df = pd.DataFrame(
        dict(
            quadkey=["11111", "22222", "333333"],
        )
    )
    mocker.patch("pandas.read_parquet", return_value=ookla_df)

    odm = OoklaDataManager(str(tmpdir / "this-directory-does-not-exist"))
    df = odm.load_type_year_data(aoi, "fixed", "2019")
    assert df is not None
    assert len(df) == 8


def test_ookla_datamanager_load_type_year_data_return_geom(
    mock_ookla_req, tmpdir, mocker
):
    fixed_2019_files = {
        OoklaFile("fixed", "2019", "1"): "2019-01-01_performance_fixed_tiles.parquet",
        OoklaFile("fixed", "2019", "2"): "2019-04-01_performance_fixed_tiles.parquet",
        OoklaFile("fixed", "2019", "3"): "2019-07-01_performance_fixed_tiles.parquet",
        OoklaFile("fixed", "2019", "4"): "2019-10-01_performance_fixed_tiles.parquet",
    }
    mocker.patch(
        "geowrangler.datasets.ookla.list_ookla_files", return_value=fixed_2019_files
    )

    aoi = mocker.MagicMock()
    aoi.total_bounds = np.array([1.0, 2.0, 3.0, 4.0])
    mocker.patch(
        "geowrangler.datasets.ookla.download_ookla_year_data",
        return_value=str(tmpdir / "this-directory-does-not-exist/ookla/fixed/2019"),
    )
    aoi_quadkeys_df = pd.DataFrame(dict(quadkey=["11111", "22222", "44444"]))
    mock_generator = mocker.MagicMock()
    mock_generator.generate_grid = mocker.MagicMock(return_value=aoi_quadkeys_df)
    mocker.patch("geowrangler.grids.BingTileGridGenerator", return_value=mock_generator)

    fixed_2019_files = [
        "2019-01-01_performance_fixed_tiles.parquet",
        "2019-04-01_performance_fixed_tiles.parquet",
        "2019-07-01_performance_fixed_tiles.parquet",
        "2019-10-01_performance_fixed_tiles.parquet",
    ]

    mocker.patch("os.listdir", return_value=fixed_2019_files)
    mock_wkt = "POLYGON((-160.02685546875 70.6435894914449, -160.021362304688 70.6435894914449, -160.021362304688 70.6417687358462, -160.02685546875 70.6417687358462, -160.02685546875 70.6435894914449))"
    mock_tiles = [mock_wkt] * 3

    ookla_df = pd.DataFrame(
        dict(
            quadkey=["11111", "22222", "333333"],
            tile=mock_tiles,
        )
    )
    mocker.patch("pandas.read_parquet", return_value=ookla_df)

    odm = OoklaDataManager(str(tmpdir / "this-directory-does-not-exist"))
    df = odm.load_type_year_data(aoi, "fixed", "2019", return_geometry=True)
    assert df is not None
    assert len(df) == 8


def test_ookla_datamanager_load_type_year_data_cached_data_file(tmpdir, mocker):
    aoi = mocker.MagicMock()
    aoi.total_bounds = np.array([1.0, 2.0, 3.0, 4.0])
    mock_data_key = "401c36c37ff0b73736d6c673afad2325"  ##gitleaks:allow
    mock_cache_dir = str(tmpdir / "this-directory-does-not-exist")
    extension = "csv"
    mock_pd_file = (
        Path(mock_cache_dir) / "ookla" / "processed" / f"{mock_data_key}.{extension}"
    )
    aoi_quadkeys_df = pd.DataFrame(dict(quadkey=[11111, 22222, 44444]))
    mock_pd_file.parent.mkdir(parents=True, exist_ok=True)
    aoi_quadkeys_df.to_csv(mock_pd_file, index=False)
    odm = OoklaDataManager(mock_cache_dir)
    df = odm.load_type_year_data(aoi, "fixed", "2019")
    assert len(aoi_quadkeys_df) == len(df)
    assert list(df["quadkey"].values) == list(aoi_quadkeys_df["quadkey"].values)


def test_ookla_datamanager_load_type_year_data_cached_data_file_return_geom(
    tmpdir, mocker
):
    aoi = mocker.MagicMock()
    aoi.total_bounds = np.array([1.0, 2.0, 3.0, 4.0])
    mock_data_key = "027a5ed231f122bb78715183809ecf89"  ##gitleaks:allow
    mock_cache_dir = str(tmpdir / "this-directory-does-not-exist")
    extension = "geojson"
    mock_pd_file = (
        Path(mock_cache_dir) / "ookla" / "processed" / f"{mock_data_key}.{extension}"
    )
    aoi_quadkeys_df = pd.DataFrame(dict(quadkey=["11111", "22222", "44444"]))
    mock_pd_file.parent.mkdir(parents=True, exist_ok=True)
    aoi_quadkeys_df.to_csv(mock_pd_file, index=False)
    mocker.patch("geopandas.read_file", return_value=aoi_quadkeys_df)
    odm = OoklaDataManager(str(tmpdir / "this-directory-does-not-exist"))
    gdf = odm.load_type_year_data(aoi, "fixed", "2019", return_geometry=True)
    assert gdf is aoi_quadkeys_df


@pytest.fixture()
def mock_ookla_data():
    mock_wkt = "POLYGON((-160.02685546875 70.6435894914449, -160.021362304688 70.6435894914449, -160.021362304688 70.6417687358462, -160.02685546875 70.6417687358462, -160.02685546875 70.6435894914449))"
    mock_tiles = [mock_wkt] * 12
    yield pd.DataFrame(
        dict(
            quadkey=[
                "11111",
                "22222",
                "33333",
                "11111",
                "22222",
                "33333",
                "11111",
                "22222",
                "33333",
                "11111",
                "22222",
                "33333",
            ],
            quarter=[
                "1",
                "1",
                "1",
                "2",
                "2",
                "2",
                "3",
                "3",
                "3",
                "4",
                "4",
                "4",
            ],
            avg_d_kbps=[
                1.0,
                2.0,
                3.0,
                1.0,
                2.0,
                3.0,
                1.0,
                2.0,
                3.0,
                1.0,
                2.0,
                3.0,
            ],
            avg_u_kbps=[
                1.0,
                2.0,
                3.0,
                1.0,
                2.0,
                3.0,
                1.0,
                2.0,
                3.0,
                1.0,
                2.0,
                3.0,
            ],
            avg_lat_ms=[
                1.0,
                2.0,
                3.0,
                1.0,
                2.0,
                3.0,
                1.0,
                2.0,
                3.0,
                1.0,
                2.0,
                3.0,
            ],
            tests=[
                1.0,
                2.0,
                3.0,
                1.0,
                2.0,
                3.0,
                1.0,
                2.0,
                3.0,
                1.0,
                2.0,
                3.0,
            ],
            devices=[
                1.0,
                2.0,
                3.0,
                1.0,
                2.0,
                3.0,
                1.0,
                2.0,
                3.0,
                1.0,
                2.0,
                3.0,
            ],
            tile=mock_tiles,
        )
    )


def test_aggregate_ookla_features(mock_ookla_req, mock_ookla_data, mocker, tmpdir):
    fixed_2019_files = {
        OoklaFile("fixed", "2019", "1"): "2019-01-01_performance_fixed_tiles.parquet",
        OoklaFile("fixed", "2019", "2"): "2019-04-01_performance_fixed_tiles.parquet",
        OoklaFile("fixed", "2019", "3"): "2019-07-01_performance_fixed_tiles.parquet",
        OoklaFile("fixed", "2019", "4"): "2019-10-01_performance_fixed_tiles.parquet",
    }
    mocker.patch(
        "geowrangler.datasets.ookla.list_ookla_files", return_value=fixed_2019_files
    )
    aoi = mocker.MagicMock()
    aoi.total_bounds = np.array([1.0, 2.0, 3.0, 4.0])
    aoi_quadkeys_df = pd.DataFrame(dict(quadkey=["11111", "22222", "44444"]))
    mock_generator = mocker.MagicMock()
    mock_generator.generate_grid = mocker.MagicMock(return_value=aoi_quadkeys_df)
    mocker.patch("geowrangler.grids.BingTileGridGenerator", return_value=mock_generator)
    fixed_2019_files = [
        "2019-01-01_performance_fixed_tiles.parquet",
        "2019-04-01_performance_fixed_tiles.parquet",
        "2019-07-01_performance_fixed_tiles.parquet",
        "2019-10-01_performance_fixed_tiles.parquet",
    ]

    mocker.patch("os.listdir", return_value=fixed_2019_files)
    odm = OoklaDataManager(str(tmpdir / "this-directory-does-not-exist"))
    odm.load_type_year_data = mocker.MagicMock(return_value=mock_ookla_data)
    df = odm.aggregate_ookla_features(aoi, "fixed", "2019")
    assert df is not None
    assert len(df) == 3
