import nengo
import numpy as np

from nengo_spa.algebras.base import (
    AbstractAlgebra,
    AbstractSign,
    CommonProperties,
    ElementSidedness,
)
from nengo_spa.networks.circularconvolution import CircularConvolution


class HrrAlgebra(AbstractAlgebra):
    r"""Holographic Reduced Representations (HRRs) algebra.

    Uses element-wise addition for superposition, circular convolution for
    binding with an approximate inverse.

    The circular convolution :math:`c` of vectors :math:`a` and :math:`b`
    is given by

    .. math:: c[i] = \sum_j a[j] b[i - j]

    where negative indices on :math:`b` wrap around to the end of the vector.

    This computation can also be done in the Fourier domain,

    .. math:: c = DFT^{-1} ( DFT(a) \odot DFT(b) )

    where :math:`DFT` is the Discrete Fourier Transform operator, and
    :math:`DFT^{-1}` is its inverse.

    Circular convolution as a binding operation is associative, commutative,
    distributive.

    More information on circular convolution as a binding operation can be
    found in [plate2003]_.

    .. [plate2003] Plate, Tony A. Holographic Reduced Representation:
       Distributed Representation for Cognitive Structures. Stanford, CA: CSLI
       Publications, 2003.
    """

    _instance = None

    def __new__(cls):
        if type(cls._instance) is not cls:
            cls._instance = super(HrrAlgebra, cls).__new__(cls)
        return cls._instance

    def is_valid_dimensionality(self, d):
        """Checks whether *d* is a valid vector dimensionality.

        For circular convolution all positive numbers are valid
        dimensionalities.

        Parameters
        ----------
        d : int
            Dimensionality

        Returns
        -------
        bool
            *True*, if *d* is a valid vector dimensionality for the use with
            the algebra.
        """
        return d > 0

    def create_vector(self, d, properties, *, rng=None):
        """Create a vector fulfilling given properties in the algebra.

        Parameters
        ----------
        d : int
            Vector dimensionality
        properties : set of str
            Definition of properties for the vector to fulfill. Valid set
            elements are constants defined in `.HrrProperties`.
        rng : numpy.random.RandomState, optional
            The random number generator to use to create the vector.

        Returns
        -------
        ndarray
            Random vector with desired properties.
        """
        properties = set(properties)

        if rng is None:
            rng = np.random.RandomState()

        v = rng.randn(d)
        v /= np.linalg.norm(v)

        if HrrProperties.POSITIVE in properties:
            properties.remove(HrrProperties.POSITIVE)
            v = self.abs(v)

        if HrrProperties.UNITARY in properties:
            properties.remove(HrrProperties.UNITARY)
            v = self.make_unitary(v)

        if len(properties) > 0:
            raise ValueError("Invalid properties: " + ", ".join(properties))

        return v

    def make_unitary(self, v):
        fft_val = np.fft.fft(v)
        fft_imag = fft_val.imag
        fft_real = fft_val.real
        fft_norms = np.sqrt(fft_imag ** 2 + fft_real ** 2)
        invalid = fft_norms <= 0.0
        fft_val[invalid] = 1.0
        fft_norms[invalid] = 1.0
        fft_unit = fft_val / fft_norms
        return np.array((np.fft.ifft(fft_unit, n=len(v))).real)

    def superpose(self, a, b):
        return a + b

    def bind(self, a, b):
        n = len(a)
        if len(b) != n:
            raise ValueError("Inputs must have same length.")
        return np.fft.irfft(np.fft.rfft(a) * np.fft.rfft(b), n=n)

    def binding_power(self, v, exponent):
        r"""Returns the binding power of *v* using the *exponent*.

        The binding power is defined as binding (*exponent*-1) times bindings
        of *v* to itself. Fractional binding powers are supported.

        Note the following special exponents:

        * an exponent of -1 will return the approximate inverse,
        * an exponent of 0 will return the identity vector,
        * and an *exponent* of w1cne will return *v* itself.

        The following relations hold for integer exponents, and for unitary
        vectors:

        * :math:`v^a \circledast v^b = v^{a+b}`,
        * :math:`(v^a)^b = v^{ab}`.

        If :math:`a \geq 0` and :math:`b \geq 0`, then the first relation holds also
        for non-unitary vectors with real exponents.

        Parameters
        ----------
        v : (d,) ndarray
            Vector to bind repeatedly to itself.
        exponent : int or float
            Exponent of the binding power.

        Returns
        -------
        (d,) ndarray
            Binding power of *v*.

        See also
        --------
        .sign
        """
        if int(exponent) != exponent and not self.sign(v).is_positive():
            raise ValueError(
                "Fractional binding powers are only supported for 'positive' vectors."
            )
        if exponent < 0:
            v = self.invert(v)
        return np.fft.irfft(np.fft.rfft(v) ** abs(exponent), n=len(v))

    def invert(self, v, sidedness=ElementSidedness.TWO_SIDED):
        """Invert vector *v*.

        This turns circular convolution into circular correlation, meaning that
        ``A*B*~B`` is approximately ``A``.

        Examples
        --------
        For the vector ``[1, 2, 3, 4, 5]``, the inverse is ``[1, 5, 4, 3, 2]``.

        Parameters
        ----------
        v : (d,) ndarray
            Vector to invert.
        sidedness : ElementSidedness, optional
            This argument has no effect because the HRR algebra is commutative
            and the inverse is two-sided.

        Returns
        -------
        (d,) ndarray
            Inverted vector.
        """
        return v[-np.arange(len(v))]

    def get_binding_matrix(self, v, swap_inputs=False):
        D = len(v)
        T = []
        for i in range(D):
            T.append([v[(i - j) % D] for j in range(D)])
        return np.array(T)

    def get_inversion_matrix(self, d, sidedness=ElementSidedness.TWO_SIDED):
        """Returns the transformation matrix for inverting a vector.

        Parameters
        ----------
        d : int
            Vector dimensionality (determines the matrix size).
        sidedness : ElementSidedness, optional
            This argument has no effect because the HRR algebra is commutative
            and the inverse is two-sided.

        Returns
        -------
        (d, d) ndarray
            Transformation matrix to invert a vector.
        """
        return np.eye(d)[-np.arange(d)]

    def implement_superposition(self, n_neurons_per_d, d, n):
        node = nengo.Node(size_in=d)
        return node, n * (node,), node

    def implement_binding(self, n_neurons_per_d, d, unbind_left, unbind_right):
        net = CircularConvolution(n_neurons_per_d, d, unbind_left, unbind_right)
        return net, (net.input_a, net.input_b), net.output

    def sign(self, v):
        """Returns the HRR sign of *v*.

        See `AbstractAlgebra.sign` for general information on the notion of a
        sign for algbras, and `.HrrSign` for details specific to HRRs.

        Parameters
        ----------
        v : (d,) ndarray
            Vector to determine sign of.

        Returns
        -------
        HrrSign
            The sign of the input vector.
        """
        dc, nyquist = np.fft.rfft(v)[[0, -1]]
        if len(v) % 2 == 1:
            nyquist = 0
        assert np.isclose(dc.imag, 0) and np.isclose(nyquist.imag, 0)
        return HrrSign(int(np.sign(dc.real)), int(np.sign(nyquist.real)))

    def absorbing_element(self, d, sidedness=ElementSidedness.TWO_SIDED):
        r"""Return the standard absorbing element of dimensionality *d*.

        An absorbing element will produce a scaled version of itself when bound
        to another vector. The standard absorbing element is the absorbing
        element with norm 1.

        The absorbing element for circular convolution is the vector
        :math:`(1, 1, \dots, 1)^{\top} / \sqrt{d}`.

        Parameters
        ----------
        d : int
            Vector dimensionality.
        sidedness : ElementSidedness, optional
            This argument has no effect because the HRR algebra is commutative
            and the standard absorbing element is two-sided.

        Returns
        -------
        (d,) ndarray
            Standard absorbing element.
        """
        return np.ones(d) / np.sqrt(d)

    def identity_element(self, d, sidedness=ElementSidedness.TWO_SIDED):
        r"""Return the identity element of dimensionality *d*.

        The identity does not change the vector it is bound to.

        The identity element for circular convolution is the vector
        :math:`(1, 0, \dots, 0)^{\top}`.

        Parameters
        ----------
        d : int
            Vector dimensionality.
        sidedness : ElementSidedness, optional
            This argument has no effect because the HRR algebra is commutative
            and the identity is two-sided.

        Returns
        -------
        (d,) ndarray
            Identity element.
        """
        data = np.zeros(d)
        data[0] = 1.0
        return data

    def negative_identity_element(self, d, sidedness=ElementSidedness.TWO_SIDED):
        r"""Return the negative identity element of dimensionality *d*.

        The negative identity element for circular convolution is the vector
        :math:`(-1, 0, \dots, 0)^{\top}`.

        Parameters
        ----------
        d : int
            Vector dimensionality.
        sidedness : ElementSidedness, optional
            This argument has no effect because the HRR algebra is commutative
            and the identity is two-sided.

        Returns
        -------
        (d,) ndarray
            Negative identity element.
        """
        return -self.identity_element(d, sidedness)

    def zero_element(self, d, sidedness=ElementSidedness.TWO_SIDED):
        """Return the zero element of dimensionality *d*.

        The zero element produces itself when bound to a different vector.
        For circular convolution this is the zero vector.

        Parameters
        ----------
        d : int
            Vector dimensionality.
        sidedness : ElementSidedness, optional
            This argument has no effect because the HRR algebra is commutative
            and the zero element is two-sided.

        Returns
        -------
        (d,) ndarray
            Zero element.
        """
        return np.zeros(d)


