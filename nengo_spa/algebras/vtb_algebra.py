import warnings

import nengo
import numpy as np

from nengo_spa.algebras.base import (
    AbstractAlgebra,
    CommonProperties,
    ElementSidedness,
    GenericSign,
)
from nengo_spa.networks.vtb import VTB


class VtbAlgebra(AbstractAlgebra):
    r"""Vector-derived Transformation Binding (VTB) algebra.

    VTB uses elementwise addition for superposition. The binding operation
    :math:`\mathcal{B}(x, y)` is defined as

    .. math::

       \mathcal{B}(x, y) := V_y x = \left[\begin{array}{ccc}
           V_y' &    0 &    0 \\
              0 & V_y' &    0 \\
              0 &    0 & V_y'
           \end{array}\right] x

    with

    .. math::

       V_y' = d^{\frac{1}{4}} \left[\begin{array}{cccc}
           y_1            & y_2            & \dots  & y_{d'}  \\
           y_{d' + 1}     & y_{d' + 2}     & \dots  & y_{2d'} \\
           \vdots         & \vdots         & \ddots & \vdots  \\
           y_{d - d' + 1} & y_{d - d' + 2} & \dots  & y_d
       \end{array}\right]

    and

    .. math:: d'^2 = d.

    The approximate inverse :math:`y^+` for :math:`y` is permuting the elements
    such that :math:`V_{y^+} = V_y^T`.

    Note that VTB requires the vector dimensionality to be square.

    The VTB binding operation is neither associative nor commutative.
    Furthermore, there are right inverses and identities only.
    By transposing the :math:`V_y` matrix, the closely related `.TvtbAlgebra`
    (Transposed VTB) algebra is obtained which does have two-sided identities
    and inverses.

    Additional information about VTB can be found in

    * `Gosmann, Jan, and Chris Eliasmith (2019). Vector-derived transformation binding:
      an improved binding operation for deep symbol-like processing in
      neural networks. Neural computation 31.5, 849-869.
      <https://direct.mit.edu/neco/article/31/5/849/8469/Vector-Derived-Transformation-Binding-An-Improved>`_
    * `Jan Gosmann (2018). An Integrated Model of Context, Short-Term, and
      Long-Term Memory. UWSpace. <https://uwspace.uwaterloo.ca/handle/10012/13498>`_

    .. seealso::
        `.TvtbAlgebra`
    """

    _instance = None

    def __new__(cls):
        if type(cls._instance) is not cls:
            cls._instance = super(VtbAlgebra, cls).__new__(cls)
        return cls._instance

    def is_valid_dimensionality(self, d):
        """Checks whether *d* is a valid vector dimensionality.

        For VTB all square numbers are valid dimensionalities.

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
        if d < 1:
            return False
        sub_d = np.sqrt(d)
        return sub_d * sub_d == d

    def _get_sub_d(self, d):
        sub_d = int(np.sqrt(d))
        if sub_d * sub_d != d:
            raise ValueError("Vector dimensionality must be a square number.")
        return sub_d

    def create_vector(self, d, properties, *, rng=None):
        """Create a vector fulfilling given properties in the algebra.

        Creating positive vectors requires SciPy.

        Parameters
        ----------
        d : int
            Vector dimensionality
        properties : set of str
            Definition of properties for the vector to fulfill. Valid set
            elements are constants defined in `.VtbProperties`.
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

        if {VtbProperties.UNITARY, VtbProperties.POSITIVE} <= properties:
            properties -= {VtbProperties.UNITARY, VtbProperties.POSITIVE}
            v = self.identity_element(d, sidedness=ElementSidedness.RIGHT)
            warnings.warn(
                "The only positive unitary vector in VTB is the identity. "
                "Use the identity directly to avoid this warning."
            )
        elif VtbProperties.UNITARY in properties:
            properties.remove(VtbProperties.UNITARY)
            v = self.make_unitary(rng.randn(d))
        elif VtbProperties.POSITIVE in properties:
            try:
                from scipy.linalg import sqrtm
            except ImportError as err:
                # From Python 3.6 onward we get a ModuleNotFoundError. We want
                # to re-raise the same type to be as specific as possible.
                raise type(err)(
                    "Creating positive VTB vectors requires SciPy to be available.",
                    name=err.name,
                    path=err.path,
                )

            properties.remove(VtbProperties.POSITIVE)
            sub_d = self._get_sub_d(d)
            v = rng.randn(d)
            v /= np.linalg.norm(v)
            mat = v.reshape((sub_d, sub_d))
            v = sqrtm(np.dot(mat, mat.T)).flatten()
        else:
            v = rng.randn(d)
            v /= np.linalg.norm(v)

        if len(properties) > 0:
            raise ValueError("Invalid properties: " + ", ".join(properties))

        return v

    def make_unitary(self, v):
        sub_d = self._get_sub_d(len(v))
        m = np.array(v.reshape((sub_d, sub_d)))
        for i in range(1, sub_d):
            y = -np.dot(m[:i, i:], m[i, i:])
            A = m[:i, :i]
            m[i, :i] = np.linalg.solve(A, y)
        m /= np.linalg.norm(m, axis=1)[:, None]
        m /= np.sqrt(sub_d)
        return m.flatten()

    def superpose(self, a, b):
        return a + b

    def bind(self, a, b):
        d = len(a)
        if len(b) != d:
            raise ValueError("Inputs must have same length.")
        m = self.get_binding_matrix(b)
        return np.dot(m, a)

    def invert(self, v, sidedness=ElementSidedness.TWO_SIDED):
        """Invert vector *v*.

        A vector bound to its inverse will result in the identity vector.

        VTB has a right inverse only.

        .. deprecated:: 1.2.0
           Calling this method with the default
           ``sidedness=ElementSidedness.TWO_SIDED`` returns the right inverse
           for backwards compatibility, but has been deprecated and will be
           removed in the next major release.

        Parameters
        ----------
        v : (d,) ndarray
            Vector to invert.
        sidedness : ElementSidedness
            Must be set to `ElementSidedness.RIGHT`.

        Returns
        -------
        (d,) ndarray
            Right inverse of vector.
        """
        if sidedness is ElementSidedness.LEFT:
            raise NotImplementedError("VtbAlgebra does not have a left inverse.")
        if sidedness is ElementSidedness.TWO_SIDED:
            warnings.warn(
                DeprecationWarning(
                    "VtbAlgebra does not have a two-sided inverse, returning "
                    "the right inverse instead. Please change your code to "
                    "request the right inverse explicitly with "
                    "`sidedness=ElementSidedness.RIGHT`."
                )
            )

        sub_d = self._get_sub_d(len(v))
        return v.reshape((sub_d, sub_d)).T.flatten()

    def binding_power(self, v, exponent):
        r"""Returns the binding power of *v* using the *exponent*.

        The binding power is defined as binding (*exponent*-1) times bindings
        of *v* to itself.

        Fractional binding powers are supported for "positive" vectors if SciPy
        is available.

        Note the following special exponents:

        * an exponent of -1 will return the inverse,
        * an exponent of 0 will return the identity vector,
        * and an *exponent* of 1 will return *v* itself.

        Be aware that the binding power for the VTB algebra does *not* satisfy
        the usual properties of exponentiation:

        * :math:`\mathcal{B}(v^a, v^b) = v^{a+b}` does *not* hold,
        * :math:`(v^a)^b = v^{ab}` does *not* hold.

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

        try:
            from scipy.linalg import fractional_matrix_power
        except ImportError as err:
            if int(exponent) == exponent:
                exponent = int(exponent)
                # Provide fallback for integer-only powers

                def fractional_matrix_power(m, exp):
                    power = np.eye(len(m))
                    for _ in range(exp):
                        power = np.dot(power, m)
                    return power

            else:
                # From Python 3.6 onward we get a ModuleNotFoundError. We want
                # to re-raise the same type to be as specific as possible.
                raise type(err)(
                    "Fractional VTB binding powers require SciPy to be available.",
                    name=err.name,
                    path=err.path,
                )

        if exponent == 0:
            return self.identity_element(len(v), sidedness=ElementSidedness.RIGHT)

        if int(exponent) != exponent and not self.sign(v).is_positive():
            raise ValueError(
                "Fractional binding powers are only supported for 'positive' vectors."
            )

        if exponent < 0:
            v = self.invert(v, sidedness=ElementSidedness.RIGHT)

        sub_d = self._get_sub_d(len(v))
        power = fractional_matrix_power(
            v.reshape((sub_d, sub_d)) * np.sqrt(sub_d), abs(exponent) - 1
        ).flatten() / np.sqrt(sub_d)
        assert np.allclose(power.imag, 0)

        return self.bind(v, power.real)

    def get_binding_matrix(self, v, swap_inputs=False):
        sub_d = self._get_sub_d(len(v))
        m = np.sqrt(sub_d) * np.kron(np.eye(sub_d), v.reshape((sub_d, sub_d)))
        if swap_inputs:
            m = np.dot(self.get_swapping_matrix(len(v)), m)
        return m

    def get_swapping_matrix(self, d):
        """Get matrix to swap operands in bound state.

        Parameters
        ----------
        d : int
            Dimensionality of vector.

        Returns
        -------
        (d, d) ndarry
            Matrix to multiply with a vector to switch left and right operand
            in bound state.
        """
        return self.get_inversion_matrix(d, sidedness=ElementSidedness.RIGHT)

    def get_inversion_matrix(self, d, sidedness=ElementSidedness.TWO_SIDED):
        """Returns the transformation matrix for inverting a vector.

        VTB has a right inverse only.

        .. deprecated:: 1.2.0
           Calling this method with the default
           ``sidedness=ElementSidedness.TWO_SIDED`` returns the right
           transformation matrix for the right inverse for backwards
           compatibility, but has been deprecated and will be removed in the
           next major release.

        Parameters
        ----------
        d : int
            Vector dimensionality.
        sidedness : ElementSidedness
            Must be set to `ElementSidedness.RIGHT`.

        Returns
        -------
        (d, d) ndarray
            Transformation matrix to invert a vector.
        """
        if sidedness is ElementSidedness.LEFT:
            raise NotImplementedError("VtbAlgebra does not have a left inverse.")
        if sidedness is ElementSidedness.TWO_SIDED:
            warnings.warn(
                DeprecationWarning(
                    "VtbAlgebra does not have a two-sided inverse, returning "
                    "the right inverse instead. Please change your code to "
                    "request the right inverse explicitly with "
                    "`sidedness=ElementSidedness.RIGHT`."
                )
            )

        sub_d = self._get_sub_d(d)
        return np.eye(d).reshape(d, sub_d, sub_d).T.reshape(d, d)

    def implement_superposition(self, n_neurons_per_d, d, n):
        node = nengo.Node(size_in=d)
        return node, n * (node,), node

    def implement_binding(self, n_neurons_per_d, d, unbind_left, unbind_right):
        net = VTB(n_neurons_per_d, d, unbind_left, unbind_right)
        return net, (net.input_left, net.input_right), net.output

    def sign(self, v):
        m = self.get_binding_matrix(v)
        if not np.allclose(m, m.T):
            return VtbSign(None)
        eigenvalues = np.linalg.eigvalsh(m)
        if np.all(eigenvalues > 0):
            return VtbSign(1)
        elif np.all(eigenvalues < 0):
            return VtbSign(-1)
        elif np.allclose(eigenvalues, 0):
            return VtbSign(0)
        else:
            return VtbSign(None)

    def abs(self, v):
        # No inverse of sign required because in VTB sign vectors are their
        # own inverse.
        return self.bind(v, self.sign(v).to_vector(len(v)))

    def absorbing_element(self, d, sidedness=ElementSidedness.TWO_SIDED):
        """VTB has no absorbing element except the zero vector.

        Always raises a `NotImplementedError`.
        """
        raise NotImplementedError("VtbAlgebra does not have any absorbing elements.")

    def identity_element(self, d, sidedness=ElementSidedness.TWO_SIDED):
        """Return the identity element of dimensionality *d*.

        VTB has a right identity only.

        .. deprecated:: 1.2.0
           Calling this method with the default
           ``sidedness=ElementSidedness.TWO_SIDED`` returns the right identity
           for backwards compatibility, but has been deprecated and will be
           removed in the next major release.

        Parameters
        ----------
        d : int
            Vector dimensionality.
        sidedness : ElementSidedness
            Must be set to `ElementSidedness.RIGHT`.

        Returns
        -------
        (d,) ndarray
            Right identity element.
        """
        if sidedness is ElementSidedness.LEFT:
            raise NotImplementedError("VtbAlgebra does not have a left identity.")
        if sidedness is ElementSidedness.TWO_SIDED:
            warnings.warn(
                DeprecationWarning(
                    "VtbAlgebra does not have a two-sided identity, returning "
                    "the right identity instead. Please change your code to "
                    "request the right identity explicitly with "
                    "`sidedness=ElementSidedness.RIGHT`."
                )
            )

        sub_d = self._get_sub_d(d)
        return (np.eye(sub_d) / d ** 0.25).flatten()

    def negative_identity_element(self, d, sidedness=ElementSidedness.TWO_SIDED):
        r"""Return the negative identity element of dimensionality *d*.

        VTB has a right negative identity only.

        Parameters
        ----------
        d : int
            Vector dimensionality.
        sidedness : ElementSidedness, optional
            Must be set to `ElementSidedness.RIGHT`.

        Returns
        -------
        (d,) ndarray
            Negative identity element.
        """
        if sidedness is not ElementSidedness.RIGHT:
            raise NotImplementedError("VTB only has a right negative identity.")
        return -self.identity_element(d, sidedness)

    def zero_element(self, d, sidedness=ElementSidedness.TWO_SIDED):
        """Return the zero element of dimensionality *d*.

        The zero element produces itself when bound to a different vector.
        For VTB this is the zero vector.

        Parameters
        ----------
        d : int
            Vector dimensionality.
        sidedness : ElementSidedness, optional
            This argument has no effect because the zero element of the VTB
            algebra is two-sided.

        Returns
        -------
        (d,) ndarray
            Zero element.
        """
        return np.zeros(d)


class VtbSign(GenericSign):
    """Represents a sign in the `.VtbAlgebra`.

    The sign depends on the symmetry and positive/negative definiteness of the
    binding matrix derived from the vector. For all non-symmetric matrices,
    the sign is indefinite. It is also indefenite, if the matrices eigenvalues
    have different signs. A symmetric, positive (negative) definite binding
    matrix corresponds to a positive (negative) sign (equivalent to all
    eigenvalues being greater than 0, respectively lower than 0). If all
    eigenvalues are equal to 0, the sign is also 0.
    """

    def to_vector(self, d):
        if self.sign is None:
            raise NotImplementedError(
                "There is no vector corresponding to an indefinite sign."
            )
        elif self.sign > 0:
            return VtbAlgebra().identity_element(d, sidedness=ElementSidedness.RIGHT)
        elif self.sign < 0:
            return VtbAlgebra().negative_identity_element(
                d, sidedness=ElementSidedness.RIGHT
            )
        elif self.sign == 0:
            return VtbAlgebra().zero_element(d)
        else:
            raise AssertionError(
                "Invalid value for sign, this code should be unreachable."
            )


class VtbProperties:
    """Vector properties supported by the `.VtbAlgebra`."""

    UNITARY = CommonProperties.UNITARY
    """A unitary vector does not change the length of a vector it is bound to."""

    POSITIVE = CommonProperties.POSITIVE
    """A positive vector does not change the sign of a vector it is bound to.

    A positive vector allows for fractional binding powers.
    """
