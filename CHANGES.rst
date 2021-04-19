***************
Release History
***************

.. Changelog entries should follow this format:

   version (release date)
   ======================

   **section**

   - One-line description of change (link to Github issue/PR)

.. Changes should be organized in one of several sections:

   - Added
   - Changed
   - Deprecated
   - Removed
   - Fixed


1.3.0 (unreleased)
==================

**Added**

- Support for (fractional) binding powers and the notion of signs in algebras.
  (`#271 <https://github.com/nengo/nengo_spa/pull/271>`__)
- ``EquallySpacedPositiveUnitaryHrrVectors`` and ``VectorsWithProperties``
  vector generators.
  (`#284 <https://github.com/nengo/nengo_spa/issues/284>`__,
  `#285 <https://github.com/nengo/nengo_spa/pull/285>`__)

**Removed**

- Python 3.5 support was removed.
  (`#273 <https://github.com/nengo/nengo_spa/issues/273>`__,
  `#274 <https://github.com/nengo/nengo_spa/pull/274>`__)


1.2.0 (November 15, 2020)
=========================

**Added**

- Transposed Vector-derived Transformation Binding (TVTB) algebra which has
  essentially the same properties as the existing VTB algebra, but has two-sided
  identities and inverses (opposed to VTB where these are right-sided only).
  The only difference in the math is that TVTB transposes the matrix used in the
  binding operation.
  (`#266 <https://github.com/nengo/nengo_spa/issues/266>`__)
- Differentiation between left, right, and two-sided special elements (identity,
  zero, absorbing element, inverse) of an algebra.
  (`#265 <https://github.com/nengo/nengo_spa/pull/265>`__)
- Added ``linv`` and ``rinv`` methods to ``SemanticPointer`` for the left and
  right inverse, respectively.
  (`#265 <https://github.com/nengo/nengo_spa/pull/265>`__)
- Add support for the ``normalized`` and ``unitary`` methods on Semantic Pointer
  symbols.
  (`#265 <https://github.com/nengo/nengo_spa/pull/265>`__)

**Changed**

- Creating special elements (identity, zero, absorbing element, inverse) of the
  ``VtbAlgebra`` without ``sidedness`` argument has been deprecated because
  these are only right-sided special element. Add the
  ``sidedness=ElementSidedness.RIGHT`` argument to update your code.
  (`#265 <https://github.com/nengo/nengo_spa/pull/265>`__)
- The ``~`` operator has been deprecated for the ``VtbAlgebra``. Use the
  ``rinv()`` method instead.
  (`#265 <https://github.com/nengo/nengo_spa/pull/265>`__)
- Improved automatic names for ``SemanticPointer`` that only contain parenthesis
  where actually needed. In addition, syntax is considered when shortening a
  name exceeding the maximum length.
  (`#255 <https://github.com/nengo/nengo_spa/issues/255>`__,
  `#270 <https://github.com/nengo/nengo_spa/pull/270>`__)


1.1.1 (November 3, 2020)
========================

**Fixed**

- ``PointerSymbol`` precedence handling has been fixed. For example,
  ``(sym.A + sym.B) * sym.C`` will be evaluated correctly now.
  (`#267 <https://github.com/nengo/nengo_spa/issues/267>`__,
  `#268 <https://github.com/nengo/nengo_spa/pull/268>`__)


1.1.0 (June 23, 2020)
=====================

**Added**

- Support division with constant scalars.
  (`#249 <https://github.com/nengo/nengo_spa/issues/249>`__,
  `#253 <https://github.com/nengo/nengo_spa/pull/253>`__,
  `#257 <https://github.com/nengo/nengo_spa/pull/257>`__)

**Changed**

- Make ``AbstractAlgebra`` an actual abstract base class (using ``ABCMeta`` as
  meta-class). While still supported, this deprecates pure duck-typing for
  algebras.
  (`#240 <https://github.com/nengo/nengo_spa/pull/240>`__)
- Raise an exception when a Semantic Pointer is added to a vocabulary with a
  differing algebra.
  (`#239 <https://github.com/nengo/nengo_spa/issues/239>`__,
  `#240 <https://github.com/nengo/nengo_spa/pull/240>`__)
