import numpy as np
import pytest

from nengo_spa.algebras.hrr_algebra import HrrAlgebra, HrrProperties, HrrSign
from nengo_spa.vector_generation import UnitLengthVectors


def test_is_singleton():
    assert HrrAlgebra() is HrrAlgebra()


@pytest.mark.parametrize(
    "sign,d",
    [
        (HrrSign(1, 0), 15),
        (HrrSign(-1, 0), 15),
        (HrrSign(1, 1), 16),
        (HrrSign(1, -1), 16),
        (HrrSign(-1, 1), 16),
        (HrrSign(-1, -1), 16),
    ],
)
def test_sign_and_abs(sign, d):
    algebra = HrrAlgebra()
    abs_v = algebra.abs(next(UnitLengthVectors(d)))
    v = algebra.bind(sign.to_vector(d), abs_v)
    assert algebra.sign(v) == sign
    assert np.allclose(algebra.abs(v), abs_v)


def test_create_positive_vector(rng):
    algebra = HrrAlgebra()
    v = algebra.create_vector(16, {HrrProperties.POSITIVE}, rng=rng)
    assert len(v) == 16
    assert algebra.sign(v).is_positive()


def test_create_unitary_vector(rng):
    algebra = HrrAlgebra()
    v = algebra.create_vector(16, {HrrProperties.UNITARY}, rng=rng)
    assert len(v) == 16
    assert np.allclose(algebra.make_unitary(v), v)


def test_create_positive_unitary_vector(rng):
    algebra = HrrAlgebra()
    v = algebra.create_vector(16, {HrrProperties.UNITARY, HrrProperties.POSITIVE})
    assert len(v) == 16
    assert algebra.sign(v).is_positive()
    assert np.allclose(algebra.make_unitary(v), v)


def test_create_vector_with_invalid_property():
    with pytest.raises(ValueError):
        HrrAlgebra().create_vector(16, "foo")


def test_additional_integer_binding_power_properties(rng):
    algebra = HrrAlgebra()
    v = algebra.create_vector(16, {HrrProperties.UNITARY}, rng=rng)

    assert np.allclose(
        algebra.bind(algebra.binding_power(v, 2), algebra.binding_power(v, 3)),
        algebra.binding_power(v, 5),
    )
    assert np.allclose(
        algebra.binding_power(algebra.binding_power(v, 2), 3),
        algebra.binding_power(v, 6),
    )

    assert np.allclose(
        algebra.bind(algebra.binding_power(v, 2), algebra.binding_power(v, -4)),
        algebra.binding_power(v, -2),
    )
    assert np.allclose(
        algebra.binding_power(algebra.binding_power(v, -2), 3),
        algebra.binding_power(v, -6),
    )


@pytest.mark.filterwarnings("ignore:.*only positive unitary vector")
def test_additional_fractional_binding_power_properties(rng):
    algebra = HrrAlgebra()
    v = algebra.create_vector(
        16, {HrrProperties.POSITIVE, HrrProperties.UNITARY}, rng=rng
    )

    assert np.allclose(
        algebra.bind(algebra.binding_power(v, 2.2), algebra.binding_power(v, 3.3)),
        algebra.binding_power(v, 5.5),
    )
    assert np.allclose(
        algebra.bind(algebra.binding_power(v, 2.2), algebra.binding_power(v, -4.4)),
        algebra.binding_power(v, -2.2),
    )

    v = algebra.create_vector(16, {HrrProperties.POSITIVE}, rng=rng)

    assert np.allclose(
        algebra.bind(algebra.binding_power(v, 2.2), algebra.binding_power(v, 3.3)),
        algebra.binding_power(v, 5.5),
    )


def test_fractional_binding_power_of_non_positive_vector_raises(rng):
    algebra = HrrAlgebra()
    v = algebra.bind(
        algebra.create_vector(16, {HrrProperties.POSITIVE}, rng=rng),
        HrrSign(-1, 1).to_vector(16),
    )
    assert algebra.sign(v).is_negative()
    with pytest.raises(ValueError):
        algebra.binding_power(v, 0.5)


class TestHrrSign:
    @pytest.mark.parametrize("sign", [HrrSign(1, 1), HrrSign(1, 0)])
    def test_positive(self, sign):
        assert sign.is_positive()
        assert not sign.is_negative()
        assert not sign.is_zero()
        assert not sign.is_indefinite()

    @pytest.mark.parametrize(
        "sign", [HrrSign(1, -1), HrrSign(-1, 1), HrrSign(-1, -1), HrrSign(-1, 0)]
    )
    def test_negative(self, sign):
        assert not sign.is_positive()
        assert sign.is_negative()
        assert not sign.is_zero()
        assert not sign.is_indefinite()

    def test_zero(self):
        sign = HrrSign(0, 0)
        assert not sign.is_positive()
        assert not sign.is_negative()
        assert sign.is_zero()
        assert not sign.is_indefinite()

    @pytest.mark.parametrize(
        "dc_sign, nyquist_sign", [(0, 1), (0, -1), (0.5, 0), (1, 2)]
    )
    def test_invalid(self, dc_sign, nyquist_sign):
        with pytest.raises(ValueError):
            HrrSign(dc_sign, nyquist_sign)

    @pytest.mark.parametrize(
        "sign,expected",
        [
            (HrrSign(0, 0), [0, 0, 0, 0]),
            (HrrSign(1, 1), [1, 0, 0, 0]),
            (HrrSign(1, 0), [1, 0, 0, 0]),
            (HrrSign(1, -1), [0, 1, 0, 0]),
            (HrrSign(-1, 1), [0, -1, 0, 0]),
            (HrrSign(-1, 0), [-1, 0, 0, 0]),
            (HrrSign(-1, -1), [-1, 0, 0, 0]),
            (HrrSign(0, 0), [0, 0, 0]),
            (HrrSign(1, 0), [1, 0, 0]),
            (HrrSign(-1, 0), [-1, 0, 0]),
        ],
    )
    def test_to_vector(self, sign, expected):
        assert HrrAlgebra().sign(expected) == sign  # sanity check
        assert np.allclose(sign.to_vector(len(expected)), expected)

    def test_equality(self):
        assert HrrSign(1, 1) == HrrSign(1, 1)
        assert HrrSign(-1, 1) == HrrSign(-1, 1)
        assert HrrSign(0, 0) == HrrSign(0, 0)
        assert HrrSign(1, -1) == HrrSign(1, -1)

        assert HrrSign(1, 1) != HrrSign(1, -1)
        assert HrrSign(1, 1) != HrrSign(0, 0)

        assert HrrSign(1, 1) != (1, 1)

    def test_repr(self):
        sign = HrrSign(-1, 1)
        assert eval(repr(sign)) == sign
