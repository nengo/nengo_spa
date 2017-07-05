import numpy as np
from numpy.testing import assert_allclose
import pytest

import nengo
import nengo_spa as spa
from nengo_spa.exceptions import SpaTypeError
from nengo_spa.examine import similarity
from nengo_spa.network import create_inhibit_node
from nengo_spa.vocab import VocabularyMap


class SpaCommunicationChannel(spa.Network):
    def __init__(
            self, dimensions, label=None, seed=None, add_to_container=None):
        super(SpaCommunicationChannel, self).__init__(
            label, seed, add_to_container)

        with self:
            self.state_in = spa.State(dimensions)
            self.state_out = spa.State(dimensions)
            self.secondary = spa.State(dimensions)

            spa.Actions(('self.state_out = self.state_in',))

        self.input = self.state_in.input
        self.input_secondary = self.secondary.input
        self.output = self.state_out.output
        self.output_secondary = self.secondary.output


def test_spa_verification(seed, plt):
    d = 16

    model = spa.Network(seed=seed)

    # building a normal model that shouldn't raise a warning
    with model:
        model.buf = spa.State(d)
        spa.Actions(('model.buf = B',))
        # make sure errors aren't fired for non-spa networks
        prod = nengo.networks.Product(10, 2)  # noqa: F841
        model.int_val = 1

        # reassignment is fine for non-networks
        model.int_val = 2


def test_spa_vocab():
    # create a model without a vocab and check that it is empty
    model = spa.Network()
    assert len(model.vocabs) == 0

    # create a model with a vocab and check that it's filled
    va = spa.Vocabulary(16)
    va.populate("PANTS")
    vb = spa.Vocabulary(32)
    vb.populate("SHOES")
    model = spa.Network(vocabs=VocabularyMap([va, vb]))
    assert list(model.vocabs[16].keys()) == ["PANTS"]
    assert list(model.vocabs[32].keys()) == ["SHOES"]

    # warning on vocabs with duplicate dimensions
    vc = spa.Vocabulary(16)
    vc.populate("SOCKS")
    with pytest.warns(UserWarning):
        model = spa.Network(vocabs=VocabularyMap([va, vb, vc]))
    assert list(model.vocabs[16].keys()) == ["SOCKS"]
    assert list(model.vocabs[32].keys()) == ["SHOES"]


def test_hierarchical(Simulator, seed, plt):
    d = 32

    with spa.Network(seed=seed) as model:
        model.comm_channel = SpaCommunicationChannel(d)
        model.out = spa.State(d)

        spa.Actions((
            'model.comm_channel = A', 'model.out = model.comm_channel'))

        p = nengo.Probe(model.out.output, synapse=0.03)

    with Simulator(model) as sim:
        sim.run(0.5)

    t = sim.trange() > 0.2
    v = model.vocabs[d].parse('A').v

    plt.plot(sim.trange(), similarity(sim.data[p], v))
    plt.xlabel("t [s]")
    plt.ylabel("Similarity")

    assert np.mean(similarity(sim.data[p][t], v)) > 0.8


def test_hierarchical_actions(Simulator, seed, plt):
    d = 32

    with spa.Network(seed=seed) as model:
        model.comm_channel = SpaCommunicationChannel(d)
        model.out = spa.State(d)

        spa.Actions((
            'model.comm_channel.state_in = A',
            'model.out = model.comm_channel.state_out'
        ))

        p = nengo.Probe(model.out.output, synapse=0.03)

    with Simulator(model) as sim:
        sim.run(0.5)

    t = sim.trange() > 0.2
    v = model.vocabs[d].parse('A').v

    plt.plot(sim.trange(), similarity(sim.data[p], v))
    plt.xlabel("t [s]")
    plt.ylabel("Similarity")

    assert np.mean(similarity(sim.data[p][t], v)) > 0.8


def test_vocab_config():
    with spa.Network() as model:
        with spa.Network() as model.shared_vocabs:
            pass
        with spa.Network(
                vocabs=spa.VocabularyMap()) as model.non_shared_vocabs:
            pass

    assert model.shared_vocabs.vocabs is model.vocabs
    assert model.non_shared_vocabs.vocabs is not model.vocabs


def test_no_magic_vocab_transform():
    d = 16
    v1 = spa.Vocabulary(d)
    v2 = spa.Vocabulary(d)

    with spa.Network() as model:
        model.a = spa.State(vocab=v1)
        model.b = spa.State(vocab=v2)
        with pytest.raises(SpaTypeError):
            spa.Actions(('model.b = model.a',))


@pytest.mark.parametrize('d1,d2,method,lookup', [
    (16, 16, 'reinterpret(a, v2)', 'v1'),
    (16, 16, 'reinterpret(a)', 'v1'),
    (16, 16, 'reinterpret(a, b)', 'v1'),
    (16, 32, 'translate(a, v2)', 'v2'),
    (16, 32, 'translate(a)', 'v2'),
    (16, 32, 'translate(a, b)', 'v2')])
def test_casting_vocabs(d1, d2, method, lookup, Simulator, plt, rng):
    v1 = spa.Vocabulary(d1, rng=rng)
    v1.populate('A')
    v2 = spa.Vocabulary(d2, rng=rng)
    v2.populate('A')

    with spa.Network() as model:
        a = spa.State(vocab=v1)
        b = spa.State(vocab=v2)
        spa.Actions((
            'a = A', 'b = {}'.format(method)))
        p = nengo.Probe(b.output, synapse=0.03)

    with Simulator(model) as sim:
        sim.run(0.5)

    t = sim.trange() > 0.2
    v = locals()[lookup].parse('A').v

    plt.plot(sim.trange(), similarity(sim.data[p], v))
    plt.xlabel("t [s]")
    plt.ylabel("Similarity")

    assert np.mean(similarity(sim.data[p][t], v)) > 0.8


def test_copy_spa(RefSimulator):
    with spa.Network() as original:
        original.state = spa.State(16)
        spa.Actions(('original.state = A',))

    cp = original.copy()

    # Check that it still builds.
    with RefSimulator(cp):
        pass


def test_create_inhibit_node(Simulator, plt):
    with nengo.Network() as model:
        ea = nengo.networks.EnsembleArray(10, 10)
        bias = nengo.Node(1)
        inhibit_node = create_inhibit_node(ea)
        nengo.Connection(bias, inhibit_node)
        nengo.Connection(
            bias, ea.input, transform=np.ones((ea.n_ensembles, 1)))
        p = nengo.Probe(ea.output, synapse=0.01)

    with Simulator(model) as sim:
        sim.run(0.3)

    plt.plot(sim.trange(), sim.data[p])
    plt.xlabel("Time [s]")

    assert_allclose(sim.data[p][sim.trange() > 0.1], 0., atol=1e-3)
