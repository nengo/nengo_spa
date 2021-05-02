import warnings
from abc import ABC, ABCMeta
from enum import Enum


class ElementSidedness(Enum):
    """The side in a binary operation for which a special element's properties hold."""

    LEFT = "left"
    RIGHT = "right"
    TWO_SIDED = "two-sided"


class _DuckTypedABCMeta(ABCMeta):
    def __instancecheck__(cls, instance):
        if super().__instancecheck__(instance):
            return True

        for member in dir(cls):
            if member.startswith("_"):
                continue
            if not hasattr(instance, member) or not hasattr(
                getattr(instance, member), "__self__"
            ):
                return False
        warnings.warn(
            DeprecationWarning(
                f"Please do not rely on pure duck-typing for {cls.__name__}. "
                f"Explicitly register your class {instance.__class__.__name__} "
                f"as a virtual subclass of {cls.__name__} or derive from it."
            )
        )
        return True


class AbstractAlgebra(metaclass=_DuckTypedABCMeta):
    """Abstract base class for algebras.

    Custom algebras can be defined by implementing the interface of this
    abstract base class.
    """

    def is_valid_dimensionality(self, d):
        """Checks whether *d* is a valid vector dimensionality.

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
        raise NotImplementedError()

    def create_vector(self, d, properties, *, rng=None):
        """Create a vector fulfilling given properties in the algebra.

        Valid properties and combinations thereof depend on the concrete
        algebra. It is suggested that the *properties* is either a *set* of
        *str* (if order does not matter) or a *list* of *str* (if order does
        matter). Use the constants defined in `.CommonProperties` where
        appropriate.

        Parameters
        ----------
        d : int
            Vector dimensionality
        properties
            Definition of properties for the vector to fulfill. Type and
            specification format depend on the concrete algbra, but it is
            suggested to use either a *set* or *list* of *str* (depending on
            whether order of properties matters) utilizing the constants defined
            in `.CommonProperties` where applicable.
        rng : numpy.random.RandomState, optional
            The random number generator to use to create the vector.

        Returns
        -------
        ndarray
            Random vector with desired properties.
        """
        raise NotImplementedError()

    def make_unitary(self, v):
        """Returns a unitary vector based on the vector *v*.

        A unitary vector does not change the length of a vector it is bound to.

        Parameters
        ----------
        v : (d,) ndarray
            Vector to base unitary vector on.

        Returns
        -------
        ndarray
            Unitary vector.
        """
        raise NotImplementedError()

    def superpose(self, a, b):
        """Returns the superposition of *a* and *b*.

        This is commonly elementwise addition.

        Parameters
        ----------
        a : (d,) ndarray
            Left operand in superposition.
        b : (d,) ndarray
            Right operand in superposition.

        Returns
        -------
        (d,) ndarray
            Superposed vector.
        """
        raise NotImplementedError()

    def bind(self, a, b):
        """Returns the binding of *a* and *b*.

        The resulting vector should in most cases be dissimilar to both inputs.

        Parameters
        ----------
        a : (d,) ndarray
            Left operand in binding.
        b : (d,) ndarray
            Right operand in binding.

        Returns
        -------
        (d,) ndarray
            Bound vector.
        """
        raise NotImplementedError()

    def binding_power(self, v, exponent):
        """Returns the binding power of *v* using the *exponent*.

        For a positive *exponent*, the binding power is defined as binding
        (*exponent*-1) times bindings of *v* to itself. For a negative
        *exponent*, the binding power is the approximate inverse bound to itself
        according to the prior definition. Depending on the algebra, fractional
        exponents might be valid or return a *ValueError*, if not. Usually, a
        fractional binding power will require that *v* has a positive sign.

        Note the following special exponents:

        * an exponent of -1 will return the approximate inverse,
        * an exponent of 0 will return the identity vector,
        * and an *exponent* of 1 will return *v* itself.

        The default implementation supports integer exponents only and will
        apply the `.bind` method multiple times. It requires the algebra to have
        a left identity.

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
        AbstractAlgebra.sign
        """

        if not int(exponent) == exponent:
            raise ValueError(
                "{} only supports integer binding powers.".format(
                    self.__class__.__name__
                )
            )
        exponent = int(exponent)

        power = self.identity_element(len(v), sidedness=ElementSidedness.LEFT)
        for _ in range(abs(exponent)):
            power = self.bind(power, v)

        if exponent < 0:
            power = self.invert(power)

        return power

    def invert(self, v, sidedness=ElementSidedness.TWO_SIDED):
        """Invert vector *v*.

        A vector bound to its inverse will result in the identity vector.

        Some algebras might not have an inverse only on specific sides. In that
        case a *NotImplementedError* may be raised for non-existing inverses.

        Parameters
        ----------
        v : (d,) ndarray
            Vector to invert.
        sidedness : ElementSidedness, optional
            Side in the binding operation on which the returned value acts as
            inverse.

        Returns
        -------
        (d,) ndarray
            Inverted vector.
        """
        raise NotImplementedError()

    def get_binding_matrix(self, v, swap_inputs=False):
        """Returns the transformation matrix for binding with a fixed vector.

        Parameters
        ----------
        v : (d,) ndarray
            Fixed vector to derive binding matrix for.
        swap_inputs : bool, optional
            By default the matrix will be such that *v* becomes the *right*
            operand in the binding. By setting *swap_inputs*, the matrix will
            be such that *v* becomes the *left* operand. For binding operations
            that are commutative (such as circular convolution), this has no
            effect.

        Returns
        -------
        (d, d) ndarray
            Transformation matrix to perform binding with *v*.
        """
        raise NotImplementedError()

    def get_inversion_matrix(self, d, sidedness=ElementSidedness.TWO_SIDED):
        """Returns the transformation matrix for inverting a vector.

        Some algebras might not have an inverse only on specific sides. In that
        case a *NotImplementedError* may be raised for non-existing inverses.

        Parameters
        ----------
        d : int
            Vector dimensionality (determines the matrix size).
        sidedness : ElementSidedness, optional
            Side in the binding operation on which a transformed vectors acts as
            inverse.

        Returns
        -------
        (d, d) ndarray
            Transformation matrix to invert a vector.
        """
        raise NotImplementedError()

    def implement_superposition(self, n_neurons_per_d, d, n):
        """Implement neural network for superposing vectors.

        Parameters
        ----------
        n_neurons_per_d : int
            Neurons to use per dimension.
        d : int
            Dimensionality of the vectors.
        n : int
            Number of vectors to superpose in the network.

        Returns
        -------
        tuple
            Tuple *(net, inputs, output)* where *net* is the implemented
            `nengo.Network`, *inputs* a sequence of length *n* of inputs to the
            network, and *output* the network output.
        """
        raise NotImplementedError()

    def implement_binding(self, n_neurons_per_d, d, unbind_left, unbind_right):
        """Implement neural network for binding vectors.

        Parameters
        ----------
        n_neurons_per_d : int
            Neurons to use per dimension.
        d : int
            Dimensionality of the vectors.
        unbind_left : bool
            Whether the left input should be unbound from the right input.
        unbind_right : bool
            Whether the right input should be unbound from the left input.

        Returns
        -------
        tuple
            Tuple *(net, inputs, output)* where *net* is the implemented
            `nengo.Network`, *inputs* a sequence of the left and the right
            input in that order, and *output* the network output.
        """
        raise NotImplementedError()

    def sign(self, v):
        """Returns the sign of *v* defined by the algebra.

        The exact definition of the sign depends on the concrete algebra, but
        should be analogous to the sign of a (complex) number in so far that
        binding two vectors with the same sign produces a "positive" vector.
        There might, however, be multiple types of negative signs, where binding
        vectors with different types of negative signs will produce another
        "negative" vector.

        Furthermore, if the algebra supports fractional binding powers, it
        should do so for all "non-negative" vectors, but not "negative" vectors.

        If an algebra does not have the notion of a sign, it may raise a
        :py:class:`NotImplementedError`.

        Parameters
        ----------
        v : (d,) ndarray
            Vector to determine sign of.

        Returns
        -------
        AbstractSign
            The sign of the input vector.

        See Also
        --------
        AbstractAlgebra.abs
        """
        raise NotImplementedError()

    def abs(self, v):
        """Returns the absolute vector of *v* defined by the algebra.

        The exact definition of "absolute vector" may depend on the concrete
        algebra. It should be a "positive" vector (see `.sign`) that relates
        to the input vector.

        The default implementation requires that the possible signs of the
        algebra correspond to actual vectors within the algebra. It will bind
        the inverse of the sign vector (from the left side) to the vector *v*.

        If an algebra does not have the notion of a sign or absolute vector,
        it may raise a :py:class:`NotImplementedError`.

        Parameters
        ----------
        v : (d,) ndarray
            Vector to obtain the absolute vector of.

        Returns
        -------
        (d,) ndarray
            The absolute vector relating to the input vector.
        """
        return self.bind(self.invert(self.sign(v).to_vector(len(v))), v)

    def absorbing_element(self, d, sidedness=ElementSidedness.TWO_SIDED):
        """Return the standard absorbing element of dimensionality *d*.

        An absorbing element will produce a scaled version of itself when bound
        to another vector. The standard absorbing element is the absorbing
        element with norm 1.

        Some algebras might not have an absorbing element other than the zero
        vector. In that case a *NotImplementedError* may be raised.

        Parameters
        ----------
        d : int
            Vector dimensionality.
        sidedness : ElementSidedness, optional
            Side in the binding operation on which the element absorbs.

        Returns
        -------
        (d,) ndarray
            Standard absorbing element.
        """
        raise NotImplementedError()

    def identity_element(self, d, sidedness=ElementSidedness.TWO_SIDED):
        """Return the identity element of dimensionality *d*.

        The identity does not change the vector it is bound to.

        Some algebras might not have an identity element. In that case a
        *NotImplementedError* may be raised.

        Parameters
        ----------
        d : int
            Vector dimensionality.
        sidedness : ElementSidedness, optional
            Side in the binding operation on which the element acts as identity.

        Returns
        -------
        (d,) ndarray
            Identity element.
        """
        raise NotImplementedError()

    def negative_identity_element(self, d, sidedness=ElementSidedness.TWO_SIDED):
        """Returns the negative identity element of dimensionality *d*.

        The negative identity only changes the sign of the vector it is bound to.

        Some algebras might not have a negative identity element (or even the
        notion of a sign). In that case a :py:class`NotImplementedError` may be
        raised.

        Parameters
        ----------
        d : int
            Vector dimensionality.
        sidedness : ElementSidedness, optional
            Side in the binding operation on which the element acts as negative
            identity.

        Returns
        -------
        (d,) ndarray
            Negative identity element.
        """
        raise NotImplementedError()

    def zero_element(self, d, sidedness=ElementSidedness.TWO_SIDED):
        """Return the zero element of dimensionality *d*.

        The zero element produces itself when bound to a different vector.
        Usually this will be the zero vector.

        Some algebras might not have a zero element. In that case a
        *NotImplementedError* may be raised.

        Parameters
        ----------
        d : int
            Vector dimensionality.
        sidedness : ElementSidedness, optional
            Side in the binding operation on which the element acts as zero.

        Returns
        -------
        (d,) ndarray
            Zero element.
        """
        raise NotImplementedError()


class AbstractSign(ABC):
    """Abstract base class for implementing signs for an algebra."""

    def is_positive(self):
        """Return whether the sign is positive."""
        raise NotImplementedError()

    def is_negative(self):
        """Return whether the sign is negative."""
        raise NotImplementedError()

    def is_zero(self):
        """Return whether the sign neither positive nor negative (i.e. zero),
        but definite."""
        return not (self.is_positive() or self.is_negative() or self.is_indefinite())

    def is_indefinite(self):
        """Return whether the sign is neither positive nor negative nor zero."""
        raise NotImplementedError()

    def to_vector(self, d):
        """Return the vector in the algebra corresponding to the sign.

        Parameters
        ----------
        d : int
            Vector dimensionality.

        Returns
        -------
        (d,) ndarray
            Vector corresponding to the sign.
        """
        raise NotImplementedError()


class GenericSign(AbstractSign):
    """A generic sign implementation.

    Parameters
    ----------
    sign : -1, 0, 1, None
        The represented sign. *None* is used for an indefinite sign.
    """

    def __init__(self, sign):
        if sign not in (-1, 0, 1, None):
            raise ValueError("sign must be one of -1, 0, 1, None")
        self.sign = sign

    def is_positive(self):
        return not self.is_indefinite() and self.sign > 0

    def is_negative(self):
        return not self.is_indefinite() and self.sign < 0

    def is_zero(self):
        return not self.is_indefinite() and self.sign == 0

    def is_indefinite(self):
        return self.sign is None

    def __repr__(self):
        return "{}(sign={})".format(self.__class__.__name__, self.sign)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.sign == other.sign


class CommonProperties:
    """Definition of constants for common properties of vectors in an algebra.

    Use these for best interoperability between algebras.
    """

    UNITARY = "unitary"
    """A unitary vector does not change the length of a vector it is bound to."""

    POSITIVE = "positive"
    """A positive vector does not change the sign of a vector it is bound to.

    A positive vector allows for fractional binding powers.
    """
