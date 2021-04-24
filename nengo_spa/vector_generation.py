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


class EquallySpacedPositiveUnitaryHrrVectors:
    """Generator for equally spaced positive unitary HRR vectors.

    The vectors produced by this generator lie all on the hyper-circle of
    positive, unitary vectors under the `.HrrAlgebra`. The distance from one
    vector to the next is constant.

    Note that the identity vector is included in the set of returned
    vectors if any of the vectors hits an offset of 0. This might not be desired
    as it will return any vector it is bound to unchanged. Use a non-integer
    *offset* to ensure that the identity vector is not included.

    Parameters
    ----------
    d : int
        Dimensionality of returned vectors.
    n : int
        Number of vectors to fit onto the hyper-circle. At most *n* vectors
        can be returned from the generator.
    offset : float
        Offset of the first returned vector along the hyper-circle. An offset
        of 0 will return the identity vector first. An offset of 1 corresponds
        to the vector when moving a 1/n-th part along the hyper-circle.

    Attributes
    ----------
    vectors : (n, d) ndarray
        All vectors that would be returned by iterating over the generator.
    """

    def __init__(self, *, d, n, offset):
        coefficient_count = (d + 1) // 2
        unity_roots = np.exp(
            2.0j
            * np.pi
            * np.arange(start=coefficient_count, stop=d % 2 - 1, step=-1)
            / coefficient_count
        )
        exponents_offset = coefficient_count / n * offset
        exponents = np.linspace(
            0 + exponents_offset,
            coefficient_count + exponents_offset,
            n,
            endpoint=False,
        )
        self.vectors = np.fft.irfft(unity_roots[None, :] ** exponents[:, None], n=d)

    def __iter__(self):
        return iter(self.vectors)


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
