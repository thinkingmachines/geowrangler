import os
from pathlib import Path

import pytest
import requests

from geowrangler.datasets import ookla
from geowrangler.datasets.ookla import (
    OoklaDataManager,
    OoklaFile,
    add_ookla_features,
    download_ookla_file,
    list_ookla_files,
)


@pytest.fixture
def mock_ookla_req(monkeypatch):
    class MockResponse:
        def raw(*args, **kwargs):
            return b""

        def raise_for_status(self):
            pass

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
    ookla_file = ookla.lookup_ookla_file("2019-01-01_performance_fixed_tiles.parquet")
    assert ookla_file == OoklaFile("fixed", "2019", "1")


def test_download_ookla_file_no_dir(mock_ookla_req, monkeypatch, mocker, tmpdir):
    # monkeypatch.setattr(shutil, "copyfileobj", mocker.MagicMock())
    def mock_retrieve(url, filename, **kwargs):
        return filename, None, None

    monkeypatch.setattr(ookla, "urlretrieve", mock_retrieve)

    filepath = ookla.download_ookla_file(
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
        ookla.download_ookla_file("fixed", "2020", "1", tmpdir)
