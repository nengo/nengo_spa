import sys

import nengo
from nengo.exceptions import ValidationError
import numpy as np
from numpy.testing import assert_equal
import pytest

import nengo_spa as spa
from nengo_spa.algebras.base import AbstractAlgebra
from nengo_spa.algebras.hrr_algebra import HrrAlgebra
from nengo_spa.algebras.vtb_algebra import VtbAlgebra
from nengo_spa.ast.symbolic import PointerSymbol
from nengo_spa.exceptions import SpaTypeError
from nengo_spa.semantic_pointer import AbsorbingElement, Identity, SemanticPointer, Zero
from nengo_spa.vector_generation import UnitaryVectors, UnitLengthVectors
from nengo_spa.testing import assert_sp_close
from nengo_spa.types import TVocabulary
from nengo_spa.vocabulary import Vocabulary


def test_init():
    a = SemanticPointer([1, 2, 3, 4])
    assert len(a) == 4

    a = SemanticPointer([1, 2, 3, 4, 5])
    assert len(a) == 5

    a = SemanticPointer(list(range(100)))
    assert len(a) == 100

    with pytest.raises(ValidationError):
        a = SemanticPointer(np.zeros((2, 2)))

    with pytest.raises(ValidationError):
        a = SemanticPointer(-1)
    with pytest.raises(ValidationError):
        a = SemanticPointer(0)
    with pytest.raises(ValidationError):
        a = SemanticPointer(1.7)
    with pytest.raises(ValidationError):
        a = SemanticPointer(None)
    with pytest.raises(TypeError):
        a = SemanticPointer(int)


def test_length(rng):
    a = SemanticPointer([1, 1])
    assert np.allclose(a.length(), np.sqrt(2))
    a = SemanticPointer(next(UnitLengthVectors(10, rng))) * 1.2
    assert np.allclose(a.length(), 1.2)


def test_normalized():
    a = SemanticPointer([1, 1]).normalized()
    b = a.normalized()
    assert a is not b
    assert np.allclose(b.length(), 1)


def test_normalized_zero():
    a = SemanticPointer([0, 0]).normalized()
    assert np.allclose(a.v, [0, 0])


@pytest.mark.parametrize("d", [64, 65, 100])
def test_make_unitary(algebra, d, rng):
    if not algebra.is_valid_dimensionality(d):
        return

    a = SemanticPointer(next(UnitLengthVectors(d, rng)), algebra=algebra)
    b = a.unitary()
    assert a is not b
    assert np.allclose(1, b.length())
    assert np.allclose(1, (b * b).length())
    assert np.allclose(1, (b * b * b).length())


def test_add_sub(algebra, rng):
    gen = UnitLengthVectors(10, rng)
    a = SemanticPointer(next(gen), algebra=algebra)
    b = SemanticPointer(next(gen), algebra=algebra)
    c = a.copy()
    d = b.copy()

    c += b
    d -= -a

    assert np.allclose((a + b).v, algebra.superpose(a.v, b.v))
    assert np.allclose((a + b).v, c.v)
    assert np.allclose((a + b).v, d.v)
    assert np.allclose((a + b).v, (a - (-b)).v)


@pytest.mark.parametrize("d", [64, 65])
def test_binding_and_inversion(algebra, d, rng):
    if not algebra.is_valid_dimensionality(d):
        return

    gen = UnitLengthVectors(d, rng)

    a = SemanticPointer(next(gen), algebra=algebra)
    b = SemanticPointer(next(gen), algebra=algebra)
    identity = Identity(d, algebra=algebra)

    c = a.copy()
    c *= b

    conv_ans = algebra.bind(a.v, b.v)

    assert np.allclose((a * b).v, conv_ans)
    assert np.allclose(a.bind(b).v, conv_ans)
    assert np.allclose(c.v, conv_ans)
    assert np.allclose((a * identity).v, a.v)
    assert (a * b * ~b).compare(a) > 0.6


def test_multiply():
    a = SemanticPointer(next(UnitLengthVectors(50)))

    assert np.allclose((a * 5).v, a.v * 5)
    assert np.allclose((5 * a).v, a.v * 5)
    assert np.allclose((a * 5.7).v, a.v * 5.7)
    assert np.allclose((5.7 * a).v, a.v * 5.7)
    assert np.allclose((0 * a).v, np.zeros(50))
    assert np.allclose((1 * a).v, a.v)

    with pytest.raises(Exception):
        a * None
    with pytest.raises(Exception):
        a * "string"
    with pytest.raises(TypeError):
        a * np.array([1, 2])