- All examples now have seeds to ensure that occasional "bad seeds" do not create
  problems in the documentation.
  (`#248 <https://github.com/nengo/nengo_spa/pull/248>`__)

**Fixed**

- ``SemanticPointer.translate`` and ``PointerSymbol.translate`` now use the ``keys``
  argument; previously, this argument was mistakenly ignored.
  (`#248 <https://github.com/nengo/nengo_spa/pull/248>`__)
- Fixed an issue where the names of iteratively generated semantic pointers
  could grow exponentially in length, by truncating them at 1 KB.
  (`#244 <https://github.com/nengo/nengo_spa/issues/244>`__,
  `#246 <https://github.com/nengo/nengo_spa/pull/246>`__)
- Allow NumPy scalars in place of Python scalars for binary operations on
  `SemanticPointer` instances.
  (`#250 <https://github.com/nengo/nengo_spa/issues/250>`__,
  `#257 <https://github.com/nengo/nengo_spa/pull/257>`__)
- The SPA sequence example was not working properly due to a missing connection.
  (`#258 <https://github.com/nengo/nengo_spa/issues/258>`__,
  `#259 <https://github.com/nengo/nengo_spa/pull/259>`__)



1.0.1 (December 14, 2019)
=========================

**Changed**

- Add redirects from old URLs to documentation.
  (`#237 <https://github.com/nengo/nengo_spa/issues/237>`__,
  `#238 <https://github.com/nengo/nengo_spa/pull/238>`__)


1.0.0 (December 12, 2019)
=========================

**Changed**

- Ensure compatibility with Nengo 3.
  (`#225 <https://github.com/nengo/nengo_spa/issues/225>`__,
  `#233 <https://github.com/nengo/nengo_spa/pull/233>`__,
  `#236 <https://github.com/nengo/nengo_spa/pull/236>`__)
- Modules and networks no longer set a default label. This will give
  more useful labels by default in Nengo GUI (assuming the latest dev
  version).
  (`#234 <https://github.com/nengo/nengo_spa/issues/234>`__,
  `#235 <https://github.com/nengo/nengo_spa/pull/235>`__)
- All networks have been converted to classes. This will give
  more useful labels by default in Nengo GUI (assuming the latest dev
  version).
  (`#234 <https://github.com/nengo/nengo_spa/issues/234>`__,
  `#235 <https://github.com/nengo/nengo_spa/pull/235>`__)


**Removed**

- Dropped support for Python 2.7 and 3.4.
  (`#233 <https://github.com/nengo/nengo_spa/pull/233>`__,
  `#236 <https://github.com/nengo/nengo_spa/pull/236>`__)


0.6.2 (June 21, 2019)
=====================

**Added**

- Add previously missing documentation on the ``vector_generation`` module as
  well as the ``reinterpret`` and ``translate`` methods of ``SemanticPointer``.
  (`#228 <https://github.com/nengo/nengo_spa/issues/228>`__,
  `#229 <https://github.com/nengo/nengo_spa/pull/229>`__)


**Fixed**

- Fixed a bug where an exception within an ``ActionSelection`` block would
  lead to every subsequent ``ActionSelection`` block to raise an exception.
  (`#230 <https://github.com/nengo/nengo_spa/issues/230>`__,
  `#231 <https://github.com/nengo/nengo_spa/pull/231>`__)
- Nengo SPA is now compatible with pytest 4. Support for earlier versions has
  been dropped.
  (`#227 <https://github.com/nengo/nengo_spa/pull/227>`__)


0.6.1 (April 26, 2019)
======================

**Changed**

- Minor documentation improvements.
  (`#217 <https://github.com/nengo/nengo_spa/pull/217>`__,
  `#218 <https://github.com/nengo/nengo_spa/pull/218>`__)


0.6.0 (September 17, 2018)
==========================

**Added**

- Support for algebras that allow to use binding operations other than circular
  convolution. This includes an implementation of vector-derived transformation
  binding (VTB) and the ``nengo_spa.networks.VTB`` network to perform this
  particular binding operation.
  (`#69 <https://github.com/nengo/nengo_spa/issues/69>`__,
  `#198 <https://github.com/nengo/nengo_spa/pull/198>`__)
