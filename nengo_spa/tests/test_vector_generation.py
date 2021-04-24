import numpy as np
import pytest

from nengo_spa.algebras import CommonProperties, HrrAlgebra
from nengo_spa.semantic_pointer import SemanticPointer
from nengo_spa.vector_generation import (
    AxisAlignedVectors,
    EquallySpacedPositiveUnitaryHrrVectors,
    ExpectedUnitLengthVectors,
    OrthonormalVectors,
    UnitaryVectors,
    UnitLengthVectors,
    VectorsWithProperties,
)


def test_axis_aligned_pointers():
    for i, p in enumerate(AxisAlignedVectors(5)):
        assert np.all(p == np.eye(5)[i])


def test_unit_length_pointers(rng):
    g = UnitLengthVectors(64, rng=rng)
    for i in range(10):
        assert np.allclose(np.linalg.norm(next(g)), 1.0)


def test_unitary_pointers(rng):
    algebra = HrrAlgebra()
    g = UnitaryVectors(64, algebra, rng=rng)
    a = SemanticPointer(next(g), algebra=algebra)
    b = SemanticPointer(next(g), algebra=algebra)
    c = SemanticPointer(next(g), algebra=algebra)
    assert np.allclose(a.compare(c), (a * b).compare(c * b))


@pytest.mark.parametrize(
    "constructor_kwargs,expected",
    [
        (dict(d=16, n=8, offset=0), np.eye(16)[::2]),
        (dict(d=16, n=8, offset=2), np.roll(np.eye(16)[::2], -2, axis=0)),
        (dict(d=16, n=8, offset=0.3), HrrAlgebra().binding_power(np.eye(16)[2], 0.3)),
        (dict(d=16, n=20, offset=1), None),
        (dict(d=9, n=9, offset=0), np.eye(9)),
        (dict(d=9, n=9, offset=2), np.roll(np.eye(9), -2, axis=0)),
        (dict(d=9, n=9, offset=0.3), HrrAlgebra().binding_power(np.eye(9)[1], 0.3)),
        (dict(d=9, n=20, offset=1), None),
    ],
)
def test_equally_spaced_positive_unitary_hrr_vectors(constructor_kwargs, expected):
    g = EquallySpacedPositiveUnitaryHrrVectors(**constructor_kwargs)

    assert np.all(
        np.array(list(g)) == g.vectors
    ), "Iterating should yield `vectors` property."
    assert len(g.vectors) == constructor_kwargs["n"], "Should produce `n` vectors."

    similarities = np.array(
        [
            np.dot(g.vectors[i], g.vectors[(i + 1) % len(g.vectors)])
            for i in range(len(g.vectors))
        ]
    )
    assert np.allclose(
        similarities, similarities[0]
    ), "Similarities of neighbouring pairs should all be the same."
    assert np.all(similarities < 1.0), "Vectors should not be the same."


def test_orthonormal_pointers(rng):
    g = OrthonormalVectors(32, rng=rng)
    vectors = np.array(list(g))
    assert len(vectors) == 32
    assert np.allclose(np.dot(vectors.T, vectors), np.eye(32))


def test_expected_unit_length_vectors(rng):
    g = ExpectedUnitLengthVectors(64, rng=rng)
    assert np.abs(np.mean([np.linalg.norm(next(g)) for i in range(50)]) - 1.0) < 0.1


def test_vectors_with_properties(rng):
    algebra = HrrAlgebra()
    g = VectorsWithProperties(
        64, {CommonProperties.POSITIVE, CommonProperties.UNITARY}, algebra, rng=rng
    )
    v = next(g)
    sqrt_v = algebra.binding_power(v, 0.5)
    assert np.allclose(v, algebra.bind(sqrt_v, sqrt_v))


@pytest.mark.parametrize(
    "vg",
    (
        AxisAlignedVectors,
        ExpectedUnitLengthVectors,
        OrthonormalVectors,
        UnitLengthVectors,
        lambda d: UnitaryVectors(d, algebra=HrrAlgebra()),
        lambda d: VectorsWithProperties(
            d, {CommonProperties.POSITIVE}, algebra=HrrAlgebra()
        ),
    ),
)
def test_instantiation_without_rng(vg):
    d = 64
    assert len(next(vg(d))) == d


@pytest.mark.parametrize(
    "vg",
    (
        AxisAlignedVectors,
        ExpectedUnitLengthVectors,
        OrthonormalVectors,
        UnitLengthVectors,
        lambda d: UnitaryVectors(d, algebra=HrrAlgebra()),
        lambda d: VectorsWithProperties(
            d, {CommonProperties.POSITIVE}, algebra=HrrAlgebra()
        ),
    ),
)
def test_iter(vg):
    d = 64
    x = vg(d)
    assert iter(x) is x
