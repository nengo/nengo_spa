"""AST classes for symbolic operations."""

import re

import nengo
import numpy as np

from nengo_spa.ast import expr_tree
from nengo_spa.ast.base import Fixed, TypeCheckedBinaryOp, infer_types
from nengo_spa.exceptions import SpaTypeError
from nengo_spa.semantic_pointer import SemanticPointer
from nengo_spa.typechecks import is_number
from nengo_spa.types import TAnyVocab, TScalar, TVocabulary


def as_symbolic_node(obj):
    if is_number(obj):
        obj = FixedScalar(obj)
    return obj


class Symbol(Fixed):
    @property
    def expr(self):
        raise NotImplementedError()


symbolic_op = TypeCheckedBinaryOp(Symbol, as_symbolic_node)


class FixedScalar(Symbol):
    # Does not implement any operators as Python does so for numbers and
    # once a Python number gets converted into an AST node it must have been
    # used with some other non-scalar AST node that will return
    # a non-FixedScalar AST node. Thus, there should never be a situation where
    # an operator is applied to two FixedScalar nodes.

    def __init__(self, value):
        super(FixedScalar, self).__init__(type_=TScalar)
        self.value = value

    def connect_to(self, sink, **kwargs):
        return nengo.Connection(self.construct(), sink, **kwargs)

    def construct(self):
        return nengo.Node(self.value, label=str(self.value))

    def evaluate(self):
        return self.value

    @property
    def expr(self):
        return repr(self.value)

    @property
    def _expr_tree(self):
        return expr_tree.Leaf(self.expr)

    def __neg__(self):
        return FixedScalar(-self.value)


class PointerSymbol(Symbol):
    def __init__(self, expr, type_=TAnyVocab):
        super(PointerSymbol, self).__init__(type_=type_)
        self._expr_tree = (
            expr if isinstance(expr, expr_tree.Node) else expr_tree.Leaf(expr)
        )

    def connect_to(self, sink, **kwargs):
        return nengo.Connection(self.construct(), sink, **kwargs)

    def construct(self):
        return nengo.Node(self.evaluate().v, label=self.expr)

    def evaluate(self):
        if not isinstance(self.type, TVocabulary):
            raise SpaTypeError(
                "Cannot evaluate a symbolic semantic pointer expression "
                "without knowing the vocabulary."
            )
        return self.type.vocab.parse(self.expr)

    @property
    def expr(self):
        return str(self._expr_tree)

    def normalized(self):
        return PointerSymbol(self.expr + ".normalized()", self.type)

    def unitary(self):
        return PointerSymbol(self.expr + ".unitary()", self.type)

    def __invert__(self):
        return PointerSymbol(~self._expr_tree, self.type)

    def linv(self):
        return PointerSymbol(self.expr + ".linv()", self.type)

    def rinv(self):
        return PointerSymbol(self.expr + ".rinv()", self.type)

    def __neg__(self):
        return PointerSymbol(-self._expr_tree, self.type)

    def __add__(self, other):
        other = as_symbolic_node(other)
        if not isinstance(other, PointerSymbol):
            return NotImplemented
        type_ = infer_types(self, other)
        return PointerSymbol(self._expr_tree + other._expr_tree, type_)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        other = as_symbolic_node(other)
        if not isinstance(other, PointerSymbol):
            return NotImplemented
        type_ = infer_types(self, other)
        return PointerSymbol(self._expr_tree - other._expr_tree, type_)

    def __rsub__(self, other):
        return (-self) + other

    @symbolic_op
    def __mul__(self, other):
        type_ = infer_types(self, other)
        return PointerSymbol(self._expr_tree * other._expr_tree, type_)

    @symbolic_op
    def __rmul__(self, other):
        type_ = infer_types(self, other)
        return PointerSymbol(other._expr_tree * self._expr_tree, type_)

    @symbolic_op
    def __truediv__(self, other):
        type_ = infer_types(self, other)
        return PointerSymbol(self._expr_tree / other._expr_tree, type_)

    @symbolic_op
    def __pow__(self, other):
        type_ = infer_types(self, other)
        return PointerSymbol(self._expr_tree ** other._expr_tree, type_)

    def dot(self, other):
        other = as_symbolic_node(other)
        if not isinstance(other, PointerSymbol):
            return NotImplemented
        infer_types(self, other)
        return FixedScalar(self.evaluate().dot(other.evaluate()))

    def __matmul__(self, other):
        return self.dot(other)

    def rdot(self, other):
        return self.dot(other)

    def __rmatmul__(self, other):
        return self.rdot(other)

    def reinterpret(self, vocab=None):
        return self.evaluate().reinterpret(vocab)

    def translate(self, vocab, populate=None, keys=None, solver=None):
        tr = self.type.vocab.transform_to(
            vocab, populate=populate, keys=keys, solver=solver
        )
        return SemanticPointer(np.dot(tr, self.evaluate().v), vocab=vocab)

    def __repr__(self):
        return f"PointerSymbol({self._expr_tree!r}, {self.type!r})"


class PointerSymbolFactory:
    """Provides syntactic sugar to create *PointerSymbol* instances.

    Use the `.sym` instance of this class to create *PointerSymbols* like so::

        sym.foo  # creates PointerSymbol('foo')

    To create more complex symbolic expressions the following syntax is
    supported too::

        sym('foo + bar * baz')  # creates PointerSymbol('foo+bar*baz')
    """

    def __getattribute__(self, key):
        return PointerSymbol(key)

    def __call__(self, expr):
        return PointerSymbol("({})".format(re.sub(r"\s+", "", expr)))


sym = PointerSymbolFactory()