- Added generators for vectors with different properties that can be used to
  define how vectors are created in a vocabulary (e.g., axis-aligned,
  orthogonal, unitary).
  (`#201 <https://github.com/nengo/nengo_spa/pull/201>`_,
  `#129 <https://github.com/nengo/nengo_spa/issues/129>`_)
- Added a matrix multiplication network ``nengo_spa.networks.MatrixMult`` based
  on the nengo-extras implementation.
  (`#198 <https://github.com/nengo/nengo_spa/pull/198>`__)
- Allow to connect to the utility node returned by `ifmax` with the SPA `>>`
  operator.
  (`#190 <https://github.com/nengo/nengo_spa/issues/190>`_,
  `#194 <https://github.com/nengo/nengo_spa/pull/194>`_)
- The Semantic Pointer names *AbsorbingElement*, *Identity*, and *Zero* now
  have a special meaning in *Vocabulary* and *nengo_spa.sym* and will return
  the respective special Semantic Pointers.
  (`#195 <https://github.com/nengo/nengo_spa/pull/195>`_,
  `#176 <https://github.com/nengo/nengo_spa/issues/176>`_)
- *SemanticPointer* instance can now track names for improved labeling in Nengo
  GUI.
  (`#202 <https://github.com/nengo/nengo_spa/pull/202>`_,
  `#184 <https://github.com/nengo/nengo_spa/issues/184>`_)
- Label the utility nodes for the action selection.
  (`#202 <https://github.com/nengo/nengo_spa/pull/202>`__)


**Changed**

- A number of module names have been changed for better naming consistency.
  In particular,

  - ``nengo_spa.actions`` to ``nengo_spa.action_selection``,
  - ``nengo_spa.pointer`` to ``nengo_spa.semantic_pointer``,
  - ``nengo_spa.vocab`` to ``nengo_spa.vocabulary``,
  - and ``nengo_spa.modules.assoc_mem`` to
    ``nengo_spa.modules.associative_memory``.

  (`#199 <https://github.com/nengo/nengo_spa/issues/199>`_,
  `#205 <https://github.com/nengo/nengo_spa/pull/205>`_)
- Require the ``mapping`` argument for associative memories. In addition to
  dictionaries and the string ``'by-key'``, a sequence of strings can be passed
  in to create an auto-associative memory.
  (`#177 <https://github.com/nengo/nengo_spa/pull/177>`_)
- Changed the ``rng`` argument for ``Vocabulary`` to ``pointer_gen``.
  (`#201 <https://github.com/nengo/nengo_spa/pull/201>`_)
- Renamed ``input_a`` and ``input_b`` of the ``nengo_spa.Bind`` module to
  ``input_left`` and ``input_right`` to account for non-commutative binding
  methods where the order of operands matters. Also, renamed the ``invert_a``
  and ``invert_b`` arguments to ``unbind_left`` and ``unbind_right`` to reflect
  that some binding methods might not have inverse vectors, but might still be
  able to do unbinding.
  (`#69 <https://github.com/nengo/nengo_spa/issues/69>`__,
  `#198 <https://github.com/nengo/nengo_spa/pull/198>`__)
- Renamed the ``nengo_spa.State`` parameter ``represent_identity`` to
  ``represent_cc_identity`` to reflect that it only optimizes for the circular
  convolution identity, but not the identity for other binding operations.
  (`#212 <https://github.com/nengo/nengo_spa/pull/212>`_)


**Removed**

- Removed ``nengo_spa.networks.circularconvolution.circconv`` because
  ``nengo_spa.algebras.CircularConvolutionAlgebra`` provides the same
  functionality.
  (`#198 <https://github.com/nengo/nengo_spa/pull/198>`__)
- The ``SemanticPointer`` class does no longer accept a single integer as
  dimensionality to create a random vector. Use the new generators in
  ``nengo_spa.vector_generation`` instead.
  (`#201 <https://github.com/nengo/nengo_spa/pull/201>`_)


**Fixed**

- Raise an exception instead of returning incorrect results from
  ``prob_cleanup``. Also, fix the function's incorrect documentation.
  (`#203 <https://github.com/nengo/nengo_spa/issues/203>`__,
  `#206 <https://github.com/nengo/nengo_spa/pull/206>`__)
