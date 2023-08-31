import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import multipolygon, point, polygon

from geowrangler import validation


@pytest.fixture()
def misoriented_geometry():
    """Generates a shapely polygon that where the points are clockwise"""
    return polygon.Polygon(([(0, 0), (0, 1), (1, 1), (1, 0)]))


@pytest.fixture()
def oriented_geometry():
    """Generates a shapely polygon that where the points are counter-clockwise"""
    return polygon.Polygon(([(0, 0), (1, 0), (1, 1), (0, 1)]))


@pytest.fixture()
def misoriented_multipolygon():
    return multipolygon.MultiPolygon(
        [
            polygon.Polygon(([(0, 0), (0, 1), (1, 1), (1, 0)])),
            polygon.Polygon(([(10, 10), (11, 10), (11, 11), (10, 11)])),
        ]
    )


@pytest.fixture()
def oriented_multipolygon():
    return multipolygon.MultiPolygon(
        [
            polygon.Polygon(([(0, 0), (1, 0), (1, 1), (0, 1)])),
            polygon.Polygon(([(10, 10), (11, 10), (11, 11), (10, 11)])),
        ]
    )


@pytest.fixture()
def self_intersecting_geometry():
    return polygon.Polygon([(0, 0), (0, 2), (1, 1), (2, 2), (2, 0), (1, 1), (0, 0)])


@pytest.fixture()
def fixed_self_intersecting_geometry():
    return multipolygon.MultiPolygon(
        [
            polygon.Polygon([(0, 0), (0, 2), (1, 1), (0, 0)]),
            polygon.Polygon([(1, 1), (2, 2), (2, 0), (1, 1)]),
        ]
    )


def test_validator_validate_passes(mocker):
    check = mocker.MagicMock(return_value=True)
    fix = mocker.MagicMock(return_value=polygon.Polygon([(0, 0), (1, 0), (1, 1)]))

    class TestValidator(validation.BaseValidator):
        validator_column_name = "test_column"

        def fix(self, geometry):
            return fix(geometry)

        def check(self, geometry):
            return check(geometry)

    gdf = gpd.GeoDataFrame(
        geometry=[
            polygon.Polygon([(0, 0), (1, 0), (0, 1)]),
        ]
    )
    validated_gdf = TestValidator().validate(gdf)
    check.assert_called_once()
    fix.assert_not_called()
    assert "test_column" in validated_gdf


def test_validator_validate_fails(mocker):
    check = mocker.MagicMock(return_value=False)
    fix = mocker.MagicMock(return_value=polygon.Polygon([(0, 0), (1, 0), (1, 1)]))

    class TestValidator(validation.BaseValidator):
        validator_column_name = "test_column"

        def fix(self, geometry):
            return fix(geometry)

        def check(self, geometry):
            return check(geometry)

    gdf = gpd.GeoDataFrame(
        geometry=[
            polygon.Polygon([(0, 0), (1, 0), (0, 1)]),
        ]
    )
    validated_gdf = TestValidator().validate(gdf)
    check.assert_called_once()
    fix.assert_called_once()
    assert "test_column" in validated_gdf


def test_validator_validate_no_column(mocker):
    check = mocker.MagicMock(return_value=False)
    fix = mocker.MagicMock(return_value=polygon.Polygon([(0, 0), (1, 0), (1, 1)]))

    class TestValidator(validation.BaseValidator):
        validator_column_name = "test_column"

        def fix(self, geometry):
            return fix(geometry)

        def check(self, geometry):
            return check(geometry)

    gdf = gpd.GeoDataFrame(
        geometry=[
            polygon.Polygon([(0, 0), (1, 0), (0, 1)]),
        ]
    )
    validated_gdf = TestValidator(add_new_column=False).validate(gdf)
    check.assert_called_once()
    fix.assert_called_once()
    assert "test_column" not in validated_gdf


def test_validator_validate_apply_fix(mocker):
    check = mocker.MagicMock(return_value=False)
    fix = mocker.MagicMock(return_value=polygon.Polygon([(0, 0), (1, 0), (1, 1)]))

    class TestValidator(validation.BaseValidator):
        validator_column_name = "test_column"

        def fix(self, geometry):
            return fix(geometry)

        def check(self, geometry):
            return check(geometry)

    gdf = gpd.GeoDataFrame(
        geometry=[
            polygon.Polygon([(0, 0), (1, 0), (0, 1)]),
        ]
    )
    validated_gdf = TestValidator(apply_fix=False).validate(gdf)
    check.assert_called_once()
    fix.assert_not_called()
    assert "test_column" in validated_gdf


def test_validator_skip(mocker):
    check = mocker.MagicMock(return_value=True)
    fix = mocker.MagicMock(return_value=polygon.Polygon([(0, 0), (1, 0), (1, 1)]))

    class TestValidator(validation.BaseValidator):
        validator_column_name = "test_column"
        geometry_types = ["Point"]

        def fix(self, geometry):
            return fix(geometry)

        def check(self, geometry):
            return check(geometry)

    gdf = gpd.GeoDataFrame(
        geometry=[
            polygon.Polygon([(0, 0), (1, 0), (0, 1)]),
            None,
        ]
    )
    TestValidator().validate(gdf)
    check.assert_not_called()
    fix.assert_not_called()


def test_orientation_validator_geometry_type():
    gdf = gpd.GeoDataFrame(geometry=[point.Point(0, 0)])
    assert validation.OrientationValidator().validate(gdf)["is_oriented_properly"].all()


def test_orientation_validator_invalid(misoriented_geometry):
    assert not validation.OrientationValidator().check(geometry=misoriented_geometry)


