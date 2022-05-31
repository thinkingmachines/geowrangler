import geopandas as gpd
import pytest
from shapely.geometry import multipolygon, polygon

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

    class TestValidator(validation.Validator):
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

    class TestValidator(validation.Validator):
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

    class TestValidator(validation.Validator):
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

    class TestValidator(validation.Validator):
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


def test_orientation_validator_invalid(misoriented_geometry):
    assert (
        validation.OrientationValidator().check(geometry=misoriented_geometry) is False
    )


def test_orientation_validator_valid(oriented_geometry):
    assert validation.OrientationValidator().check(geometry=oriented_geometry) is True


def test_orientation_validator_fix_invalid(misoriented_geometry, oriented_geometry):
    assert (
        validation.OrientationValidator()
        .fix(geometry=misoriented_geometry)
        .equals(oriented_geometry)
    )


def test_geometry_validation(oriented_geometry):
    gdf = gpd.GeoDataFrame(
        geometry=[
            oriented_geometry,
        ],
        crs="EPSG:4326",
    )
    validation.GeometryValidation(gdf).validate_all()


def test_geometry_validation_get_validators(oriented_geometry):
    gdf = gpd.GeoDataFrame(geometry=[oriented_geometry])
    validators = validation.GeometryValidation(gdf, ["orientation"])._get_validators()
    assert all(issubclass(v, validation.Validator) for v in validators)


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
