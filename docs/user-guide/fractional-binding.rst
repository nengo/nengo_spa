Advanced: fractional binding
============================

The binding of Semantic Pointers is similar to multiplication.
When you multiply a number repeatedly with itself,
you get a power of this number, e.g. :math:`x \cdot x \cdot x = x^3`.
This concept translates to binding:

.. math::

    \vec{v} \circledast \vec{v} \circledast \vec{v} = \vec{v}^3
    
When working with `.SemanticPointer` instances,
you can just use Python's power operator ``**``;
algebras provide a `~.AbstractAlgebra.binding_power` method:
    
.. testsetup:: fractional_binding_user_guide

    import nengo_spa as spa
    import numpy as np

    d = 64
    algebra = spa.algebras.HrrAlgebra()
    positive = spa.SemanticPointer(
        algebra.create_vector(d, {spa.algebras.CommonProperties.POSITIVE}),
        algebra=algebra
    )
    pointer = spa.semantic_pointer.NegativeIdentity(d) * positive

.. testcode:: fractional_binding_user_guide

    assert np.allclose((pointer * pointer * pointer).v, (pointer ** 3).v)
    assert np.allclose((pointer * pointer * pointer).v, algebra.binding_power(pointer.v, 3))

The exponent of such a power may also be a real (as in non-integer) number
under certain conditions, e.g. :math:`\vec{v}^{1.23}`.
We call this fractional binding
(or fractional binding powers)
as the vector will be bound only "partially" to itself.
As you let the exponent :math:`p` change from 1 to 2,
the binding power :math:`\vec{v}^p`
will transition continuously from :math:`\vec{v}` to :math:`\vec{v}^2`.

.. plot:: pyplots/power_similarity.py

Fractional binding is useful
because it allows encoding real-valued numbers.
One application,
where this is required,
is the representation of continuous space [komer2019]_.


Semantic Pointer signs
----------------------

Fractional exponents can only be used with certain Semantic Pointers.
Real numbers can serve here as an analogy again.
Consider, for example, :math:`(-1)^{0.5} = \sqrt{-1}`:
there is no solution within the real numbers itself
(you'd need to expand the domain to complex numbers).
Fractional exponents require a non-negative sign of the base.
The concept of a sign can be translated to Semantic Pointers,
albeit a bit more complex,
and a fractional binding requires a Semantic Pointer with non-negative sign.

A sign of a Semantic Pointer can not just be positive, negative, or zero,
but also indefinite.
There might also be multiple types of negative signs.
Thus, the binding of two Semantic Pointers with negative signs might not be positive.
Only the binding of two Semantic Pointers with the same type of sign will yield
a positive Semantic Pointer.

Like the sign of a number has a corresponding number
(+1 for the positive sign, —1 for the negative sign, 0 for zero),
certain Semantic Pointers will correspond to the Semantic Pointer signs.
Binding a Semantic Pointer with its sign vector will give a positive Semantic Pointer.

How exactly the signs work depend on the :doc:`algebra <algebras>`.
See the documenation of `.HrrSign`, `.VtbSign`, and `.TvtbSign` for more details.

To determine the sign of a Semantic Pointer use the `~.SemanticPointer.sign`
method:

.. testcode:: fractional_binding_user_guide

    sign = pointer.sign()
    print("Positive?", sign.is_positive())
    print("Negative?", sign.is_negative())
    
.. testoutput:: fractional_binding_user_guide

    Positive? False
    Negative? True
    
A sign will also correspond to a specfic Semantic Pointer.
Binding a Semantic Pointer to the inverse sign Semantic Pointer
will give a positive version of the bound Semantic Pointer
in most algebras.

.. testcode:: fractional_binding_user_guide

    abs_pointer = ~pointer.sign().to_semantic_pointer() * pointer
    print("Positive?", abs_pointer.sign().is_positive())

.. testoutput:: fractional_binding_user_guide

    Positive? True
    
.. hint::

    This is analogous to the sign of complex numbers:

    .. math::

        \mathrm{sign}(z) = \frac{z}{\mathrm{abs}(z)}

    By cross-multiplying we get:

    .. math::

        \mathrm{abs}(z) = \mathrm{sign}^{-1}(z) \cdot z

One can also use the `~.SemanticPointer.abs` method
to obtain a positive Semantic Pointer
based on a given Semantic Pointer.
If a new positive Semantic Pointer,
without relation to an existing Semantic Pointer,
is needed,
the `.VectorsWithProperties` generator can be used:

.. testcode:: fractional_binding_user_guide

    from nengo_spa.algebras import CommonProperties
    from nengo_spa.vector_generation import VectorsWithProperties

    gen = VectorsWithProperties(d, {CommonProperties.POSITIVE}, algebra=algebra)
    positive_pointer = spa.SemanticPointer(next(gen), algebra=algebra)

    print("Positive?", positive_pointer.sign().is_positive())
    
.. testoutput:: fractional_binding_user_guide

    Positive? True


Desirable properties for exponentiated Semantic Pointers
--------------------------------------------------------

When increasing the exponent in a power of a number,
the result will approach either 0 or grow without bound
(:math:`\lim_{p \rightarrow \infty} x^p = 0` if :math:`0 \leq x < 1`,
:math:`\lim_{p \rightarrow \infty} x^p = \infty` if :math:`x > 1`).
The same can happen for the vector length of the binding power of a Semantic Pointer.
This might be undesirable (e.g. for representation in neurons).
Using a unitary Semantic Pointer ensures that the vectors length will stay constant.
the `.VectorsWithProperties` generator can be used
to create positive unitary Semantic Pointers:

.. testcode:: fractional_binding_user_guide

    from nengo_spa.algebras import CommonProperties
    from nengo_spa.vector_generation import VectorsWithProperties

    gen = VectorsWithProperties(d, {CommonProperties.POSITIVE, CommonProperties.UNITARY}, algebra=algebra)
    positive_unitary_pointer = spa.SemanticPointer(next(gen), algebra=algebra)

Note that ``pointer.abs().unitary()`` or ``pointer.unitary().abs()`` is *not*
guaranteed to work because the operation of making a Semantic Pointer unitary
(positive) can destroy the property of being positive (unitary)
if not both constraints are taken into account at the same time.

The binding powers of a positive, unitary Semantic Pointer
move around a multidimensional circle.
A negative Semantic Pointer will jump
between such multidimensional circles
ith each binding
(similar to the powers of a negative number that are alternating
between positive and negative numbers).


Exponentiation laws
-------------------

The usual exponentiation laws do not hold in general for binding powers,
i.e. :math:`(\vec{v}^a)^b \ne \vec{v}^{a \cdot b}`
and :math:`\vec{v}^a \cdot \vec{v}^b \ne \vec{v}^{a + b}`.
For a specfic algebra exponentiation laws might hold under certain conditions.
See `.HrrAlgebra.binding_power`, `.VtbAlgebra.binding_power`,
and `.TvtbAlgebra.binding_power` for details.


Negative exponents and approximate inverses
-------------------------------------------

For real numbers, an exponent of —1 is equivalent to the multiplicative inverse.
Semantic Pointer binding powers work similar, however,
an exponent of —1 represents the approximate inverse here.
Thus, the identity :math:`(\vec{v}^a)^b = \vec{v}^{a \cdot b}`
only holds for unitary Semantic Pointers :math:`\vec{v}`.


References
----------

.. [komer2019] Komer, B., Stewart, T.C., Voelker, A.R. and Eliasmith, C.
     A neural representation of continuous space using fractional binding.
     Proceedings of the 41st Annual Meeting of the Cognitive Science
     Society. 2019.