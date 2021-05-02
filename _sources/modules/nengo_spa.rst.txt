nengo\_spa
==========

* `nengo_spa.ActionSelection`
* `nengo_spa.create_inhibit_node`
* `nengo_spa.ifmax`
* `nengo_spa.Network`
* `nengo_spa.sym`

.. autoclass:: nengo_spa.ActionSelection

.. autofunction:: nengo_spa.create_inhibit_node

.. function:: nengo_spa.ifmax([name,] condition, actions)

   Defines a potential aciton within an `ActionSelection` context.

   :param name: Name for the action. Can be omitted.
   :type name: str, optional
   :param condition: The utility value for the given actions.
   :param actions: The actions to activate if the given utility is the highest.

   :return: Nengo object that can be connected to, to provide additional input
            to the utility value.
   :rtype: nengo.base.NengoObject

.. autoclass:: nengo_spa.Network
   :show-inheritance:

.. data:: nengo_spa.sym

   Provides Semantic Pointer symbols for symbolic expressions that are not tied
   to a single vocabulary. The vocabulary will be determined from the context.
   To use a symbol access it as an attribute on this object.

   For example the following::

       sym.A * sym.B >> state

   is equivalent to::

       state.vocab.parse('A * B') >> state


Further members
---------------

Commonly used classes and functions are accessible at the top level of the
`nengo_spa` package.

.. autosummary::
   :nosignatures:

   nengo_spa.vocabulary.Vocabulary


SPA Modules
^^^^^^^^^^^

.. autosummary::
   :nosignatures:

   nengo_spa.modules.AssociativeMemory
   nengo_spa.modules.IAAssocMem
   nengo_spa.modules.ThresholdingAssocMem
   nengo_spa.modules.WTAAssocMem
   nengo_spa.modules.BasalGanglia
   nengo_spa.modules.Bind
   nengo_spa.modules.Compare
   nengo_spa.modules.Product
   nengo_spa.modules.Scalar
   nengo_spa.modules.State
   nengo_spa.modules.Thalamus
   nengo_spa.modules.Transcode


Examination of Semantic Pointers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autosummary::
   :nosignatures:

   nengo_spa.examine.pairs
   nengo_spa.examine.similarity
   nengo_spa.examine.text


Operators
^^^^^^^^^

.. autosummary::
   :nosignatures:

   nengo_spa.operators.dot
   nengo_spa.operators.reinterpret
   nengo_spa.operators.translate
