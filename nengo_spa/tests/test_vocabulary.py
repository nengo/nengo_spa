# -*- coding: utf-8 -*-

import nengo.solvers
import numpy as np
import pytest
from nengo.exceptions import NengoWarning, ValidationError
from numpy.testing import assert_equal

from nengo_spa import SemanticPointer, Vocabulary
from nengo_spa.algebras import HrrAlgebra, VtbAlgebra
from nengo_spa.exceptions import SpaParseError
from nengo_spa.vector_generation import AxisAlignedVectors
from nengo_spa.vocabulary import (
    VocabularyMap,
    VocabularyMapParam,
    VocabularyOrDimParam,
    special_sps,
)


def test_add(rng):
    v = Vocabulary(3, pointer_gen=rng)
    v.add("A", [1, 2, 3])
    v.add("B", [4, 5, 6])
    v.add("C", [7, 8, 9])
    assert np.allclose(v.vectors, [[1, 2, 3], [4, 5, 6], [7, 8, 9]])


def test_add_raises_exception_for_algebra_mismatch():
    v = Vocabulary(4, algebra=HrrAlgebra())
    with pytest.raises(ValidationError, match="different vocabulary or algebra"):
        v.add("V", SemanticPointer(np.ones(4), algebra=VtbAlgebra()))
    v.add("V", SemanticPointer(np.ones(4), algebra=VtbAlgebra()).reinterpret(v))


def test_added_algebra_match(rng):
    v = Vocabulary(4, algebra=VtbAlgebra(), pointer_gen=rng)
    sp = v.create_pointer()
    assert sp.algebra is VtbAlgebra()
    v.add("V", sp)
    assert v["V"].vocab is v
    assert v["V"].algebra is VtbAlgebra()
    assert v["V"].name == "V"


def test_populate(rng):
    v = Vocabulary(64, pointer_gen=rng)

    v.populate("")
    v.populate(" \r\n\t")
    assert len(v) == 0

    v.populate("A")
    assert "A" in v

    v.populate("B; C")
    assert "B" in v
    assert "C" in v

    v.populate("D.unitary()")
    assert "D" in v
    np.testing.assert_almost_equal(np.linalg.norm(v["D"].v), 1.0)
    np.testing.assert_almost_equal(np.linalg.norm((v["D"] * v["D"]).v), 1.0)

    v.populate("E = A + 2 * B")
    assert np.allclose(v["E"].v, v.parse("A + 2 * B").v)
    assert np.linalg.norm(v["E"].v) > 2.0

    v.populate("F = (A + 2 * B).normalized()")
    assert np.allclose(v["F"].v, v.parse("A + 2 * B").normalized().v)
    np.testing.assert_almost_equal(np.linalg.norm(v["F"].v), 1.0)

    v.populate("Positive.abs()")
    assert v["Positive"].sign().is_positive()

    v.populate("G = A; H")
    assert np.allclose(v["G"].v, v["A"].v)
    assert "H" in v

    # Assigning non-existing pointer
    with pytest.raises(NameError):
        v.populate("I = J")

    # Redefining
    with pytest.raises(ValidationError):
        v.populate("H = A")

    # Calling non existing function
    with pytest.raises(AttributeError):
        v.populate("I = H.invalid()")

    # invalid names: lowercase, unicode
    with pytest.raises(SpaParseError):
        v.populate("x = A")
    with pytest.raises(SpaParseError):
        v.populate(u"Aα = A")


def test_pointer_gen():
    v = Vocabulary(32, pointer_gen=AxisAlignedVectors(32))
    v.populate("A; B; C")
    assert np.all(v.vectors == np.eye(32)[:3])


@pytest.mark.parametrize("pointer_gen", ("string", 123))
def test_invalid_pointer_gen(pointer_gen):
    with pytest.raises(ValidationError):
        Vocabulary(32, pointer_gen=pointer_gen)


@pytest.mark.parametrize(
    "name", ("None", "True", "False", "Zero", "AbsorbingElement", "Identity")
)
def test_reserved_names(name):
    v = Vocabulary(16)
    with pytest.raises(SpaParseError):
        v.populate(name)


