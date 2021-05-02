import nengo
import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_equal

import nengo_spa as spa
from nengo_spa import sym
from nengo_spa.ast.symbolic import FixedScalar, PointerSymbol
from nengo_spa.types import TVocabulary


def test_product_of_scalars(Simulator, seed):
    with spa.Network(seed=seed) as model:
        stimulus = nengo.Node(0.5)
        a = spa.Scalar()
        b = spa.Scalar()
        nengo.Connection(stimulus, a.input)
        nengo.Connection(stimulus, b.input)
        x = a * b
        p = nengo.Probe(x.construct(), synapse=0.03)

    with Simulator(model) as sim:
        sim.run(0.5)

    assert_allclose(sim.data[p][sim.trange() > 0.3], 0.25, atol=0.2)


def test_unary_minus_on_scalar():
    assert (-FixedScalar(1.0)).evaluate() == -1.0


def test_pointer_symbol_network_creation(rng):
    vocab = spa.Vocabulary(16, pointer_gen=rng)
    vocab.populate("A")

    with spa.Network():
        A = PointerSymbol("A", TVocabulary(vocab))
        node = A.construct()
    assert_equal(node.output, vocab["A"].v)


@pytest.mark.parametrize("op", ["-", "~"])
def test_unary_operation_on_pointer_symbol(op, rng):
    vocab = spa.Vocabulary(16, pointer_gen=rng)
    vocab.populate("A")

    with spa.Network():
        x = eval(op + "PointerSymbol('A', TVocabulary(vocab))")
        node = x.construct()
    assert_equal(node.output, vocab.parse(op + "A").v)


@pytest.mark.parametrize("method", ["linv", "rinv", "normalized", "unitary"])
def test_unary_method_on_pointer_symbol(method, rng):
    vocab = spa.Vocabulary(16, pointer_gen=rng)
    vocab.populate("A")

    with spa.Network():
        x = eval("PointerSymbol('A', TVocabulary(vocab))." + method + "()")
        node = x.construct()
    assert_equal(node.output, vocab.parse("A." + method + "()").v)


@pytest.mark.parametrize("op", ["+", "-", "*"])
def test_binary_operation_on_pointer_symbols(op, rng):
    vocab = spa.Vocabulary(16, pointer_gen=rng)
    vocab.populate("A; B")

    with spa.Network():
        v = TVocabulary(vocab)  # noqa: F841
        x = eval("PointerSymbol('A', v)" + op + "PointerSymbol('B', v)")
        node = x.construct()
    assert_equal(node.output, vocab.parse("A" + op + "B").v)


@pytest.mark.parametrize("scalar", [3, np.float64(3)])
def test_pow_operation_on_pointer_symbols(scalar, rng):
    vocab = spa.Vocabulary(16, pointer_gen=rng)
    vocab.populate("A")

    with spa.Network():
        x = eval("PointerSymbol('A', TVocabulary(vocab)) ** scalar")
        node = x.construct()
    assert_equal(node.output, vocab.parse("A ** 3").v)


def test_pointer_symbol_mul_with_array():
    with pytest.raises(TypeError):
        PointerSymbol("X") * np.array([1, 2])


@pytest.mark.parametrize("op", ["+", "-"])
def test_additive_op_fixed_scalar_and_pointer_symbol(op, rng):
    vocab = spa.Vocabulary(16, pointer_gen=rng)
    vocab.populate("A")

    with spa.Network():
        with pytest.raises(TypeError):
            eval("2" + op + "PointerSymbol('A')")


@pytest.mark.parametrize("scalar", [2, np.float64(2)])
def test_multiply_fixed_scalar_and_pointer_symbol(scalar, rng):
    vocab = spa.Vocabulary(16, pointer_gen=rng)
    vocab.populate("A")

    with spa.Network():
        x = scalar * PointerSymbol("A", TVocabulary(vocab))
        node = x.construct()
    assert_equal(node.output, vocab.parse("2 * A").v)


@pytest.mark.parametrize("scalar", [2, np.float64(2)])
def test_divide_pointer_symbol_by_fixed_scalar(scalar, rng):
    vocab = spa.Vocabulary(16, pointer_gen=rng)
    vocab.populate("A")

    with spa.Network():
        x = PointerSymbol("A", TVocabulary(vocab)) / scalar
        node = x.construct()
    assert_equal(node.output, vocab.parse("0.5 * A").v)


def test_fixed_dot(rng):
    vocab = spa.Vocabulary(16, pointer_gen=rng)
    vocab.populate("A; B")

    v = TVocabulary(vocab)
    assert_allclose(
        spa.dot(PointerSymbol("A", v), PointerSymbol("A", v)).evaluate(), 1.0
    )
    assert spa.dot(PointerSymbol("A", v), PointerSymbol("B", v)).evaluate() <= 0.1


def test_fixed_dot_matmul(rng):
    vocab = spa.Vocabulary(16, pointer_gen=rng)
    vocab.populate("A; B")

    v = TVocabulary(vocab)  # noqa: F841
    assert_allclose(
        eval("PointerSymbol('A', v) @ PointerSymbol('A', v)").evaluate(), 1.0
    )


def test_translate(rng):
    v1 = spa.Vocabulary(16, pointer_gen=rng)
    v1.populate("A; B")
    v2 = spa.Vocabulary(16, pointer_gen=rng)
    v2.populate("A; B")

    assert_allclose(
        spa.translate(PointerSymbol("A", TVocabulary(v1)), v2).evaluate().dot(v2["A"]),
        1.0,
        atol=0.2,
    )


def test_reinterpret(rng):
    v1 = spa.Vocabulary(16, pointer_gen=rng)
    v1.populate("A; B")
    v2 = spa.Vocabulary(16, pointer_gen=rng)
    v2.populate("A; B")

    assert_equal(
        spa.reinterpret(PointerSymbol("A", TVocabulary(v1)), v2).evaluate().v, v1["A"].v
    )


def test_pointer_symbol_factory():
    ps = sym.A
    assert isinstance(ps, PointerSymbol)
    assert ps.expr == "A"


@pytest.mark.parametrize(
    "ps,expected",
    [
        (sym("A + B * C"), "(A+B*C)"),
        (sym.A + sym.B * sym.C, "A + B * C"),
        (sym("(A + B) * C"), "((A+B)*C)"),
        ((sym.A + sym.B) * sym.C, "(A + B) * C"),
    ],
)
def test_pointer_symbol_factory_expressions(ps, expected):
    assert isinstance(ps, PointerSymbol)
    assert ps.expr == expected