def test_compare(rng):
    gen = UnitLengthVectors(50, rng)
    a = SemanticPointer(next(gen)) * 10
    b = SemanticPointer(next(gen)) * 0.1

    assert a.compare(a) > 0.99
    assert a.compare(b) < 0.2
    assert np.allclose(a.compare(b), a.dot(b) / (a.length() * b.length()))


def test_dot(rng):
    gen = UnitLengthVectors(50, rng)
    a = SemanticPointer(next(gen)) * 1.1
    b = SemanticPointer(next(gen)) * (-1.5)
    assert np.allclose(a.dot(b), np.dot(a.v, b.v))
    assert np.allclose(a.dot(b.v), np.dot(a.v, b.v))
    assert np.allclose(a.dot(list(b.v)), np.dot(a.v, b.v))
    assert np.allclose(a.dot(tuple(b.v)), np.dot(a.v, b.v))


@pytest.mark.skipif(sys.version_info < (3, 5), reason="requires Python 3.5")
def test_dot_matmul(rng):
    gen = UnitLengthVectors(50, rng)
    a = SemanticPointer(next(gen)) * 1.1
    b = SemanticPointer(next(gen)) * (-1.5)
    assert np.allclose(eval("a @ b"), np.dot(a.v, b.v))


def test_distance(rng):
    gen = UnitLengthVectors(50, rng)
    a = SemanticPointer(next(gen))
    b = SemanticPointer(next(gen))
    assert a.distance(a) < 1e-5
    assert a.distance(b) > 0.7


def test_len():
    a = SemanticPointer(next(UnitLengthVectors(5)))
    assert len(a) == 5

    a = SemanticPointer(list(range(10)))
    assert len(a) == 10


def test_copy():
    a = SemanticPointer(next(UnitLengthVectors(5)))
    b = a.copy()
    assert a is not b
    assert a.v is not b.v
    assert np.allclose(a.v, b.v)
    assert a.algebra is b.algebra
    assert a.vocab is b.vocab
    assert a.name is b.name


def test_mse():
    gen = UnitLengthVectors(50)
    a = SemanticPointer(next(gen))
    b = SemanticPointer(next(gen))

    assert np.allclose(((a - b).length() ** 2) / 50, a.mse(b))


def test_binding_matrix(algebra, rng):
    gen = UnitLengthVectors(64, rng)
    a = SemanticPointer(next(gen), algebra=algebra)
    b = SemanticPointer(next(gen), algebra=algebra)

    m = b.get_binding_matrix()
    m_swapped = a.get_binding_matrix(swap_inputs=True)

    assert np.allclose((a * b).v, np.dot(m, a.v))
    assert np.allclose((a * b).v, np.dot(m_swapped, b.v))


@pytest.mark.parametrize("op", ("~a", "-a", "a+a", "a-a", "a*a", "2*a"))
def test_ops_preserve_vocab(op):
    v = Vocabulary(50)
    a = SemanticPointer(next(UnitLengthVectors(50)), vocab=v)  # noqa: F841
    x = eval(op)
    assert x.vocab is v


@pytest.mark.parametrize("op", ("a+b", "a-b", "a*b", "a.dot(b)", "a.compare(b)"))
def test_ops_check_vocab_compatibility(op):
    gen = UnitLengthVectors(50)
    a = SemanticPointer(next(gen), vocab=Vocabulary(50))  # noqa: F841
    b = SemanticPointer(next(gen), vocab=Vocabulary(50))  # noqa: F841
    with pytest.raises(SpaTypeError):
        eval(op)


@pytest.mark.parametrize("op", ("a+b", "a-b", "a*b", "a.dot(b)", "a.compare(b)"))
def test_none_vocab_is_always_compatible(op):
    gen = UnitLengthVectors(50)
    v = Vocabulary(50)
    a = SemanticPointer(next(gen), vocab=v)  # noqa: F841
    b = SemanticPointer(next(gen), vocab=None)  # noqa: F841
    eval(op)  # no assertion, just checking that no exception is raised


def test_fixed_pointer_network_creation(rng):
    with spa.Network():
        A = SemanticPointer(next(UnitLengthVectors(16)))
        node = A.construct()
    assert_equal(node.output, A.v)


