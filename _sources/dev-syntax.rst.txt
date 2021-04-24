Implementation of the SPA syntax
--------------------------------

The SPA syntax is implemented with Python operator overloading at its core.
There is a hierarchy of certain sets to consider in this.

1. An operation on two `.SemanticPointer` instances will always produce
   another `.SemanticPointer` instance (or scalar in case of a dot product).
   Thus, the set of `.SemanticPointer` is closed under most operations.
2. Next is the set of symbols created with `nengo_spa.sym`.
   These will be instances of `.PointerSymbol` and any operation on two of these
   instance will give another `.PointerSymbol`.
   For example, ``PointerSymbol('A') * PointerSymbol('B')`` will give
   ``PointerSymbol('A*B')``. In addition, some operations are defined between
   `.FixedScalar` and `.PointerSymbol`. When using a number in such an operation
   it will be converted automatically to a `.FixedScalar` instance.
3. The final set are operations based on module outputs that will change over
   the course of a simulation. All of these fall into the set of `.DynamicNode`
   instances. The implementation of the operators for `.DynamicNode` is a little
   bit more involved as the operands may not just be other `.DynamicNode`
   instances, but also `.PointerSymbol` and `.SemanticPointer` instances. The
   result will usually be also a `.DynamicNode`, but certain specializations
   exist. `.Summed` is used for the sum of multiple dynamic outputs,
   `.Transformed` is used for a dynamic output to which a constant transformation
   matrix is applied, and `.ModuleOutput` is the bare output of a SPA module.

NengoSPA used to construct a complete abstract syntax tree (AST) before
constructing any network, but this has since been changed to greedily construct
networks as soon as all the required information has been obtained. For this
historical reason, most of the classes mentioned still live in `nengo_spa.ast`.
Furthermore, all of this classes derive from `nengo_spa.ast.base.Node` which
specifies the minimal interface of all these classes:

* A *type* attribute used to ensure type safety within
  the SPA syntax and provides the type a node evaluates to (see below).
* A *connect_to(sink, **kwargs)* method that creates all the network components
  to implement the node and connects the output to the Nengo object *sink*.
  The keyword arguments are to be passed to the `nengo.Connection`.
* A *construct()* method that creates all the network components required to
  implement the node and returns a Nengo object providing the output (instead
  of connecting into a receiving Nengo object).

For fixed values nodes of the type `.Fixed` are used that need to implement an
additional *evaluate()* method that evaluates the fixed expression and returns
the result.


Types
^^^^^

Types in NengoSPA are defined by deriving from `nengo_spa.types.Type`. Two
types will be considered equal if their *name* attributes match (as long as
*__eq__* is not overwritten). For more complex relationships, the *__gt__*
method may be overwritten to specify a partial ordering. A call to
``a.__gt__(b)`` should return *True*, if (and only if) *b* can be cast to the
type *a*. For example, the type for an unspecified vocabulary can be cast to
the type for a specific vocabulary.

Currently, the types `.TScalar`, `.TAnyVocab`, `.TAnyVocabOfDim`, and 
`.TVocabulary` are defined, with partial ordering `TScalar < TAnyVocab`,
`TAnyVocab < TAnyVocabOfDim`, `TAnyVocab < TVocabulary`,
`TAnyVocabOfDim(vocab.dimensions) < TVocabulary(vocab)`.

The `nengo_spa.types.coerce_types` can be used to determine the smallest type
in the partial ordering enclosing all given types.


Actions and the ``>>`` operator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``>>`` (right shift) operator for creating connections is also implemented
through operator overloading on the `.ModuleInput` class. Depending on the
context, it either creates the connection immediately or creates
a `.RoutedConnection` instance in the context of an `nengo_spa.Actions` object.
`nengo_spa.actions.ifmax` will then trigger the actual creation of the gated
connection with the appropriate gating.


Application of the operator overloading to `nengo_spa.Network`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

So far the operator overloading has only been done on specific classes deriving
from `nengo_spa.ast.base.Node`. However, the operators need to work with SPA
networks. For this, `nengo_spa.Network` derives from `.SpaOperatorMixin` which:

1. Defines the overloaded operators
2. Converts the operands to the appropriate
   `nengo_spa.ast.base.Node` (or `.ModuleInput`) class
3. Delegates to the class's implementation of the operator.

Furthermore, the operators need to be overloaded for the input and outputs of
a SPA network. These will be basic Nengo objects and should continue to be
usable as such. Thus, the `.Network.declare_input` and
`.Network.declare_output` methods will dynamically insert `.SpaOperatorMixin`
into the inheritance list of a single instance. They also register the
associated vocabulary for the type checking.
