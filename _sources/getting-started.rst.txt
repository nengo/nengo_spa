Getting started
===============

Installation
------------

To install NengoSPA, we recommend using ``pip``::

    pip install nengo-spa

``pip`` will do its best to install all of Nengo's requirements when it
installs NengoSPA. However, if anything goes wrong during this process, you
can install NengoSPA's requirements manually before doing ``pip install
nengo-spa`` again.

NengoSPA only depends on `core Nengo
<https://www.nengo.ai/nengo/index.html>`_ (which depends on `NumPy
<https://numpy.org/>`_). Please check the `Nengo documentation
<https://www.nengo.ai/nengo/getting-started.html#installation>`__ for
instructions on how to install Nengo or NumPy.

We also suggest that you install `SciPy <https://www.scipy.org/>`_ to obtain the
best accuracy in your networks and access to all NengoSPA features. We
recommend installing SciPy with the same method that you used to install NumPy.
Check the `Nengo documentation
<https://www.nengo.ai/nengo/getting-started.html#installing-numpy>`__ and
`SciPy documentation <https://www.scipy.org/install.html>`_ for available
installation methods.

Further optional packages
^^^^^^^^^^^^^^^^^^^^^^^^^

Besides optional SciPy package, there are a few more optional packages that
are only required for specific purposes.

.. code-block:: bash

   pip install nengo-spa[docs]  # For building docs
   pip install nengo-spa[tests]  # For running the test suite
   pip install nengo-spa[all]  # All of the above, including SciPy

Examples
^^^^^^^^

Examples of NengoSPA usage are included in this documentation. Each example
has a link to download it as Jupyter notebook at the top of its page.


Usage
-----

The recommended way to use NengoSPA is to ``import nengo_spa as spa``. (Note
that this uses an underscore in the module name and is different from
`nengo.spa` which refers to the legacy SPA module shipped with core Nengo.)

To use NengoSPA functionality in your models use `nengo_spa.Network` instead of
`nengo.Network`. A basic NengoSPA model can look like this::

    import nengo
    import nengo_spa as spa

    with spa.Network() as model:
        state = spa.State(16)
        spa.sym.A >> state


Next steps
----------

* If you are unfamiliar with the Semantic Pointer Architecture, start with the
  :ref:`/user-guide/spa-intro.rst`.
* If you are new to building SPA models with Nengo, read the
  :ref:`/examples/intro.ipynb`.
* If you have used the legacy SPA module included in core Nengo, read the
  tutorial on :ref:`/examples/intro-coming-from-legacy-spa.ipynb`.
