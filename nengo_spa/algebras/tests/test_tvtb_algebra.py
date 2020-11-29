import numpy as np
import pytest

from nengo_spa.algebras.tvtb_algebra import TvtbAlgebra, TvtbProperties, TvtbSign


def test_is_singleton():
    assert TvtbAlgebra() is TvtbAlgebra()


def test_is_valid_dimensionality():
    assert not TvtbAlgebra().is_valid_dimensionality(-1)
    assert not TvtbAlgebra().is_valid_dimensionality(0)
    assert not TvtbAlgebra().is_valid_dimensionality(15)
    assert not TvtbAlgebra().is_valid_dimensionality(24)
    assert TvtbAlgebra().is_valid_dimensionality(1)
    assert TvtbAlgebra().is_valid_dimensionality(16)
    assert TvtbAlgebra().is_valid_dimensionality(25)


@pytest.mark.parametrize(
    "sign",
    [TvtbSign(-1), TvtbSign(1)],
)
def test_sign_and_abs(sign):
    pytest.importorskip("scipy")
    d = 16
    algebra = TvtbAlgebra()
    abs_v = algebra.create_vector(d, {TvtbProperties.POSITIVE})
    v = algebra.bind(sign.to_vector(d), abs_v)
    assert algebra.sign(v) == sign
    assert np.allclose(algebra.abs(v), abs_v)


def test_create_positive_vector(rng):
    pytest.importorskip("scipy")
    algebra = TvtbAlgebra()
    v = algebra.create_vector(16, {TvtbProperties.POSITIVE}, rng=rng)
    assert len(v) == 16
    assert algebra.sign(v).is_positive()


def test_create_unitary_vector(rng):
    algebra = TvtbAlgebra()
    v = algebra.create_vector(16, {TvtbProperties.UNITARY}, rng=rng)
    assert len(v) == 16
    assert np.allclose(algebra.make_unitary(v), v)


@pytest.mark.filterwarnings("ignore:.*only positive unitary vector")
def test_create_positive_unitary_vector(rng):
    algebra = TvtbAlgebra()
    v = algebra.create_vector(16, {TvtbProperties.UNITARY, TvtbProperties.POSITIVE})
    assert len(v) == 16
    assert algebra.sign(v).is_positive()
    assert np.allclose(algebra.make_unitary(v), v)


def test_create_vector_with_invalid_property():
    with pytest.raises(ValueError):
        TvtbAlgebra().create_vector(16, "foo")
