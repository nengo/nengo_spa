from nengo_spa import version
from nengo_spa.action_selection import ActionSelection
from nengo_spa.ast.symbolic import sym
from nengo_spa.examine import pairs, similarity, text
from nengo_spa.modules import (
    AssociativeMemory,
    BasalGanglia,
    Bind,
    Compare,
    IAAssocMem,
    Product,
    Scalar,
    State,
    Superposition,
    Thalamus,
    ThresholdingAssocMem,
    Transcode,
    WTAAssocMem,
)
from nengo_spa.network import Network, create_inhibit_node, ifmax
from nengo_spa.operators import dot, reinterpret, translate
from nengo_spa.semantic_pointer import SemanticPointer
from nengo_spa.vector_generation import (
    AxisAlignedVectors,
    EquallySpacedPositiveUnitaryHrrVectors,
    ExpectedUnitLengthVectors,
    OrthonormalVectors,
    UnitaryVectors,
    UnitLengthVectors,
    VectorsWithProperties,
)
from nengo_spa.vocabulary import Vocabulary

__copyright__ = "2013-2021, Applied Brain Research"
__license__ = "Free for non-commercial use; see LICENSE.rst"
__version__ = version.version
