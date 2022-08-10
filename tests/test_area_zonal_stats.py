from geowrangler.area_zonal_stats import extract_func


def test_extract_func():
    assert extract_func("count") == ("count", [])
    assert extract_func("raw_count") == ("count", ["raw"])
    assert extract_func("imputed_count") == ("count", ["imputed"])
    assert extract_func("raw_imputed_count") == ("count", ["raw", "imputed"])