- Fix ``nengo_spa.ActionSelection.keys()`` when no named actions have been
  provided.
  (`#210 <https://github.com/nengo/nengo_spa/pull/210>`_)
- Do not create an unnecessary compare network when computing a dot product
  with a ``SemanticPointer`` instance.
  (`#202 <https://github.com/nengo/nengo_spa/pull/202>`__)
- Handle ``SemanticPointer`` instances correctly as first argument to
  ``nengo_spa.dot``.
  (`#202 <https://github.com/nengo/nengo_spa/pull/202>`__)


0.5.2 (July 6, 2018)
====================

**Fixed**

- SPA modules will use the same default vocabularies even if not instantiated
  in the context of a `spa.Network`.
  (`#174 <https://github.com/nengo/nengo-spa/issues/174>`_,
  `#185 <https://github.com/nengo/nengo-spa/pull/185>`_)
- Disallow Python keywords, including None, True, and False, as well as unicode
  characters from Python names.
  (`#188 <https://github.com/nengo/nengo_spa/pull/188>`_,
  `#187 <https://github.com/nengo/nengo_spa/issues/187>`_)
- Allow action rules without name to have no effects.
  (`#189 <https://github.com/nengo/nengo_spa/issues/189>`_,
  `#191 <https://github.com/nengo/nengo_spa/pull/191>`_)
- Raise exception when using NumPy arrays in SPA operations which would give
  unexpected results.
  (`#192 <https://github.com/nengo/nengo_spa/issues/192>`_,
  `#193 <https://github.com/nengo/nengo_spa/pull/193>`_)


0.5.1 (June 7, 2018)
====================

**Added**

- ``Transcode`` now supports ``SemanticPointer`` and
  ``PointerSymbol`` output types.
  (`#175 <https://github.com/nengo/nengo-spa/issues/175>`_,
  `#178 <https://github.com/nengo/nengo-spa/pull/178>`_)

**Fixed**

- Allow integer values for vocabularies in associative memories.
  (`#171 <https://github.com/nengo/nengo_spa/pull/171>`_)
- Implement ``reinterpret`` operator for pointer symbols.
  (`#169 <https://github.com/nengo/nengo_spa/issues/169>`_,
  `#179 <https://github.com/nengo/nengo_spa/pull/179>`_)


0.5.0 (June 1, 2018)
====================

**Added**

- One-dimensional outputs of Nengo objects can be used as scalars in action
  rules.
  (`#139 <https://github.com/nengo/nengo_spa/issues/139>`_,
  `#157 <https://github.com/nengo/nengo_spa/pull/157>`_)
- Syntactic sugar for complex symbolic expressions:
  ``nengo_spa.sym('A + B * C')``.
  (`#138 <https://github.com/nengo/nengo_spa/issues/138>`_,
  `#159 <https://github.com/nengo/nengo_spa/pull/159>`_)
- Include the achieved similarity in warning issued when desired maximum
  similarity could not be obtained.
  (`#117 <https://github.com/nengo/nengo_spa/issues/117>`_,
  `#158 <https://github.com/nengo/nengo_spa/pull/158>`_)
- Possibility to name Vocabulary instances for debugging.
  (`#163 <https://github.com/nengo/nengo_spa/issues/163>`_,
  `#165 <https://github.com/nengo/nengo_spa/pull/165>`_)

**Changed**