@pytest.mark.parametrize("name,sp", sorted(special_sps.items()))
def test_special_sps(name, sp, rng):
    v = Vocabulary(16, pointer_gen=rng)
    assert name in v
    assert np.allclose(v[name].v, sp(16).v)
    assert np.allclose(v.parse(name).v, sp(16).v)


def test_populate_with_transform_on_first_vector(rng):
    v = Vocabulary(64, pointer_gen=rng)

    v.populate("A.unitary()")
    assert "A" in v
    assert np.allclose(v["A"].v, v["A"].unitary().v)


def test_populate_with_transform_on_nonstrict_vocab(rng):
    v = Vocabulary(64, pointer_gen=rng, strict=False)

    v.populate("A.unitary()")
    assert "A" in v
    assert np.allclose(v["A"].v, v["A"].unitary().v)


def test_parse(rng):
    v = Vocabulary(64, pointer_gen=rng)
    v.populate("A; B; C")
    A = v.parse("A")
    B = v.parse("B")
    C = v.parse("C")
    assert np.allclose((A * B).v, v.parse("A * B").v)
    assert np.allclose((A * ~B).v, v.parse("A * ~B").v)
    assert np.allclose((A + B).v, v.parse("A + B").v)
    assert np.allclose((A - (B * C) * 3 + ~C).v, v.parse("A-(B*C)*3+~C").v)

    assert np.allclose(v.parse("0").v, np.zeros(64))
    assert np.allclose(v.parse("1").v, np.eye(64)[0])
    assert np.allclose(v.parse("1.7").v, np.eye(64)[0] * 1.7)

    with pytest.raises(SyntaxError):
        v.parse("A((")
    with pytest.raises(SpaParseError):
        v.parse('"hello"')
    with pytest.raises(SpaParseError):
        v.parse('"hello"')


def test_parse_n(rng):
    v = Vocabulary(64, pointer_gen=rng)
    v.populate("A; B; C")
    A = v.parse("A")
    B = v.parse("B")

    parsed = v.parse_n("A", "A*B", "A+B", "3")
    assert np.allclose(parsed[0].v, A.v)
    assert np.allclose(parsed[1].v, (A * B).v)
    assert np.allclose(parsed[2].v, (A + B).v)
    # FIXME should give an exception?
    assert np.allclose(parsed[3].v, 3 * v["Identity"].v)


def test_invalid_dimensions():
    with pytest.raises(ValidationError):
        Vocabulary(1.5)
    with pytest.raises(ValidationError):
        Vocabulary(0)
    with pytest.raises(ValidationError):
        Vocabulary(-1)


def test_capital(rng):
    v = Vocabulary(16, pointer_gen=rng)
    with pytest.raises(SpaParseError):
        v.parse("a")
    with pytest.raises(SpaParseError):
        v.parse("A+B+C+a")


@pytest.mark.parametrize("solver", [None, nengo.solvers.Lstsq()])
def test_transform(rng, solver):
    v1 = Vocabulary(32, strict=False, pointer_gen=rng)
    v2 = Vocabulary(64, strict=False, pointer_gen=rng)
    v1.populate("A; B; C")
    v2.populate("A; B; C")
    A = v1["A"]
    B = v1["B"]
    C = v1["C"]

    # Test transform from v1 to v2 (full vocbulary)
    # Expected: np.dot(t, A.v) ~= v2.parse('A')
    # Expected: np.dot(t, B.v) ~= v2.parse('B')
    # Expected: np.dot(t, C.v) ~= v2.parse('C')
    t = v1.transform_to(v2, solver=solver)

    assert v2.parse("A").compare(np.dot(t, A.v)) > 0.85
    assert v2.parse("C+B").compare(np.dot(t, C.v + B.v)) > 0.85

    # Test transform from v1 to v2 (only 'A' and 'B')
    t = v1.transform_to(v2, keys=["A", "B"], solver=solver)

    assert v2.parse("A").compare(np.dot(t, A.v)) > 0.85
    assert v2.parse("B").compare(np.dot(t, C.v + B.v)) > 0.85

    # Test warns on missing keys
    v1.populate("D")
    D = v1["D"]
    with pytest.warns(NengoWarning):
        v1.transform_to(v2, solver=solver)

    # Test populating missing keys
    t = v1.transform_to(v2, populate=True, solver=solver)
    assert v2.parse("D").compare(np.dot(t, D.v)) > 0.85

    # Test ignores missing keys in source vocab
    v2.populate("E")
    v1.transform_to(v2, populate=True, solver=solver)
    assert "E" not in v1


