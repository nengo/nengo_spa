import re

import nengo
import numpy as np
import pytest
from nengo.exceptions import NengoWarning, ValidationError
from numpy.testing import assert_equal

import nengo_spa as spa
from nengo_spa.algebras.base import (
    AbstractAlgebra,
    CommonProperties,
    ElementSidedness,
    GenericSign,
)
from nengo_spa.algebras.hrr_algebra import HrrAlgebra, HrrSign
from nengo_spa.ast.symbolic import PointerSymbol
from nengo_spa.exceptions import SpaTypeError
from nengo_spa.semantic_pointer import (
    AbsorbingElement,
    Identity,
    NegativeIdentity,
    SemanticPointer,
    SemanticPointerSign,
    Zero,
)
from nengo_spa.testing import assert_sp_close
from nengo_spa.types import TVocabulary
from nengo_spa.vector_generation import (
    UnitaryVectors,
    UnitLengthVectors,
    VectorsWithProperties,
)
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
    a = SemanticPointer(next(UnitLengthVectors(10, rng=rng))) * 1.2
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

    a = SemanticPointer(next(UnitLengthVectors(d, rng=rng)), algebra=algebra)
    b = a.unitary()
    assert a is not b
    assert np.allclose(1, b.length())
    assert np.allclose(1, (b * b).length())
    assert np.allclose(1, (b * b * b).length())


def test_sign():
    a = Identity(16)
    sign = a.sign()
    assert isinstance(sign, SemanticPointerSign)
    assert sign.sign == HrrSign(1, 1)


def test_abs():
    neg_sp = NegativeIdentity(16)
    assert neg_sp.sign().is_negative()
    abs_sp = neg_sp.abs()
    assert abs_sp.sign().is_positive()
    assert np.allclose(abs_sp.v, Identity(16).v)


def test_add_sub(algebra, rng):
    gen = UnitLengthVectors(10, rng=rng)
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
def test_binding(algebra, d, rng):
    if not algebra.is_valid_dimensionality(d):
        return

    gen = UnitLengthVectors(d, rng=rng)

    a = SemanticPointer(next(gen), algebra=algebra)
    b = SemanticPointer(next(gen), algebra=algebra)

    c = a.copy()
    c *= b

    conv_ans = algebra.bind(a.v, b.v)

    assert np.allclose((a * b).v, conv_ans)
    assert np.allclose(a.bind(b).v, conv_ans)
    assert np.allclose(c.v, conv_ans)
    try:
        identity = Identity(d, algebra=algebra, sidedness=ElementSidedness.RIGHT)
        assert np.allclose((a * identity).v, a.v)
    except NotImplementedError:
        pass
    try:
        identity = Identity(d, algebra=algebra, sidedness=ElementSidedness.LEFT)
        assert np.allclose((identity * a).v, a.v)
    except NotImplementedError:
        pass


@pytest.mark.parametrize("d", [64, 65])
def test_integer_binding_power(algebra, d, rng):
    if not algebra.is_valid_dimensionality(d):
        return

    gen = UnitaryVectors(d, algebra, rng=rng)
    a = SemanticPointer(next(gen), algebra=algebra)

    assert np.allclose((a * a * a).v, (a ** 3).v)
    assert np.allclose((a * a * a).v, pow(a, 3).v)


@pytest.mark.parametrize("d", [64, 65])
def test_fractional_binding_power(algebra, d, rng):
    pytest.importorskip("scipy")

    if not algebra.is_valid_dimensionality(d):
        return

    gen = VectorsWithProperties(
        d, {CommonProperties.POSITIVE, CommonProperties.UNITARY}, algebra, rng=rng
    )
    a = SemanticPointer(next(gen), algebra=algebra)

    assert np.allclose(a.v, (((a ** 0.5) ** 2).v))
    assert np.allclose(a.v, (pow(a, 0.5) ** 2).v)


@pytest.mark.filterwarnings("ignore:.*sidedness:DeprecationWarning")
def test_inverse(algebra, rng):
    gen = UnitLengthVectors(64, rng=rng)
    a = SemanticPointer(next(gen), algebra=algebra)

    try:
        assert np.allclose(
            (~a).v, algebra.invert(a.v, sidedness=ElementSidedness.TWO_SIDED)
        )
    except NotImplementedError:
        pass

    try:
        assert np.allclose(
            a.linv().v, algebra.invert(a.v, sidedness=ElementSidedness.LEFT)
        )
    except NotImplementedError:
        pass

    try:
        assert np.allclose(
            a.rinv().v, algebra.invert(a.v, sidedness=ElementSidedness.RIGHT)
        )
    except NotImplementedError:
        pass