- Make the error message for incompatible types more informative.
  (`#131 <https://github.com/nengo/nengo_spa/issues/131>`_,
  `#160 <https://github.com/nengo/nengo_spa/pull/160>`_



0.4.1 (May 18, 2018)
====================

This release fixes problems with the online documentation. Local installs are
not affected.


0.4.0 (May 17, 2018)
====================

This release increases the minimum required Nengo version to Nengo 2.7
(previously Nengo 2.4).

**Added**

- Added documentation and build tools for the documentation.
  (`#68 <https://github.com/nengo/nengo_spa/pull/68>`_)

**Changed**

- This release introduces a new syntax for SPA action rules.
  (`#114 <https://github.com/nengo/nengo_spa/pull/114>`_)

**Remove**

- Unnecessary ``vocab`` argument from ``Transcode``.
  (`#68 <https://github.com/nengo/nengo_spa/pull/68>`_)

**Fixed**

- Validation of ``VocabOrDimParam`` and ``VocabularyMapParam``.
  (`#95 <https://github.com/nengo/nengo_spa/issues/95>`_,
  `#98 <https://github.com/nengo/nengo_spa/pull/98>`_)
- Allow the configuration of instance parameters with
  ``nengo_spa.Network.config``.
  (`#112 <https://github.com/nengo/nengo_spa/issues/112>`_,
  `#113 <https://github.com/nengo/nengo_spa/pull/113>`_)
- Fix an undeclared input to the ``IAAssocMem`` module.
  (`#118 <https://github.com/nengo/nengo_spa/issues/118>`_,
  `#120 <https://github.com/nengo/nengo_spa/pull/120>`_)


0.3.2 (November 17, 2017)
=========================

**Added**

- Add ``all_bgs`` and ``all_thals`` methods to
  ``AstAccessor`` to enable easy access to these objects.
  (`#61 <https://github.com/nengo/nengo_spa/pull/99>`__,
  `#28 <https://github.com/nengo/nengo_spa/issues/80>`__)

**Fixed**

- Allow the ``spa.Actions`` string to be empty.
  (`#107 <https://github.com/nengo/nengo_spa/issues/107>`_,
  `#109 <https://github.com/nengo/nengo_spa/pull/109>`_)
- The ``pass`` keyword can now be used to create blocks in action rules that
  do not have any effect.
  (`#101 <https://github.com/nengo/nengo_spa/issues/101>`_,
  `#103 <https://github.com/nengo/nengo_spa/pull/103>`_)
- Allow comments at various places in actions rules.
  (`#102 <https://github.com/nengo/nengo_spa/issues/102>`_,
  `#104 <https://github.com/nengo/nengo_spa/pull/104>`_)


0.3.1 (November 7, 2017)
========================

**Changed**

- Clearer error message as a ``SpaTypeError`` something is used as input/output
  in an action rule without being declared as such.
  (`#82 <https://github.com/nengo/nengo_spa/issues/82>`_,
  `#89 <https://github.com/nengo/nengo_spa/pull/89>`_)

**Fixed**

- Allow leading comments in actions rules.
  (`#81 <https://github.com/nengo/nengo_spa/issues/81>`_,
  `#85 <https://github.com/nengo/nengo_spa/pull/85>`_)
- Gave the basal ganglia a default label.
  (`#84 <https://github.com/nengo/nengo_spa/issues/84>`_,
  `#88 <https://github.com/nengo/nengo_spa/pull/88>`_)
- Fixed warning produce by the ``create_inhibit_node`` function.
  (`#90 <https://github.com/nengo/nengo_spa/pull/90>`_)
- Prevent whitespace from being completely removed in action rules.
  (`#92 <https://github.com/nengo/nengo_spa/issues/92>`_,
  `#93 <https://github.com/nengo/nengo_spa/pull/93>`_)
- Have the ``intercept_width`` argument of ``IA`` actually take effect.
  (`#94 <https://github.com/nengo/nengo_spa/issues/94>`_,
  `#97 <https://github.com/nengo/nengo_spa/pull/97>`_)


0.3.0 (October 16, 2017)
========================

**Added**

- Add ``add_output`` and ``add_neuron_output`` methods to
  ``IdentityEnsembleArray`` to provide the full API that is provided by the
  regular Nengo ``EnsembleArray``.
  (`#61 <https://github.com/nengo/nengo_spa/pull/61>`_,
  `#28 <https://github.com/nengo/nengo_spa/issues/28>`_)
- Add ``create_inhibit_node`` function to create nodes that inhibit complete
  Nengo networks.
  (`#65 <https://github.com/nengo/nengo_spa/pull/65>`_,
  `#26 <https://github.com/nengo/nengo_spa/issues/26>`_)
- Add a ``solver`` argument to the action rule's ``translate`` to use a solver
  instead of an outer product to obtain the transformation matrix which can
  give slightly better results.
  (`#62 <https://github.com/nengo/nengo_spa/pull/62>`_,
  `#57 <https://github.com/nengo/nengo_spa/issues/57>`_)

**Changed**

- Actions rules do not require module to be assigned to the model any longer.
  They will access exactly the same variables as are available in the
  surrounding Python code. This means that existing action rules need to be
  changed to reference the correct names.
  (`#63 <https://github.com/nengo/nengo_spa/pull/63>`_)
- The action rule syntax changed significantly.
  (`#54 <https://github.com/nengo_spa/nengo/issues/54>`_,
  `#72 <https://github.com/nengo_spa/nengo/pull/72>`_)
- Actions will be build automatically without an explicit call to ``build()``.
  (`#59 <https://github.com/nengo/nengo_spa/pull/59>`_,
  `#45 <https://github.com/nengo/nengo_spa/issues/45>`_,
  `#55 <https://github.com/nengo/nengo_spa/issues/55>`_)
- Consolidated the functionality of ``Encode`` and ``Decode`` into
  ``Transcode``.
  (`#67 <https://github.com/nengo/nengo_spa/pull/67>`_,
  `#58 <https://github.com/nengo/nengo_spa/issues/58>`_)

**Fixed**

- Fix some operations changing the dimensionality of semantic pointers with an
  odd initial dimensionality.
  (`#52 <https://github.com/nengo/nengo_spa/issues/52>`_,
  `#53 <https://github.com/nengo/nengo_spa/pull/53>`_)
- When building actions the basal ganglia and thalamus will only be created
  when actually required.
  (`#60 <https://github.com/nengo/nengo_spa/pull/60>`_,
  `#42 <https://github.com/nengo/nengo_spa/issues/42>`_)
- The vocabulary translate mechanism will properly ignore missing keys in the
  target vocabulary when ``populate=False``.
  (`#62 <https://github.com/nengo/nengo_spa/pull/62>`_,
  `#56 <https://github.com/nengo/nengo_spa/issues/56>`_)
- Allow empty string as argument to `Vocabulary.populate`.
  (`#73 <https://github.com/nengo_spa/nengo/pull/73>`_)


0.2 (June 22, 2017)
===================

**Added**

- Tutorial explaining what has changed in nengo_spa compared to the legacy SPA
  implementation.
  (`#46 <https://github.com/nengo/nengo_spa/pull/46>`_)
- Examples can be extracted with ``python -m nengo_spa extract-examples
  <destination>``.
  (`#49 <https://github.com/nengo/nengo_spa/pull/49>`_,
  `#7 <https://github.com/nengo/nengo_spa/issues/7>`_)

**Changed**

- Replaced *input_keys* and *output_keys* arguments of associative memories
  with a single *mapping* argument.
  (`#29 <https://github.com/nengo/nengo_spa/pull/29>`_,
  `#8 <https://github.com/nengo/nengo_spa/issues/8>`_)
- Replaced *ampa_config* and *gaba_config* parameters of the
  *BasalGanglia* with *ampa_synapse* and *gaba_synapse* parameters.
  Removed the *general_config* parameter.
  (`#30 <https://github.com/nengo/nengo_spa/pull/30>`_,
  `#23 <https://github.com/nengo/nengo_spa/issues/23>`_)

**Fixed**

- Improved a number of error messages.
  (`#35 <https://github.com/nengo/nengo_spa/pull/35>`_,
  `#32 <https://github.com/nengo/nengo_spa/issues/32>`_,
  `#34 <https://github.com/nengo/nengo_spa/issues/34>`_)
- Improved accuracy by fixing choice of evaluation point and intercept
  distributions.
  (`#39 <https://github.com/nengo/nengo_spa/pull/39>`_)
- Correctly apply transforms on first vector in vocabularies on on non-strict
  vocabularies.
  (`#43 <https://github.com/nengo/nengo_spa/pull/43>`_)


0.1.1 (May 19, 2017)
====================

**Fixed**

- Updated the 0.1 changelog.


0.1 (May 19, 2017)
==================

Initial release of Nengo SPA with core functionality, but excluding

- updates and completion the documentation,
- proper integration with Nengo GUI.

The API is still conisdered unstable in some parts of it are likely to change
in the future.

Main features compared to the SPA implementation shipped with Nengo are:

- neural representations have been optimized for higher accuracy,
- support for arbitrarily complex action rules,
- SPA networks can be used as normal Nengo networks,
- and SPA networks can be nested.