def test_create_pointer_warning(rng):
    v = Vocabulary(2, pointer_gen=rng)

    # five pointers shouldn't fit
    with pytest.warns(UserWarning):
        v.populate("A; B; C; D; E")


def test_readonly(rng):
    v1 = Vocabulary(32, pointer_gen=rng)
    v1.populate("A;B;C")

    v1.readonly = True

    with pytest.raises(ValueError):
        v1.parse("D")


def test_subset(rng, algebra):
    v1 = Vocabulary(32, pointer_gen=rng, algebra=algebra)
    v1.populate("A; B; C; D; E; F; G")

    # Test creating a vocabulary subset
    v2 = v1.create_subset(["A", "C", "E"])
    assert list(v2.keys()) == ["A", "C", "E"]
    assert_equal(v2["A"].v, v1["A"].v)
    assert_equal(v2["C"].v, v1["C"].v)
    assert_equal(v2["E"].v, v1["E"].v)

    assert v1.algebra is v2.algebra


def test_vocabulary_tracking(rng):
    v = Vocabulary(32, pointer_gen=rng)
    v.populate("A")

    assert v["A"].vocab is v
    assert v.parse("2 * A").vocab is v


def test_vocabulary_set(rng):
    v8 = Vocabulary(8)
    v16 = Vocabulary(16)
    v32 = Vocabulary(32)
    vs = VocabularyMap([v8, v16], rng=rng)

    # Behaviour common to set and dict
    assert len(vs) == 2
    assert 8 in vs
    assert 16 in vs
    assert 32 not in vs

    assert v8 in vs
    assert v16 in vs
    assert v32 not in vs
    assert Vocabulary(8) not in vs

    # dict behaviour
    assert vs[8] is v8
    assert vs[16] is v16

    del vs[8]
    assert 8 not in vs

    # set behaviour
    vs.add(v32)
    assert vs[32] is v32
    with pytest.warns(UserWarning):
        vs.add(v32)

    vs.discard(32)
    assert 32 not in vs
    vs.discard(v16)
    assert 16 not in vs

    # creating new vocabs if non existent
    vs.add(v8)
    assert vs.get_or_create(8) is v8
    new = vs.get_or_create(16)
    assert vs[16] is new
    assert new.dimensions == 16
    assert new.pointer_gen.rng is rng


def test_vocabulary_map_param():
    class Test:
        vocab_map = VocabularyMapParam("vocab_map", readonly=False)

    obj = Test()
    vm = VocabularyMap()
    v16 = Vocabulary(16)
    v32 = Vocabulary(32)

    obj.vocab_map = vm
    assert obj.vocab_map is vm

    obj.vocab_map = [v16, v32]
    assert obj.vocab_map[16] is v16
    assert obj.vocab_map[32] is v32

    with pytest.raises(ValidationError):
        obj.vocab_map = "incompatible"


def test_vocabulary_or_dim_param():
    v16 = Vocabulary(16)
    v32 = Vocabulary(32)

    class Test:
        vocabs = VocabularyMap([v16])
        vocab = VocabularyOrDimParam("vocab", readonly=False)

    obj = Test()

    obj.vocab = v32
    assert obj.vocab is v32

    obj.vocab = 16
    assert obj.vocab is v16

    with pytest.raises(ValidationError):
        obj.vocab = "incompatible"

    with pytest.raises(ValidationError):
        obj.vocab = 0


def test_pointer_names():
    v = Vocabulary(16)
    v.populate("A; B")

    assert v["A"].name == "A"
    assert v.parse("A*B").name == "A * B"
