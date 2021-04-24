Examples
========

See the following examples for demonstrations
of how ``nengo_spa`` works.

.. note::

   In most of the examples, we set seeds on the network and vocabulary objects.
   This is done for consistency; all the examples should work across a wide variety
   of seeds, but occasionally a "bad seed" will cause the results to be different
   from what we describe. We set the seeds to avoid this problem.
   In practice, such adverse results can typically be avoided by using more dimensions
   per semantic pointer (at least 64). We often use smaller numbers of dimensions in
   the examples so that they run quickly, but this makes bad seeds somewhat more common.

.. toctree::

   examples/convolution
   examples/associative-memory
   examples/question
   examples/question-control
   examples/question-memory
   examples/spa-sequence
   examples/spa-sequence-routed
   examples/spa-parser
   examples/vocabulary-casting
