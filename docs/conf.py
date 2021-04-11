# -*- coding: utf-8 -*-
#
# This file is execfile()d with the current directory set
# to its containing dir.

import os
import sys

try:
    import nengo_sphinx_theme

    import nengo_spa

    assert nengo_sphinx_theme
except ImportError:
    print(
        "To build the documentation, nengo_spa and nengo_sphinx_theme "
        "must be installed in the current environment. Please install these "
        "and their requirements first. A virtualenv is recommended!"
    )
    sys.exit(1)

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.githubpages",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "matplotlib.sphinxext.plot_directive",
    "nbsphinx",
    "nengo_sphinx_theme.ext.redirects",
]

default_role = "py:obj"
numfig = True

# -- sphinx.ext.autodoc
autoclass_content = "both"  # class and __init__ docstrings are concatenated
autodoc_default_options = {  # new in version 1.8
    "members": None,
}
autodoc_member_order = "bysource"  # default is alphabetical

# -- sphinx.ext.intersphinx
intersphinx_mapping = {
    "nengo": ("https://www.nengo.ai/nengo/", None),
    "numpy": ("https://numpy.org/doc/stable", None),
}

# -- sphinx.ext.todo
todo_include_todos = True

# -- linkcheck
linkcheck_ignore = [
    r"^https?://www\.amazon\..*$",
    r"^https://uwspace\.uwaterloo\.ca/.*$",
    r"^https?://journals\.plos\.org/.*$",
    r"^https?://direct.mit.edu/neco/article/.*$",
]

# -- doctest
doctest_global_setup = "import nengo_spa"

# -- nbsphinx
nbsphinx_allow_errors = False
nbsphinx_timeout = 600
nbsphinx_execute = "always"

# -- sphinx
exclude_patterns = ["_build", "examples/.ipynb_checkpoints"]
source_suffix = ".rst"
source_encoding = "utf-8"
master_doc = "index"

# Need to include https Mathjax path for sphinx < v1.3
mathjax_path = (
    "https://cdn.mathjax.org/mathjax/latest/MathJax.js" "?config=TeX-AMS-MML_HTMLorMML"
)

project = "NengoSPA"
authors = "Applied Brain Research"
copyright = nengo_spa.__copyright__
version = ".".join(nengo_spa.__version__.split(".")[:2])  # Short X.Y version
release = nengo_spa.__version__  # Full version, with tags
pygments_style = "friendly"

# -- Options for HTML output --------------------------------------------------

html_theme = "nengo_sphinx_theme"
html_title = f"NengoSPA {release} docs"
html_static_path = ["_static"]
html_favicon = os.path.join("_static", "favicon.ico")
html_use_smartypants = True
htmlhelp_basename = "Nengodoc"
html_last_updated_fmt = ""  # Suppress 'Last updated on:' timestamp
html_show_sphinx = False
html_theme_options = {
    "nengo_logo": "nengo-spa-full-light.svg",
    "nengo_logo_color": "#d40000",
    "analytics_id": "UA-41658423-2",
}
html_redirects = [
    (old, old.replace("_", "-"))
    for old in (
        "dev_syntax.html",
        "examples/associative_memory.html",
        "examples/custom_module.html",
        "examples/intro_coming_from_legacy_spa.html",
        "examples/question_control.html",
        "examples/question_memory.html",
        "examples/spa_parser.html",
        "examples/spa_sequence_routed.html",
        "examples/spa_sequence.html",
        "examples/vocabulary_casting.html",
        "getting_started.html",
        "user_guide.html",
        "user_guide/algebras.html",
        "user_guide/spa_intro.html",
    )
]

# -- Options for LaTeX output -------------------------------------------------

latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "11pt",
}

latex_documents = [
    # (source start file, target, title, author, documentclass [howto/manual])
    ("index", "nengo.tex", html_title, authors, "manual"),
]

# -- Options for manual page output -------------------------------------------

man_pages = [
    # (source start file, name, description, authors, manual section).
    ("index", "nengo", html_title, [authors], 1)
]

# -- Options for Texinfo output -----------------------------------------------

texinfo_documents = [
    # (source start file, target, title, author, dir menu entry,
    #  description, category)
    (
        "index",
        "nengo",
        html_title,
        authors,
        "Nengo",
        "Large-scale neural simulation in Python",
        "Miscellaneous",
    ),
]
