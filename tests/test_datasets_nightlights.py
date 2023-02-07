import json
import os
from pathlib import Path
from urllib.error import HTTPError
import numpy as np

import pytest

import geowrangler.datasets.nightlights as ntl

TEST_ACCESS_TOKEN_VALUE = "Test Access Token Value"


@pytest.fixture
def mock_eog_credentials(mocker):
    mock_response = mocker.MagicMock()
    mock_response.text = json.dumps(dict(access_token=TEST_ACCESS_TOKEN_VALUE))
    mocker.patch("requests.post", return_value=mock_response)
    yield


def test_get_eog_access_token(mock_eog_credentials):
    access_token = ntl.get_eog_access_token("test user", "test password")
    assert access_token == TEST_ACCESS_TOKEN_VALUE


def test_get_eog_access_token_save_token(mock_eog_credentials, tmpdir):
    save_path = str(tmpdir / "this-directory-does-not-exist/eog_access_token")
    access_token = ntl.get_eog_access_token(
        "test user", "test password", save_token=True, save_path=save_path
    )
    assert access_token == TEST_ACCESS_TOKEN_VALUE
    creds_file = Path(save_path)
    assert creds_file.is_file()
    assert os.environ.get("EOG_ACCESS_TOKEN", None) == TEST_ACCESS_TOKEN_VALUE


def test_clear_eog_access_token(tmpdir):
    save_path = str(tmpdir / "this-directory-does-not-exist/eog_access_token")
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w") as f:
        f.write(TEST_ACCESS_TOKEN_VALUE)
    os.environ["EOG_ACCESS_TOKEN"] = TEST_ACCESS_TOKEN_VALUE
    ntl.clear_eog_access_token(save_file=save_path)
    assert not Path(save_path).exists()
    assert os.environ.get("EOG_ACCESS_TOKEN", None) == ""


def test_generate_nightlights_feature(mocker, tmpdir):
    aoi = mocker.MagicMock()
    aoi.copy = mocker.MagicMock(return_value=aoi)
    aoi.total_bounds = np.array([1.0, 2.0, 3.0, 4.0])
    cache_dir = str(tmpdir / "this-directory-does-not-exist")
    filename = Path(cache_dir) / "nightlights" / "testdata.tif.gz"
    filename.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w") as f:
        f.write("test zip file contents")
    mock_response = (filename, {}, None)
    mocker.patch(
        "geowrangler.datasets.nightlights.urlretrieve", return_value=mock_response
    )
    mocker.patch("gzip.open", return_value=mocker.MagicMock())
    mocker.patch("shutil.copyfileobj", mocker.MagicMock())
    mocker.patch(
        "geowrangler.raster_process.query_window_by_polygon", mocker.MagicMock()
    )
    mocker.patch(
        "geowrangler.raster_zonal_stats.create_raster_zonal_stats",
        mocker.MagicMock(return_value=aoi),
    )

    os.environ["EOG_ACCESS_TOKEN"] = TEST_ACCESS_TOKEN_VALUE
    aoi_result = ntl.generate_nightlights_feature(aoi, "2017", cache_dir=cache_dir)
    assert aoi_result is aoi
