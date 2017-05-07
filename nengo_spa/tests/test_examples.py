import codecs
import os
from pkg_resources import resource_isdir, resource_listdir, resource_stream

import pytest
import _pytest.capture

from nengo.utils.ipython import read_nb
from nengo.utils.stdlib import execfile

# Monkeypatch _pytest.capture.DontReadFromInput
#  If we don't do this, importing IPython will choke as it reads the current
#  sys.stdin to figure out the encoding it will use; pytest installs
#  DontReadFromInput as sys.stdin to capture output.
#  Running with -s option doesn't have this issue, but this monkeypatch
#  doesn't have any side effects, so it's fine.
_pytest.capture.DontReadFromInput.encoding = "utf-8"
_pytest.capture.DontReadFromInput.write = lambda: None
_pytest.capture.DontReadFromInput.flush = lambda: None

too_slow = ['question',
            'question_control',
            'question_memory',
            'spa_parser',
            'spa_sequence',
            'spa_sequence_routed']

all_examples, slow_examples, fast_examples = [], [], []


def resource_walk(package_or_requirement, resource_name):
    queue = [resource_name]
    while len(queue) > 0:
        dirpath = queue.pop()
        dirnames = []
        filenames = []
        for name in resource_listdir(package_or_requirement, dirpath):
            fullpath = os.path.join(dirpath, name)
            if resource_isdir(package_or_requirement, fullpath):
                dirnames.append(name)
                queue.append(fullpath)
            else:
                filenames.append(name)
        yield dirpath, dirnames, filenames


def load_example(example):
    with codecs.getreader('utf-8')(resource_stream(
            'nengo_spa', example + '.ipynb')) as f:
        nb = read_nb(f)
    return nb


for subdir, _, files in resource_walk('nengo_spa', 'examples'):
    if (os.path.sep + '.') in subdir:
        continue
    files = [f for f in files if f.endswith('.ipynb')]
    examples = [os.path.join(subdir, os.path.splitext(f)[0]) for f in files]
    all_examples.extend(examples)
    slow_examples.extend([e for e, f in zip(examples, files)
                          if os.path.splitext(f)[0] in too_slow])
    fast_examples.extend([e for e, f in zip(examples, files)
                          if os.path.splitext(f)[0] not in too_slow])

# os.walk goes in arbitrary order, so sort after the fact to keep pytest happy
all_examples.sort()
slow_examples.sort()
fast_examples.sort()


def assert_noexceptions(nb_file, tmpdir):
    plt = pytest.importorskip('matplotlib.pyplot')
    pytest.importorskip("IPython", minversion="1.0")
    pytest.importorskip("jinja2")
    from nengo.utils.ipython import export_py
    nb = load_example(nb_file)
    pyfile = "%s.py" % tmpdir.join(os.path.basename(nb_file))
    export_py(nb, pyfile)
    execfile(pyfile, {})
    plt.close('all')


@pytest.mark.example
@pytest.mark.parametrize('nb_file', fast_examples)
def test_fast_noexceptions(nb_file, tmpdir):
    """Ensure that no cells raise an exception."""
    assert_noexceptions(nb_file, tmpdir)


@pytest.mark.slow
@pytest.mark.example
@pytest.mark.parametrize('nb_file', slow_examples)
def test_slow_noexceptions(nb_file, tmpdir):
    """Ensure that no cells raise an exception."""
    assert_noexceptions(nb_file, tmpdir)


def iter_cells(nb_file, cell_type="code"):
    nb = load_example(nb_file)

    if nb.nbformat <= 3:
        cells = []
        for ws in nb.worksheets:
            cells.extend(ws.cells)
    else:
        cells = nb.cells

    for cell in cells:
        if cell.cell_type == cell_type:
            yield cell


@pytest.mark.example
@pytest.mark.parametrize('nb_file', all_examples)
def test_no_signature(nb_file):
    nb = load_example(nb_file)
    assert 'signature' not in nb.metadata, "Notebook has signature"


@pytest.mark.example
@pytest.mark.parametrize('nb_file', all_examples)
def test_no_outputs(nb_file):
    """Ensure that no cells have output."""
    pytest.importorskip("IPython", minversion="1.0")

    for cell in iter_cells(nb_file):
        assert cell.outputs == [], "Cell outputs not cleared"


@pytest.mark.example
@pytest.mark.parametrize('nb_file', all_examples)
def test_loads_ipynb_ext(nb_file):
    pytest.importorskip("IPython", minversion="1.0")

    no_sim = True
    for cell in iter_cells(nb_file):
        if "%load_ext nengo.ipynb" in cell.source:
            break
        if "nengo.Simulator(" in cell.source:
            no_sim = False
    else:
        assert no_sim, "nengo.ipynb extension not loaded"