@pytest.mark.parametrize("op", ["+", "-", "*"])
@pytest.mark.parametrize("order", ["AB", "BA"])
def test_binary_operation_on_fixed_pointer_with_pointer_symbol(
    Simulator, op, order, rng
):
    vocab = spa.Vocabulary(64, pointer_gen=rng)
    vocab.populate("A; B")
    a = PointerSymbol("A", TVocabulary(vocab))  # noqa: F841
    b = SemanticPointer(vocab["B"].v)  # noqa: F841

    with spa.Network() as model:
        if order == "AB":
            x = eval("a" + op + "b")
        elif order == "BA":
            x = eval("b" + op + "a")
        else:
            raise ValueError("Invalid order argument.")
        p = nengo.Probe(x.construct(), synapse=0.03)

    with Simulator(model) as sim:
        sim.run(0.5)

    assert_sp_close(
        sim.trange(), sim.data[p], vocab.parse(order[0] + op + order[1]), skip=0.3
    )


@pytest.mark.parametrize("op", ("+", "*"))
def test_incompatible_algebra(op):
    gen = UnitLengthVectors(32)
    a = SemanticPointer(next(gen), algebra=AbstractAlgebra())  # noqa: F841
    b = SemanticPointer(next(gen), algebra=AbstractAlgebra())  # noqa: F841
    with pytest.raises(TypeError):
        eval("a" + op + "b")


def test_invalid_algebra():
    gen = UnitLengthVectors(32)
    with pytest.raises(ValidationError, match="AbstractAlgebra"):
        SemanticPointer(next(gen), algebra=HrrAlgebra)
    SemanticPointer(next(gen), algebra=HrrAlgebra())


def test_identity(algebra):
    assert np.allclose(Identity(64, algebra=algebra).v, algebra.identity_element(64))


def test_absorbing_element(algebra, plt):
    plt.plot([0, 1], [0, 1])
    try:
        assert np.allclose(
            AbsorbingElement(64, algebra=algebra).v, algebra.absorbing_element(64)
        )
    except NotImplementedError:
        pass


def test_zero(algebra):
    assert np.allclose(Zero(64, algebra=algebra).v, algebra.zero_element(64))


def test_name():
    a = SemanticPointer(np.ones(4), name="a")
    b = SemanticPointer(np.ones(4), name="b")
    unnamed = SemanticPointer(np.ones(4), name=None)

    assert str(a) == "SemanticPointer<a>"
    assert repr(a) == (
        "SemanticPointer({!r}, vocab={!r}, algebra={!r}, name={!r}".format(
            a.v, a.vocab, a.algebra, a.name
        )
    )

    assert (-a).name == "-(a)"
    assert (~a).name == "~(a)"
    assert a.normalized().name == "(a).normalized()"
    assert a.unitary().name == "(a).unitary()"
    assert a.nondegenerate().name == "(a).nondegenerate()"
    assert (a + b).name == "(a)+(b)"
    assert (a * b).name == "(a)*(b)"
    assert (2.0 * a).name == "(2.0)*(a)"
    assert (a ** 3).name == "(a)**(3)"

    assert (a + unnamed).name is None
    assert (a * unnamed).name is None


@pytest.mark.parametrize("d", [1, 4, 9, 16, 129, 512])
def test_fractional_binding_properties(d, rng):
    # tests a number of properties of fractional binding with nondegenerate
    # vectors. these vectors don't strictly need to be unitary, but they
    # should still be generated somewhat carefully. it is recommended to
    # use both unitary + nondegenerate when possible.

    gen = UnitaryVectors(d, algebra=HrrAlgebra(), rng=rng)
    for _ in range(100):
        x = SemanticPointer(next(gen)).nondegenerate()
        x *= 1.1  # don't assume it's unitary

        # check that it's not unitary
        assert not np.allclose((x.unitary()).v, x.v)

        # check that making it nondegenerate again
        # does not change the vector
        assert np.allclose((x.nondegenerate()).v, x.v)

        # check that (sqrt(x))**2 == x
        assert np.allclose(((x ** 0.5) ** 2).v, x.v)

        # multiplication will add the exponents
        assert np.allclose((x ** 2 * x).v, (x ** 3).v)
        assert np.allclose((x ** 2.5 * x ** 1.5).v, (x * x * x * x).v)

        # check this more generally
        a, b, c = 10 * rng.rand(3) - 5  # [-5, 5]
        assert np.allclose((x ** a * x ** b * x ** c).v, (x ** (a + b + c)).v)

        # counter-intuitively, the property:
        #     (x**a)**b == x**(a*b)
        # does not hold in general -- e.g. (x**2)**(0.5) can be +/- x
        # that is because sqrt is a multi-valued function
        # assert np.allclose(((x**a)**b).v, (x**(a*b)).v)