def test_multiply(rng):
    a = SemanticPointer(next(UnitLengthVectors(50, rng=rng)))

    assert np.allclose((a * 5).v, a.v * 5)
    assert np.allclose((5 * a).v, a.v * 5)
    assert np.allclose((a * 5.7).v, a.v * 5.7)
    assert np.allclose((5.7 * a).v, a.v * 5.7)
    assert np.allclose((0 * a).v, np.zeros(50))
    assert np.allclose((1 * a).v, a.v)

    numpy_scalar = np.float64(5.7)
    assert np.allclose((numpy_scalar * a).v, a.v * numpy_scalar)
    assert np.allclose((a * numpy_scalar).v, a.v * numpy_scalar)

    with pytest.raises(Exception):
        a * None
    with pytest.raises(Exception):
        a * "string"
    with pytest.raises(TypeError):
        a * np.array([1, 2])


def test_divide(rng):
    a = SemanticPointer(next(UnitLengthVectors(50, rng=rng)))

    assert np.allclose((a / 5).v, a.v / 5)
    assert np.allclose((a / 5.7).v, a.v / 5.7)
    assert np.allclose((a / np.float64(5.7)).v, a.v / 5.7)
    assert np.allclose((a / 1.0).v, a.v)

    with pytest.raises(ZeroDivisionError):
        a / 0
    with pytest.raises(TypeError):
        5 / a
    with pytest.raises(TypeError):
        a / None
    with pytest.raises(TypeError):
        a / np.ones(50)
    with pytest.raises(TypeError):
        a / SemanticPointer(next(UnitLengthVectors(50, rng=rng)))


def test_compare(rng):
    gen = UnitLengthVectors(50, rng=rng)
    a = SemanticPointer(next(gen)) * 10
    b = SemanticPointer(next(gen)) * 0.1

    assert a.compare(a) > 0.99
    assert a.compare(b) < 0.2
    assert np.allclose(a.compare(b), a.dot(b) / (a.length() * b.length()))


def test_dot(rng):
    gen = UnitLengthVectors(50, rng=rng)
    a = SemanticPointer(next(gen)) * 1.1
    b = SemanticPointer(next(gen)) * (-1.5)
    assert np.allclose(a.dot(b), np.dot(a.v, b.v))
    assert np.allclose(a.dot(b.v), np.dot(a.v, b.v))
    assert np.allclose(a.dot(list(b.v)), np.dot(a.v, b.v))
    assert np.allclose(a.dot(tuple(b.v)), np.dot(a.v, b.v))


def test_dot_matmul(rng):
    gen = UnitLengthVectors(50, rng=rng)
    a = SemanticPointer(next(gen)) * 1.1
    b = SemanticPointer(next(gen)) * (-1.5)
    assert np.allclose(eval("a @ b"), np.dot(a.v, b.v))


def test_distance(rng):
    gen = UnitLengthVectors(50, rng=rng)
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


def test_mse(rng):
    gen = UnitLengthVectors(50, rng=rng)
    a = SemanticPointer(next(gen))
    b = SemanticPointer(next(gen))

    assert np.allclose(((a - b).length() ** 2) / 50, a.mse(b))


def test_binding_matrix(algebra, rng):
    gen = UnitLengthVectors(64, rng=rng)
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


def test_fixed_pointer_network_creation():
    with spa.Network():
        A = SemanticPointer(next(UnitLengthVectors(16)))
        node = A.construct()
    assert_equal(node.output, A.v)


@pytest.mark.parametrize("op", ["+", "-", "*"])
@pytest.mark.parametrize("order", [("A", "B"), ("B", "A")])
def test_binary_operation_on_fixed_pointer_with_pointer_symbol(
    Simulator, op, order, seed, rng
):
    vocab = spa.Vocabulary(64, pointer_gen=rng)
    vocab.populate("A; B")
    a = PointerSymbol("A", TVocabulary(vocab))  # noqa: F841
    b = SemanticPointer(vocab["B"].v)  # noqa: F841

    with spa.Network(seed=seed) as model:
        if order == ("A", "B"):
            x = eval("a" + op + "b")
        elif order == ("B", "A"):
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


@pytest.mark.filterwarnings("ignore:.*:DeprecationWarning")
@pytest.mark.parametrize("sidedness", ElementSidedness)
def test_identity(algebra, sidedness):
    try:
        assert np.allclose(
            Identity(64, algebra=algebra, sidedness=sidedness).v,
            algebra.identity_element(64, sidedness=sidedness),
        )
    except NotImplementedError:
        pass


@pytest.mark.filterwarnings("ignore:.*:DeprecationWarning")
@pytest.mark.parametrize("sidedness", ElementSidedness)
def test_absorbing_element(algebra, sidedness, plt):
    plt.plot([0, 1], [0, 1])
    try:
        assert np.allclose(
            AbsorbingElement(64, algebra=algebra, sidedness=sidedness).v,
            algebra.absorbing_element(64, sidedness=sidedness),
        )
    except NotImplementedError:
        pass


@pytest.mark.filterwarnings("ignore:.*:DeprecationWarning")
@pytest.mark.parametrize("sidedness", ElementSidedness)
def test_zero(algebra, sidedness):
    try:
        assert np.allclose(
            Zero(64, algebra=algebra, sidedness=sidedness).v,
            algebra.zero_element(64, sidedness=sidedness),
        )
    except NotImplementedError:
        pass