class HrrSign(AbstractSign):
    r"""Represents a sign in the `.HrrAlgebra`.

    For odd dimensionalities, the sign is equal to the sign of the DC component
    of the Fourier representation of the vector. For even dimensionalities the
    sign is constituted out of the signs of the DC component and Nyquist
    frequency. Thus, for even dimensionalities, there is a total of four
    sub-signs excluding zero. The overall sign is considered positive if the
    DC component is positive and the Nyquist component is non-negative;
    the sign is considered negative if either component is negative; and
    the sign is considered zero if both are zero. Binding two Semantic Pointers
    with the same sub-sign will yield a positive Semantic Pointer. See the table
    below for details.

    .. table:: Resulting Semantic Pointer signs from HRR binding two Semantic
         Pointers. (Only the upper triangle is given as the matrix is
         symmetric.)

        ================== =========== ========== ========== ========== ======
        Sign (DC, Nyquist) \+ (+1, +1) − (+1, -1) − (-1, +1) − (−1, -1) (0, 0)
        ================== =========== ========== ========== ========== ======
        \+ (+1, +1)        \+ (+1, +1) − (+1, -1) − (−1, +1) − (−1, -1) (0, 0)
        − (+1, -1)                     \+ (1, +1) − (−1, -1) − (−1, +1) (0, 0)
        − (−1, +1)                                \+ (1, +1) − (+1, -1) (0, 0)
        − (−1, -1)                                           \+ (1, +1) (0, 0)
        (0, 0)                                                          (0, 0)
        ================== =========== ========== ========== ========== ======

    Parameters
    ----------
    dc_sign : int
        Sign of the DC component.
    nyquist_sign : int
        Sign of the Nyquist frequency component. Will be set to the *dc_sign*
        if zero.
    """

    __slots__ = ["dc_sign", "nyquist_sign"]

    def __init__(self, dc_sign, nyquist_sign):
        if dc_sign == 0 and nyquist_sign != 0:
            raise ValueError(
                "nyquist_sign must be 0 if dc_sign is 0 to constitute a valid "
                "sign in the HrrAlgebra."
            )
        if dc_sign not in (-1, 0, 1):
            raise ValueError("dc_sign must be one of -1, 0, 1")
        if nyquist_sign not in (-1, 0, 1):
            raise ValueError("nyquist_sign must be one of -1, 0, 1")

        self.dc_sign = dc_sign
        self.nyquist_sign = nyquist_sign
        if self.nyquist_sign == 0:
            self.nyquist_sign = self.dc_sign

    def is_positive(self):
        return self.dc_sign > 0 and self.nyquist_sign >= 0

    def is_negative(self):
        return self.dc_sign < 0 or self.nyquist_sign < 0

    def is_indefinite(self):
        return False

    def to_vector(self, d):
        """Return the vector in the algebra corresponding to the sign.

        =======  ============  =======================================
        DC sign  Nyquist sign  Vector
        =======  ============  =======================================
         1        1            [ 1,  0, 0, ...] (identity)
         1       -1            [ 0,  1, 0, 0, ...]
        -1        1            [ 0, -1, 0, ...]
        -1       -1            [-1,  0, 0, 0, ...] (negative identity)
         0        0            [ 0,  0, 0, ...] (zero)
        =======  ============  =======================================

        Parameters
        ----------
        d : int
            Vector dimensionality.

        Returns
        -------
        (d,) ndarray
            Vector corresponding to the sign.
        """
        if self.dc_sign == 0:
            return np.zeros(d)

        v = HrrAlgebra().identity_element(d)
        if self.dc_sign * self.nyquist_sign < 0:
            v = np.roll(v, 1)
        return self.dc_sign * v

    def __repr__(self):
        return "{}(dc_sign={}, nyquist_sign={})".format(
            self.__class__.__name__, self.dc_sign, self.nyquist_sign
        )

    def __eq__(self, other):
        if not isinstance(other, HrrSign):
            return False
        return self.dc_sign == other.dc_sign and self.nyquist_sign == other.nyquist_sign


class HrrProperties:
    """Vector properties supported by the `.HrrAlgebra`."""

    UNITARY = CommonProperties.UNITARY
    """A unitary vector does not change the length of a vector it is bound to."""

    POSITIVE = CommonProperties.POSITIVE
    """A positive vector does not change the sign of a vector it is bound to.

    A positive vector allows for fractional binding powers.
    """
