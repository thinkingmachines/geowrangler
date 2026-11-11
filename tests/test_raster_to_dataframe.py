import pytest

import geowrangler.raster_to_dataframe as rtdf

TIFF_FILE = "data/vector_to_raster_mask_sample/cabanglasan.tif"
SHAPE_FILE = "data/vector_to_raster_mask_sample/labels_20220816.gpkg"
LABELS = {
    "mining": 1,
    "neg": 2,
    "agriculture": 3,
    "product_extraction": 4,
    "kaingin": 5,
    "biophysical": 6,
}


def test_generate_mask(tmp_path):
    masks, grids, values = rtdf.generate_mask(
        tiff_file=TIFF_FILE,
        shape_file=SHAPE_FILE,
        output_file=tmp_path / "mask.tiff",
        labels_column="label",
        labels_dict=LABELS,
    )
    assert values == LABELS
    assert masks.shape == grids.shape
    assert (tmp_path / "mask.tiff").exists()


def test_generate_mask_missing_labels_column(tmp_path):
    with pytest.raises(ValueError, match="not_a_column"):
        rtdf.generate_mask(
            tiff_file=TIFF_FILE,
            shape_file=SHAPE_FILE,
            output_file=tmp_path / "mask.tiff",
            labels_column="not_a_column",
            labels_dict=LABELS,
        )