def test_orientation_validator_valid(oriented_geometry):
    assert validation.OrientationValidator().check(geometry=oriented_geometry)


def test_orientation_validator_fix_invalid(misoriented_geometry, oriented_geometry):
    assert (
        validation.OrientationValidator()
        .fix(geometry=misoriented_geometry)
        .equals(oriented_geometry)
    )


def test_orientation_validator_invalid_multipolygon(misoriented_multipolygon):
    assert (
        validation.OrientationValidator().check(geometry=misoriented_multipolygon)
        is False
    )


def test_orientation_validator_valid_multipolygon(oriented_multipolygon):
    assert (
        validation.OrientationValidator().check(geometry=oriented_multipolygon) is True
    )


def test_orientation_validator_fix_invalid_multipolygon(
    misoriented_multipolygon, oriented_multipolygon
):
    assert (
        validation.OrientationValidator()
        .fix(geometry=misoriented_multipolygon)
        .equals(oriented_multipolygon)
    )


def test_geometry_validation(oriented_geometry):
    gdf = gpd.GeoDataFrame(
        geometry=[
            oriented_geometry,
        ],
        crs="EPSG:4326",
    )
    validation.GeometryValidation(gdf).validate_all()


def test_geometry_validation_by_class(oriented_geometry):
    gdf = gpd.GeoDataFrame(
        geometry=[
            oriented_geometry,
        ],
        crs="EPSG:4326",
    )
    validation.GeometryValidation(
        gdf,
        validators=[
            validation.NullValidator,
            validation.SelfIntersectingValidator,
            validation.OrientationValidator,
            validation.CrsBoundsValidator,
        ],
    ).validate_all()


def test_geometry_validation_get_validators(oriented_geometry):
    gdf = gpd.GeoDataFrame(geometry=[oriented_geometry])
    validators = validation.GeometryValidation(gdf, ["orientation"])._get_validators()
    assert all(issubclass(v, validation.BaseValidator) for v in validators)


def test_geometry_validation_get_validators_not_valid(
    oriented_geometry,
):

    gdf = gpd.GeoDataFrame(geometry=[oriented_geometry])
    with pytest.raises(validation.ValidationError):
        validation.GeometryValidation(gdf, ["not-valid"])._get_validators()


def test_geometry_validation_get_validators_not_valid_object(
    oriented_geometry,
):

    gdf = gpd.GeoDataFrame(geometry=[oriented_geometry])
    with pytest.raises(validation.ValidationError):
        validation.GeometryValidation(gdf, [object])._get_validators()


def test_crs_bounds():
    p = polygon.Polygon([(200, 0), (1, 0), (0, 1)])
    gdf = gpd.GeoDataFrame(
        geometry=[
            p,
        ],
        crs="EPSG:4326",
    )
    assert validation.CrsBoundsValidator().check(p, gdf) is False


def test_crs_bounds_invalid():
    p = polygon.Polygon([(200, 0), (1, 0), (0, 1)])
    gdf = gpd.GeoDataFrame(
        geometry=[
            p,
        ],
        crs="EPSG:4326",
    )
    assert validation.CrsBoundsValidator().check(p, gdf) is False


def test_crs_bounds_valid():
    p = polygon.Polygon([(1, 0), (1, 0), (0, 1)])
    gdf = gpd.GeoDataFrame(
        geometry=[
            p,
        ],
        crs="EPSG:4326",
    )
    assert validation.CrsBoundsValidator().check(p, gdf) is True


def test_crs_bounds_no_crs_set():
    p = polygon.Polygon([(1, 0), (1, 0), (0, 1)])
    gdf = gpd.GeoDataFrame(
        geometry=[
            p,
        ],
    )
    assert validation.CrsBoundsValidator().check(p, gdf) is False


def test_crs_bounds_warning():
    p = polygon.Polygon([(200, 0), (1, 0), (0, 1)])
    gdf = gpd.GeoDataFrame(
        geometry=[
            p,
        ],
        crs="EPSG:4326",
    )
    with pytest.warns(UserWarning, match="Found geometries out of bounds from crs"):
        validation.CrsBoundsValidator().validate(gdf)


def test_self_intersecting_invalid(self_intersecting_geometry):
    assert (
        validation.SelfIntersectingValidator().check(
            geometry=self_intersecting_geometry
        )
        is False
    )


def test_self_intersecting_invalid(fixed_self_intersecting_geometry):
    assert (
        validation.SelfIntersectingValidator().check(
            geometry=fixed_self_intersecting_geometry
        )
        is True
    )


def test_self_intersecting_validator_fix(
    self_intersecting_geometry, fixed_self_intersecting_geometry
):
    assert (
        validation.SelfIntersectingValidator()
        .fix(geometry=self_intersecting_geometry)
        .equals(fixed_self_intersecting_geometry)
    )


def test_null_invalid():
    assert validation.NullValidator().check(geometry=None) is False
    assert validation.NullValidator().check(geometry=np.nan) is False


def test_null_valid():
    assert (
        validation.NullValidator().check(
            geometry=polygon.Polygon(([(0, 0), (1, 0), (1, 1), (0, 1)]))
        )
        is True
    )


def test_null_warning():
    gdf = gpd.GeoDataFrame(
        geometry=[None, np.nan],
        crs="EPSG:4326",
    )
    with pytest.warns(UserWarning, match="Found null geometries"):
        validation.NullValidator().validate(gdf)


def test_has_area():
    p = polygon.Polygon([(0, 0), (1, 0), (0, 1)])
    assert validation.AreaValidator().check(p) is True


def test_has_area_invalid():
    p = polygon.Polygon([(0, 1), (1, 0), (0, 1)])
    assert validation.AreaValidator().check(p) is False