@pytest.mark.parametrize("d", [1, 4, 9, 16, 129, 512])
def test_fractional_binding_unitary(d, rng):
    # tests a number of properties of fractional binding with nondegenerate
    # and unitary vectors

    gen = UnitaryVectors(d, algebra=HrrAlgebra(), rng=rng)
    for _ in range(100):
        x = SemanticPointer(next(gen)).nondegenerate()

        # check that making it nondegenerate or unitary again
        # does not change the vector
        assert np.allclose((x.nondegenerate()).v, x.v)
        assert np.allclose((x.unitary()).v, x.v)

        # 1/x is the inverse (since unitary)
        assert np.allclose((x ** (-1)).v, (~x).v)

        # x**0 gives the identity (since unitary)
        assert np.allclose((x ** 0).v, Identity(d).v)

        # check that it's still unitary after fractional binding
        sqrt_x = x ** 0.5
        x_check = sqrt_x * sqrt_x

        assert np.allclose(np.linalg.norm(sqrt_x.v), 1)
        assert np.allclose(np.linalg.norm(x_check.v), 1)
        assert np.allclose(x_check.v, x.v)


def test_degenerate():
    # tests that an error occurs if throwing away imag components
    # this error occurs regardless of whether it's unitary
    x = SemanticPointer([1, 2, 3, 4, 5, 6]).unitary()
    with pytest.raises(ValueError, match="nondegenerate"):
        x ** 0.5


def test_fractional_binding_natural():
    # tests fractional binding with natural exponents
    x = SemanticPointer([1, 2, 3, 4, 5, 6])

    assert np.allclose((x ** 1).v, x.v)
    assert np.allclose((x ** 2).v, (x * x).v)
    assert np.allclose((x ** 4).v, (x * x * x * x).v)

    # check that x is degenerate (i.e., not nondegenerate)
    assert not np.allclose(x.nondegenerate().v, x.v)


@pytest.mark.parametrize("d", [1, 4, 9, 144])
def test_fractional_binding_vtb(d, rng):
    pytest.importorskip("scipy")

    algebra = VtbAlgebra()
    v = next(UnitLengthVectors(d, rng=rng))
    x = SemanticPointer(v, algebra=algebra)

    # note: doesn't quite behave with ideal properties
    assert np.allclose((x ** 0).v, algebra.identity_element(d))
    assert np.allclose((x ** 1).v, (~x).v)
    assert np.allclose((x ** 2).v, (~x * x).v)
    assert np.allclose((x ** 3).v, (((~x) * x) * x).v)


@pytest.mark.parametrize("d", [1, 4, 9, 144])
def test_nondegenerate_vtb(d, rng):
    pytest.importorskip("scipy")

    algebra = VtbAlgebra()
    identity = Identity(d, algebra=algebra)
    v = next(UnitLengthVectors(d, rng=rng))
    x = SemanticPointer(v, algebra=algebra).nondegenerate()

    # nondegenerate VTB vectors are unitary
    assert np.allclose(algebra.make_unitary(x.v), x.v)

    # power of 0 gives the identity
    assert np.allclose((x ** 0).v, identity.v)

    # integer powers, positive and negative
    assert np.allclose((x ** 1).v, x.v)
    assert np.allclose((x ** 2).v, (x * x).v)
    assert np.allclose((x ** 3).v, (((x) * x) * x).v)
    assert np.allclose((x ** -1).v, (~x).v)
    assert np.allclose((x ** -2).v, (~x * ~x).v)
    assert np.allclose((x ** -3).v, (((~x) * ~x) * ~x).v)

    # fractional powers, positive and negative
    assert np.allclose((x ** 2.3).v, ((x ** 1.1) * (x ** 1.2)).v)
    assert np.allclose((x ** -2.3).v, ((x ** -1.1) * (x ** -1.2)).v)
    assert np.allclose((x ** 0.7).v, ((x ** -1.5) * (x ** 2.2)).v)
    assert np.allclose((x ** -1.3).v, ((x ** -1.5) * (x ** 0.2)).v)
    assert np.allclose((x ** 2.8).v, (((x ** 1.7) * (x ** -0.4)) * (x ** 1.5)).v)

    # adding of exponents in general
    a, b, c = 10 * rng.rand(3) - 5  # [-5, 5]
    assert np.allclose((x ** a * x ** b * x ** c).v, (x ** (a + b + c)).v)

    # repeated fractional binds do not decay the dot product
    step = x ** 0.1
    pt = step
    for _ in range(1, 100):
        pt = pt * step
    assert(np.allclose(np.dot(pt.v, (x ** 10).v), 1))