def test_name():
    a = SemanticPointer(np.ones(4), name="a")
    b = SemanticPointer(np.ones(4), name="b")
    unnamed = SemanticPointer(np.ones(4), name=None)

    assert str(a) == "SemanticPointer<a>"
    assert repr(a) == (
        f"SemanticPointer({a.v!r}, vocab={a.vocab!r}, algebra={a.algebra!r}, "
        f"name={a.name!r}"
    )

    assert (-a).name == "-a"
    assert (~a).name == "~a"
    assert a.normalized().name == "a.normalized()"
    assert a.unitary().name == "a.unitary()"
    assert a.sign().to_semantic_pointer().name == "a.sign().to_semantic_pointer()"
    assert a.abs().name == "a.abs()"
    assert (a + b).name == "a + b"
    assert (a * b).name == "a * b"
    assert (a ** 2).name == "a ** 2"
    assert (2.0 * a).name == "2.0 * a"
    assert (a / 2.0).name == "a / 2.0"

    assert (a + unnamed).name is None
    assert (a * unnamed).name is None

    # check that names that blow up exponentially in length are truncated
    for i in range(10):
        a += a * b
    assert len(a.name) <= a.MAX_NAME
    assert a.name.startswith("a + a * b + (a + a * b) * b")
    assert a.name.endswith("...")


def test_translate(rng):
    v1 = spa.Vocabulary(16, pointer_gen=rng)
    v1.populate("A; B")
    v2 = spa.Vocabulary(16, pointer_gen=rng)
    v2.populate("A; B")
    v3 = spa.Vocabulary(16, pointer_gen=rng)
    v3.populate("B")

    a1 = v1.parse("A")
    assert isinstance(a1, SemanticPointer)

    assert np.allclose(a1.translate(v2).dot(v2["A"]), 1.0, atol=0.2)
    assert np.allclose(a1.translate(v2, keys=["A"]).dot(v2["A"]), 1.0, atol=0.2)
    assert not np.allclose(a1.translate(v2, keys=["B"]).dot(v2["A"]), 1.0, atol=0.2)

    with pytest.warns(NengoWarning, match="source vocabulary has keys not existent"):
        a1.translate(v3)
    assert np.allclose(a1.translate(v3, populate=True).dot(v3["A"]), 1.0, atol=0.2)


class TestSemanticPointerSign:
    class DummySign(GenericSign):
        def to_vector(self, d):
            return np.ones(d)

    @pytest.mark.parametrize(
        "sign,method,expected",
        [
            (1, "is_positive", True),
            (-1, "is_negative", True),
            (0, "is_zero", True),
            (None, "is_indefinite", True),
            (0, "is_positive", False),
            (0, "is_negative", False),
            (1, "is_zero", False),
            (0, "is_indefinite", False),
        ],
    )
    def test_proxies_underlying_sign_methods(self, sign, method, expected):
        sp_sign = SemanticPointerSign(GenericSign(sign), vocab=Vocabulary(16))
        assert getattr(sp_sign, method)() == expected

    def test_proxies_underlying_to_vector_method(self):
        sp_sign = SemanticPointerSign(
            TestSemanticPointerSign.DummySign(1), vocab=Vocabulary(16)
        )
        assert np.allclose(sp_sign.to_vector(16), np.ones(16))

    def test_equality(self):
        with pytest.raises(NotImplementedError):
            SemanticPointerSign(
                GenericSign(1), vocab=Vocabulary(16)
            ) == SemanticPointerSign(GenericSign(1), vocab=Vocabulary(16))

    def test_repr(self):
        assert re.match(
            r"SemanticPointerSign\(GenericSign\(sign=1\), algebra=None, "
            r"dimensions=16, vocab=\<.*\>, name=None\)",
            repr(SemanticPointerSign(GenericSign(1), vocab=Vocabulary(16), name=None)),
        )

    def test_to_semantic_pointer_with_vocab(self):
        vocab = Vocabulary(16)
        sp_sign = SemanticPointerSign(
            TestSemanticPointerSign.DummySign(1), vocab=vocab, name="a"
        )
        sp = sp_sign.to_semantic_pointer()
        assert np.allclose(sp.v, np.ones(16))
        assert sp.vocab is vocab

    def test_to_semantic_pointer_with_algebra(self):
        algebra = HrrAlgebra()
        sp_sign = SemanticPointerSign(
            TestSemanticPointerSign.DummySign(1),
            dimensions=16,
            algebra=algebra,
            name="a",
        )
        sp = sp_sign.to_semantic_pointer()
        assert np.allclose(sp.v, np.ones(16))
        assert sp.algebra is algebra

    def test_to_semantic_pointer_without_name(self):
        algebra = HrrAlgebra()
        sp_sign = SemanticPointerSign(
            TestSemanticPointerSign.DummySign(1),
            dimensions=16,
            algebra=algebra,
        )
        sp_sign.to_semantic_pointer()  # should not throw
