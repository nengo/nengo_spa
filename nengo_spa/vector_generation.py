"""Generators to create vectors with specific properties."""

import numpy as np


def AxisAlignedVectors(d):
    """Generator for axis aligned vectors.

    Can yield at most *d* vectors.

    Note that while axis-aligned vectors can be useful for debugging,
    they will not work well with most binding methods for Semantic Pointers.

    Parameters
    ----------
    d : int
        Dimensionality of returned vectors.

    Examples
    --------
    >>> for p in nengo_spa.vector_generation.AxisAlignedVectors(4):
    ...    print(p)
    [1. 0. 0. 0.]
    [0. 1. 0. 0.]
    [0. 0. 1. 0.]
    [0. 0. 0. 1.]
    """
    for v in np.eye(d):
        yield v


class UnitLengthVectors:
    """Generator for uniformly distributed unit-length vectors.

    Parameters
    ----------
    d : int
        Dimensionality of returned vectors.
    rng : numpy.random.RandomState, optional
        The random number generator to use to create new vectors.
    """

    def __init__(self, d, rng=None):
        if rng is None:
            rng = np.random.RandomState()

        self.d = d
        self.rng = rng

    def __iter__(self):
        return self

    def __next__(self):
        v = self.rng.randn(self.d)
        v /= np.linalg.norm(v)
        return v

    def next(self):
        return self.__next__()


class UnitaryVectors:
    """Generator for unitary vectors (given some binding method).

    Parameters
    ----------
    d : int
        Dimensionality of returned vectors.
    algebra : AbstractAlgebra
        Algebra that defines what vectors are unitary.
    rng : numpy.random.RandomState, optional
        The random number generator to use to create new vectors.
    """

    def __init__(self, d, algebra, rng=None):
        if rng is None:
            rng = np.random.RandomState()

        self.d = d
        self.algebra = algebra
        self.rng = rng

    def __iter__(self):
        return self

    def __next__(self):
        return self.algebra.make_unitary(self.rng.randn(self.d))

    def next(self):
        return self.__next__()


class OrthonormalVectors:
    """Generator for random orthonormal vectors.

    Parameters
    ----------
    d : int
        Dimensionality of returned vectors.
    rng : numpy.random.RandomState, optional
        The random number generator to use to create new vectors.
    """

    def __init__(self, d, rng=None):
        if rng is None:
            rng = np.random.RandomState()

        self.d = d
        self.rng = rng
        self.vectors = []

    def __iter__(self):
        return self

    def __next__(self):
        v = self.rng.randn(self.d)
        i = len(self.vectors)
        if i >= self.d:
            raise StopIteration()
        elif i > 0:
            vectors = np.asarray(self.vectors)
            y = -np.dot(vectors[:, i:], v[i:])
            A = vectors[:i, :i]
            v[:i] = np.linalg.solve(A, y)
        v /= np.linalg.norm(v)
        self.vectors.append(v)
        return v

    def next(self):
        return self.__next__()


class ExpectedUnitLengthVectors:
    r"""Generator for vectors with expected unit-length.

    The vectors will be uniformly distributed with an expected norm
    of 1, but each specific pointer may have a length different than 1.
    Specifically each vector component will be normal distributed with mean 0
    and standard deviation :math:`1/\sqrt{d}`.

    Parameters
    ----------
    d : int
        Dimensionality of returned vectors.
    rng : numpy.random.RandomState, optional
        The random number generator to use to create new vectors.
    """

    def __init__(self, d, rng=None):
        if rng is None:
            rng = np.random.RandomState()

        self.d = d
        self.rng = rng

    def __iter__(self):
        return self

    def __next__(self):
        return self.rng.randn(self.d) / np.sqrt(self.d)

    def next(self):
        return self.__next__()


class VectorsWithProperties:
    """Generator for vectors with given properties.

    Supported properties depend on the algebra. See the respective algebra's
    :meth:`.AbstractAlgebra.create_vector` method.

    Parameters
    ----------
    d : int
        Dimensionality of returned vectors.
    properties
        Properties that the generated vectors have to fulfill. Details depend
        on the exact algebra.
    algebra : AbstractAlgebra
        Algebra that determines the interpretation of the properties.
    rng : numpy.random.RandomState, optional
        The random number generator to use to create new vectors.
    """

    def __init__(self, d, properties, algebra, *, rng=None):
        if rng is None:
            rng = np.random.RandomState()

        self.d = d
        self.properties = properties
        self.algebra = algebra
        self.rng = rng

    def __iter__(self):
        return self

    def __next__(self):
        return self.algebra.create_vector(self.d, self.properties, rng=self.rng)

    def next(self):
        return self.__next__()
